from .frame import DataFrame
from .lazyframe import LazyFrame
from .series import Series
from .expr import Expr

def get_schema(df):
    if isinstance(df, DataFrame):
        return df.schema
    if isinstance(df, LazyFrame):
        return df.collect_schema()


# Alias for get_schema
def schema(df):
    return get_schema(df)


def get_columns(df):
    if isinstance(df, DataFrame):
        return df.columns
    elif isinstance(df, LazyFrame):
        return list(get_schema(df).keys())
    else:
        raise TypeError("Unsupported type. Must be DataFrame or LazyFrame.")


# Alias for get_columns
def columns(df):
    if isinstance(df, DataFrame):
        return df.columns
    if isinstance(df, LazyFrame):
        return get_columns(df)


def to_plx_expr(self, arg):
    if isinstance(arg, str):
        parsed_expr = parse_polars_expr(arg, get_schema(self))
        if len(parsed_expr) == 1:
            return parsed_expr[0]
        return parsed_expr
    else:
        return arg


def plx_frame_patch(plx_func_name, func):
    setattr(DataFrame, plx_func_name, func)
    setattr(LazyFrame, plx_func_name, func)


def plx_expr_patch(plx_func_name, func):
    setattr(Expr, plx_func_name, func)


def plx_series_patch(plx_func_name, func):
    setattr(Series, plx_func_name, func)