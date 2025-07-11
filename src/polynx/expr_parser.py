from lark import Lark, Transformer, Tree
import re
import polars as pl
import pandas as pd
import numpy as np
import inspect
from .constant import POLARS_TYPES
from .expr import Expr
from .series import Series
from .wrapper import wrap, unwrap
import hashlib
import logging
from functools import lru_cache
from collections import OrderedDict
from .config import get_cache_mode, get_cache_max_size

logger = logging.getLogger("polynx")

# === Lark grammar
query_grammar = r"""
    ?start: statement (";" statement)* ";"? -> multi_statements
    ?statement: assignment | expr
    assignment: CNAME "=" expr -> assign    

    ?expr: list_expr      
    | expr "|" and_expr -> or_expr
    | and_expr     
   
    ?and_expr: and_expr "&" comp_expr -> and_expr
    | comp_expr

    ?comp_expr: arith_expr (COMP_OP arith_expr)+ -> chained_comparison
    | arith_expr "in" expr -> in_expr
    | arith_expr "not" "in" expr -> not_in_expr  
    | arith_expr -> bare_column_as_filter

    ?arith_expr: arith_expr "+" term -> add
    | arith_expr "-" term -> sub
    | term

    ?term: term "*" factor -> mul
    | term "/" factor -> div
    | term "//" factor -> floordiv
    | term "%" factor -> mod
    | factor

    ?factor: factor "**" base -> power
    | base

    ?base:atom_or_func_call method_call* -> apply_method_chain
    | "-" base -> neg
    | "not" base -> not_
    | "~" base -> bitnot

    ?atom_or_func_call: atom | func_call

    ?atom:  BACKTICKED_STRING   -> backticked  
    | constant
    | boolean
    | variable  -> variable
    | "(" expr ")"        -> grouping      

    boolean: "True" -> true
    | "False" -> false

    constant: ESCAPED_STRING  -> string    
    | CNAME   -> column
    | SIGNED_NUMBER   -> number
    | "pl" "." CNAME  -> pl_type      
   
    BACKTICKED_STRING: "`" ( /[^`\\]/ | /\\./ )* "`"  
   
    ?method_call: "." CNAME "(" [args] ")" -> dynamic_method
    | "." CNAME -> namespace    

    ?func_call: CNAME "(" [args] ")" -> func_call
   
    list_expr: "[" [expr ("," expr)* [","]] "]"    
  
    COMP_OP: "==" | "!=" | "<=" | ">=" | "<" | ">"

    case_flag: "True" -> true
    | "False" -> false

    ESCAPED_STRING: "\"" ( /[^"\\]/ | /\\./ )* "\""
    |"\'" ( /[^"\\]/ | /\\./ )* "\'"
    | "'" ( /[^'\\]/ | /\\./ )* "'"
   
    ?args: arg_or_kwarg ("," arg_or_kwarg)*
   
    ?arg_or_kwarg: kwarg | arg
   
    kwarg: CNAME "=" arg

    ?arg: expr

    ?variable: "@" CNAME
       
    %import common.CNAME
    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS
    %import common.NEWLINE -> _NL
    %ignore _NL
"""

# === Regex for date/datetime detection ===
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
DATETIME_RE = re.compile(r'^\d{4}-\d{2}-\d{2}( \d{2}:\d{2}(:\d{2})?)?$')

def to_pl_date(s):
    if isinstance(s, str):        
        if DATE_RE.match(s):                
            return pl.lit(s).str.strptime(pl.Date, strict=False)
        if DATETIME_RE.match(s):            
            return pl.lit(s).str.strptime(pl.Datetime, strict=False)
    return s


class VarNode:
    def __init__(self, name): self.name = name
    def __repr__(self): return f"VarNode({self.name!r})"


