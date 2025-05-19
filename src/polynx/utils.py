from .frame import DataFrame, pl
from .lazyframe import LazyFrame
from .series import Series
from .expr import Expr
from .expr_parser import parse_polars_expr
from .constant import PL_DATETIME_DTYPE, PL_NUMERIC_DTYPES, PL_FLT_DTYPES



def plx_frame_patch(plx_func_name, func):
    setattr(DataFrame, plx_func_name, func)
    setattr(LazyFrame, plx_func_name, func)


def plx_expr_patch(plx_func_name, func):
    setattr(Expr, plx_func_name, func)


def plx_series_patch(plx_func_name, func):
    setattr(Series, plx_func_name, func)


def get_schema(self):
    #df = self.to_polars()       
    #print(type(self))
    if isinstance(self, (pl.DataFrame, DataFrame)):
        #print(self.schema)
        return self.schema
    if isinstance(self, (pl.LazyFrame, LazyFrame)):
        return self.collect_schema()


# Alias for get_schema
def schema(self):    
    return get_schema(self)


def get_columns(self):
    #df = self.to_polars()
    if isinstance(self, (pl.DataFrame, DataFrame)):
        return self.columns
    elif isinstance(self, (pl.LazyFrame, LazyFrame)):
        return list(get_schema(self).keys())
    else:
        raise TypeError("Unsupported type. Must be DataFrame or LazyFrame.")


# Alias for get_columns
def columns(self):
    return get_columns(self)


def to_plx_expr(self, arg):
    if isinstance(arg, str):
        parsed_expr = parse_polars_expr(arg, get_schema(self))
        if len(parsed_expr) == 1:
            return parsed_expr[0]
        return parsed_expr
    else:
        return arg


def plx_rolling_prod(expr, *args, **kwargs):
    return expr.log().rolling_sum(*args, **kwargs).exp()


def is_datetime_dtype(dtype):
    return dtype in PL_DATETIME_DTYPE


def is_numeric_dtype(dtype):
    return dtype in PL_NUMERIC_DTYPES


def is_flt_dtype(dtype):
    return dtype in PL_FLT_DTYPES