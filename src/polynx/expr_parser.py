from lark import Lark, Transformer, Tree
import re
import polars as pl
import inspect
from .constant import POLARS_TYPES

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
    | arith_expr "in" list_expr -> in_expr
    | arith_expr "not" "in" list_expr -> not_in_expr  
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
   
# === Transformer ===
class PolarsExprBuilder(Transformer):
    def __init__(self, df_schema=None, local_vars=None):
        self.schema = set(df_schema or [])
        self.cols = set()
        self.env = {}
        self.local_vars = local_vars or {}

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
   
    @staticmethod
    def resolve_dtype(value: str):
        if value.startswith("pl."):
            value = value[3:]
        return POLARS_TYPES[value]
   
    def pl_type(self, items): 
        return PolarsExprBuilder.resolve_dtype("pl." + str(items[0]))
       
    def kwarg(self, args):
        return (args[0], args[1])

    def neg(self, val):
        return -val[0]

    def bitnot(self, val):
        return ~val[0]

    def not_(self, val):
        return ~val[0]

    def add(self, args):
        return args[0] + args[1]

    def sub(self, args):
        return args[0] - args[1]

    def mul(self, args):
        return args[0] * args[1]

    def div(self, args):
        return args[0] / args[1]

    def floordiv(self, args):
        return args[0] // args[1]

    def mod(self, args):
        return args[0] % args[1]

    def power(self, args):
        return args[0] ** args[1]

    def and_expr(self, args):
        return args[0] & args[1]

    def or_expr(self, args):
        return args[0] | args[1]

    def chained_comparison(self, items):      
        result = None
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
        return args

    def in_expr(self, args):
        if isinstance(args[1][0], str) and DATE_RE.match(args[1][0]):                    
            args[0] = args[0].dt.date().cast(pl.Utf8)
        return args[0].is_in(args[1])
       
    def not_in_expr(self, args):
        if isinstance(args[1][0], str) and DATE_RE.match(args[1][0]):            
            args[0] = args[0].dt.date().cast(pl.Utf8)
        return ~args[0].is_in(args[1])
       
    def not_(self, args):
        return (~args[0]).fill_null(True)
   
    def grouping(self, args):
        return args[0]

    def bare_column_as_filter(self, args):
        val = args[0]
        if isinstance(val, str) and val in self.schema:
            return pl.col(val)
        return val

    # Multi-stmt assignment
    def assign(self, args):
        target_col = str(args[0])
        expr = args[1]
        self.env[target_col] = expr
        if isinstance(expr, list):
            return pl.Series(target_col, expr)
        if isinstance(expr, (int, float, str, bool)):
            return pl.lit(expr).alias(target_col)
        return expr.alias(target_col)
   
    def multi_statements(self, args):
        return args # Just return the list of expressions or assignments
   
    def register(self, name: str, func: callable):
        self.user_func[name] = func

    def get_user_func(self, name: str):
        return self.user_funcs.get(name)

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

    @staticmethod
    def get_args(node, args, kwargs):
        if isinstance(node, tuple):
            kwargs.update({node[0].value: node[1]})
        elif isinstance(node, Tree):
            for child in node.children:
                PolarsExprBuilder.get_args(child, args, kwargs)
        else:
            args.append(node)

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
        raw_args = args[1:]
        func_args = [a for a in raw_args if a is not None]        

        def _method_call(arg, method):
            if isinstance(arg, pl.Expr):
                return method(PolarsExprBuilder.extract_col_name(arg))
            elif isinstance(arg, list):
                return method(PolarsExprBuilder.extract_column_names_from_list(arg))
            else:
                return method(PolarsExprBuilder.extract_column_names_from_tree(arg))            

        def wrapper(expr):
            method = getattr(expr, method_name)
            if not func_args:
                return method()  

            arg = func_args[0]
            if method_name == "over":                                                            
                return _method_call(arg, method)              
               
            if method_name == "alias":                  
                if isinstance(arg, str):
                    return method(arg)
                return _method_call(arg, method)

            if method_name in ['is_in', 'is_not_in']:
                if isinstance(arg, list) and isinstance(arg[0], str) and DATE_RE.match(arg[0]):                                  
                    method = getattr(expr.dt.date().cast(pl.Utf8), method_name)
                return method(arg)

            _args, _kwargs = [], {}                      
            PolarsExprBuilder.get_args(func_args[0], _args, _kwargs)            
            return method(*_args, **_kwargs)          
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
        raw_args = args[1:]
        func_args = [a for a in raw_args if a is not None]
           
        if not func_args:
            return func()          

        _args, _kwargs = [], {}
        PolarsExprBuilder.get_args(func_args[0], _args, _kwargs)
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


def substitute_var(expr: str, scope_vars):
    """ Replaces @var with its actual value from the execution scope. """
    def replace_var(match):
        var_name = match.group(1)
        if var_name not in scope_vars:
            raise NameError(f"Variable '@{var_name}' is not defined.")
        value = scope_vars[var_name]
        if isinstance(value, str):
            return f"'{value}'"
        else:
            return str(value)
    return re.sub(r'@(\w+)', replace_var, expr)


PL_PARSER = Lark(query_grammar, parser="lalr")


def parse_polars_expr(query_str: str, df_schema=None, local_vars=None, return_cols=False):    
    if local_vars is None:
        local_vars = dynamic_all_scopes()    
    expr = query_str.strip()
    expr = substitute_var(expr, local_vars)    
    transformer = PolarsExprBuilder(df_schema=df_schema or [], local_vars=local_vars)
    tree = PL_PARSER.parse(expr)    
    parsed_tree = transformer.transform(tree)
    if return_cols:
        return parsed_tree, transformer.cols
    else:
        return parsed_tree