# === Transformer ===
class PolarsExprBuilder(Transformer):
    _registered_udfs = {}

    @classmethod
    def register_udf(cls, name, fn):
        cls._registered_udfs[name] = fn

    def __init__(self, df_schema=None, local_vars=None):
        self.schema = set(df_schema or [])
        self.cols = set()
        self.env = {}        
        self.local_vars = {**PolarsExprBuilder._registered_udfs, **(local_vars or {})}

    def column(self, token):           
        name = str(token[0])
        if name in self.env:
            return self.env[name]
        elif name in self.schema:
            self.cols.add(name)
            return pl.col(name)
        else:
            return name  

    def number(self, token):
        if isinstance(token, (int, float)):
            return token
        else:
            text = str(token[0])
        return int(text) if text.isdigit() else float(text)

    def string(self, val):              
        s = val[0][1:-1]       
        if s in POLARS_TYPES:
            return POLARS_TYPES[s]
        return s          

    def backticked(self, val):
        s = val[0][1:-1]
        if s in self.schema:
            self.cols.add(s)
            return pl.col(s)
        return s

    def true(self, _):
        return True

    def false(self, _):
        return False
    
    def variable(self, items):
        return VarNode(str(items[0]))
    
    def resolve_var(self, value):
        #print("resolve_var called", value)        
        if isinstance(value, VarNode):
            return self.local_vars[value.name]            
        if isinstance(value, list) and len(value) > 0:
            return [self.resolve_var(i) for i in value]
        if isinstance(value, tuple) and len(value) > 0:
            return tuple([self.resolve_var(i) for i in value])
        return value
   
    @staticmethod
    def resolve_dtype(value: str):
        if value.startswith("pl."):
            value = value[3:]
        return POLARS_TYPES[value]
   
    def pl_type(self, items): 
        return PolarsExprBuilder.resolve_dtype("pl." + str(items[0]))
       
    def kwarg(self, args):
        args = self.resolve_var(args)        
        return (args[0], args[1])

    def neg(self, val):
        val = self.resolve_var(val)
        return -val[0]

    def bitnot(self, val):
        val = self.resolve_var(val)
        return ~val[0]

    def not_(self, val):
        val = self.resolve_var(val)
        return ~val[0]

    def add(self, args):
        args = self.resolve_var(args)
        return args[0] + args[1]

    def sub(self, args):
        args = self.resolve_var(args)
        return args[0] - args[1]

    def mul(self, args):
        args = self.resolve_var(args)
        return args[0] * args[1]

    def div(self, args):
        args = self.resolve_var(args)
        return args[0] / args[1]

    def floordiv(self, args):
        args = self.resolve_var(args)
        return args[0] // args[1]

    def mod(self, args):
        args = self.resolve_var(args)
        return args[0] % args[1]

    def power(self, args):
        args = self.resolve_var(args)
        return args[0] ** args[1]

    def and_expr(self, args):
        args = self.resolve_var(args)
        return args[0] & args[1]

    def or_expr(self, args):
        args = self.resolve_var(args)
        return args[0] | args[1]

    def chained_comparison(self, items):      
        result = None
        items = self.resolve_var(items)
        left = to_pl_date(items[0])
        for i in range(1, len(items)-1, 2):
            op = items[i].value
            right = to_pl_date(items[i+1])
            comp = {
                "==": left == right,
                "!=": left != right,
                "<": left < right,
                "<=": left <= right,
                ">": left > right,
                ">=": left >= right,
                }[op]
            result = comp if result is None else result & comp
            left = right
        return result
   
    def list_expr(self, args):        
        return self.resolve_var(args) 

    def in_expr(self, args):
        args = self.resolve_var(args)
        if isinstance(args[1][0], str) and DATE_RE.match(args[1][0]):                    
            args[0] = args[0].dt.date().cast(pl.Utf8)
        return args[0].is_in(args[1])
       
    def not_in_expr(self, args):
        args = self.resolve_var(args)
        if isinstance(args[1][0], str) and DATE_RE.match(args[1][0]):            
            args[0] = args[0].dt.date().cast(pl.Utf8)
        return ~args[0].is_in(args[1])
       
    def not_(self, args):
        args = self.resolve_var(args)
        return (~args[0]).fill_null(True)
   
    def grouping(self, args):
        return self.resolve_var(args[0])

    def bare_column_as_filter(self, args):
        val = self.resolve_var(args[0])
        if isinstance(val, str) and val in self.schema:
            return pl.col(val)
        return val

    # Multi-stmt assignment
    def assign(self, args):
        target_col = str(args[0])
        expr = self.resolve_var(args[1])
        self.env[target_col] = expr
        if isinstance(expr, (Series, pl.Series)):
            return expr.rename(target_col)
        if isinstance(expr, (list, tuple, np.ndarray, pd.Series)):
            return pl.Series(target_col, expr)
        if isinstance(expr, (int, float, str, bool)):
            return pl.lit(expr).alias(target_col)
        return expr.alias(target_col)
   
    def multi_statements(self, args):
        return args # Just return the list of expressions or assignments
   
    # def register(self, name: str, func: callable):
    #     self.user_func[name] = func

    # def get_user_func(self, name: str):
    #     return self.user_funcs.get(name)

    def apply_method_chain(self, children):
        base = children[0]
        if len(children) == 1:            
            if isinstance(base, str):
                return self.column(children)          
            if isinstance(base, (int, float)):
                return base

        for fn in children[1:]:            
            if callable(fn):
                base = fn(base)
            else:
                raise TypeError(f"Expected callable, got {type(fn)}: {fn}")
        return base      

    def get_args(self, node, args, kwargs):
        args = self.resolve_var(args)       
        if isinstance(node, tuple):            
            kwargs.update({node[0].value: self.resolve_var(node[1])})
        elif isinstance(node, Tree):
            for child in node.children:
                args = self.get_args(child, args, kwargs)                
        else:
            args.append(node)
        
        return args

    @staticmethod
    def extract_col_name(expr):
        match = re.match(r'col\("([^"]+)"\)', str(expr))
        if match:
            return match.group(1)
        raise ValueError(f"Not a column expression: {expr}")

    @staticmethod
    def extract_column_names_from_tree(tree):            
        return [PolarsExprBuilder.extract_col_name(child) for child in tree.children]  
   
    @staticmethod
    def extract_column_names_from_list(lst):            
        return [PolarsExprBuilder.extract_col_name(child) for child in lst]

    def dynamic_method(self, args):        
        method_name = str(args[0])
        raw_args = self.resolve_var(args[1:])
        func_args = [a for a in raw_args if a is not None]        

        def _method_call(arg, method):
            if isinstance(arg, (Expr, pl.Expr)):
                return method(PolarsExprBuilder.extract_col_name(arg))
            elif isinstance(arg, (tuple, list)):
                return method(PolarsExprBuilder.extract_column_names_from_list(arg))
            else:
                return method(PolarsExprBuilder.extract_column_names_from_tree(arg))            

        def wrapper(expr):            
            expr = wrap(expr)                               
            method = getattr(expr, method_name)            
                        
            if not func_args:
                result = method()
            else:
                arg = func_args[0]
                if method_name == "over":                                                            
                    result = _method_call(arg, method)              
               
                elif method_name == "alias":                  
                    if isinstance(arg, str):
                        result = method(arg)
                    else:
                        result = _method_call(arg, method)

                elif method_name in ['is_in', 'is_not_in']:
                    if isinstance(arg, (list, tuple)) and isinstance(arg[0], str) and DATE_RE.match(arg[0]):                                  
                        method = getattr(expr.dt.date().cast(pl.Utf8), method_name)                   
                    result = method(arg)
                    
                else:
                    _args, _kwargs = [], {}                      
                    _args = self.get_args(func_args[0], _args, _kwargs)                                                           
                    result = method(*_args, **_kwargs)
            return unwrap(result) 
        return wrapper

    def namespace(self, args):              
        name = str(args[0])        
        return lambda expr: getattr(expr, name)
    
    # Namespace function is not supported to avoid confusion with method call
    def fn_name(self, args):
        return str(args[0])

    def func_call(self, args):        
        try:
            func = eval(str(args[0]))
        except:
            func = self.local_vars[str(args[0])]
        
        raw_args = self.resolve_var(args[1:])        
        func_args = [a for a in raw_args if a is not None]  
           
        if not func_args:
            return func()          

        _args, _kwargs = [], {}
        _args = self.get_args(func_args[0], _args, _kwargs)
        return func(*_args, **_kwargs)    
        

def dynamic_all_scopes(max_frames=10):
    """ Retrieves variables and functions from the correct execution scope. """
    try:
        frame = inspect.currentframe().f_back
        scope_vars = {}
        for _ in range(max_frames):
            if frame is None:
                break
            scope_vars.update(frame.f_globals)
            scope_vars.update(frame.f_locals)
            frame = frame.f_back
        return scope_vars
    except AttributeError:
        return {}

PL_PARSER = Lark(query_grammar, parser="lalr")

def parse_pl_expr(query_str: str, df_schema, local_vars=None, return_cols=False):    
    if local_vars is None:
        local_vars = dynamic_all_scopes()    
    expr = query_str.strip()    
    transformer = PolarsExprBuilder(df_schema=df_schema, local_vars=local_vars)
    tree = PL_PARSER.parse(expr)    
    parsed_tree = transformer.transform(tree)
    if return_cols:
        return parsed_tree, transformer.cols
    else:
        return parsed_tree

def register_udf(name: str, fn: callable):    
    PolarsExprBuilder.register_udf(name, fn)

def register_udfs_from_module(module):
    for name, fn in inspect.getmembers(module, inspect.isfunction):
        register_udf(name, fn)

def register_udfs_by_names(module, names: list[str]):
    """ Register udf by name for a given module"""
    for name in names:
        fn = getattr(module, name)
        register_udf(name, fn)


# Global Cache Containers
_raw_cache = {}
_hash_cache = {}
cache_stats = {"hit": 0, "miss": 0}

_warned = {
    "raw": False,
    "hash": False,
    "custom_lru": False    
}

# Custom LRU Cache
class ExprCacheLRU:
    def __init__(self, max_size=1000):
        self.max_size = max_size
        self.store = OrderedDict()

    def get(self, expr_str):
        key = self._hash(expr_str)
        if key in self.store:
            self.store.move_to_end(key)
            return self.store[key]
        return None

    def set(self, expr_str, parsed):
        key = self._hash(expr_str)
        self.store[key] = parsed
        self.store.move_to_end(key)
        if len(self.store) == self.max_size and not _warned["custom_lru"]:
            logger.warning("⚠️ Expression cache (custom_lru) reached max size: %d", self.max_size)
            _warned["custom_lru"] = True
        if len(self.store) > self.max_size:
            self.store.popitem(last=False)

    def clear(self):
        self.store.clear()

    @staticmethod
    def _hash(expr_str):
        return hashlib.sha1(expr_str.encode("utf-8")).hexdigest()

_custom_lru_cache = ExprCacheLRU(max_size=get_cache_max_size())

## Caching Backends
def _parse_with_raw_dict(query_str: str, *args, **kwargs):
    if query_str in _raw_cache:
        cache_stats["hit"] += 1
        return _raw_cache[query_str]
    cache_stats["miss"] += 1
    if not _warned["raw"] and len(_raw_cache) >= get_cache_max_size():
        logger.warning("⚠️ Expression cache (raw) reached max size.")
        _warned["raw"] = True
    parsed = parse_pl_expr(query_str, *args, **kwargs)
    _raw_cache[query_str] = parsed
    return parsed

def _parse_with_hashed_dict(query_str: str, *args, **kwargs):
    key = hashlib.sha1(query_str.encode("utf-8")).hexdigest()
    if key in _hash_cache:
        cache_stats["hit"] += 1
        return _hash_cache[key]
    cache_stats["miss"] += 1
    if not _warned["hash"] and len(_hash_cache) >= get_cache_max_size():
        logger.warning("⚠️ Expression cache (hash) reached max size.")
        _warned["hash"] = True
    parsed = parse_pl_expr(query_str, *args, **kwargs)
    _hash_cache[key] = parsed
    return parsed

def _parse_with_custom_lru(query_str: str, *args, **kwargs):
    cached = _custom_lru_cache.get(query_str)
    if cached is not None:
        cache_stats["hit"] += 1
        return cached
    cache_stats["miss"] += 1
    parsed = parse_pl_expr(query_str, *args, **kwargs)
    _custom_lru_cache.set(query_str, parsed)
    return parsed

# Public Interface
def parse_polars_expr(query_str: str, df_schema, local_vars=None, return_cols=False):
    mode = get_cache_mode()
    if mode == "raw":
        return _parse_with_raw_dict(query_str, df_schema, local_vars, return_cols)
    elif mode == "hash":
        return _parse_with_hashed_dict(query_str, df_schema, local_vars, return_cols)
    elif mode == "custom_lru":
        return _parse_with_custom_lru(query_str, df_schema, local_vars, return_cols)
    else:
        raise ValueError(f"Unsupported CACHE_MODE: {mode}")


# Cache Utility Functions
def clear_all_expr_caches():
    _raw_cache.clear()
    _hash_cache.clear()
    _custom_lru_cache.clear()
    if hasattr(_parse_with_lru, "cache_clear"):
        _parse_with_lru.cache_clear()
    cache_stats["hit"] = 0
    cache_stats["miss"] = 0
    for k in _warned:
        _warned[k] = False

def get_expr_cache():
    mode = get_cache_mode()
    if mode == "raw":
        return dict(_raw_cache)
    elif mode == "hash":
        return dict(_hash_cache)
    elif mode == "custom_lru":
        return dict(_custom_lru_cache.store)    
    else:
        return {"error": f"Unknown cache mode {mode}"}

def get_expr_cache_size():
    mode = get_cache_mode()
    if mode == "raw":
        return len(_raw_cache)
    elif mode == "hash":
        return len(_hash_cache)
    elif mode == "custom_lru":
        return len(_custom_lru_cache.store)    
    else:
        return -1

def get_expr_cache_stats():
    return dict(cache_stats)

def reset_expr_cache_stats():
    cache_stats["hit"] = 0
    cache_stats["miss"] = 0