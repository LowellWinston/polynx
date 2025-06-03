from .frame import DataFrame
from .lazyframe import LazyFrame
from .series import Series
from .expr import Expr
from .expr_parser import parse_polars_expr
from .constant import PL_DATETIME_DTYPE, PL_NUMERIC_DTYPES, PL_FLT_DTYPES
import polars as pl


def plx_frame_patch(plx_func_name, func):
    setattr(LazyFrame, plx_func_name, func)
    setattr(DataFrame, plx_func_name, func)    


def plx_expr_patch(plx_func_name, func):
    setattr(Expr, plx_func_name, func)


def plx_series_patch(plx_func_name, func):
    setattr(Series, plx_func_name, func)


def get_schema(self):
    if isinstance(self, (pl.DataFrame, DataFrame)):
        return self.schema
    if isinstance(self, (pl.LazyFrame, LazyFrame)):
        return self.collect_schema()


# Alias for get_schema
def schema(self):    
    return get_schema(self)


def get_columns(self):
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


def is_datetime_dtype(dtype):
    return dtype in PL_DATETIME_DTYPE


def is_numeric_dtype(dtype):
    return dtype in PL_NUMERIC_DTYPES


def is_flt_dtype(dtype):
    return dtype in PL_FLT_DTYPES

def plx_merge(left, right, on=None, how="inner", suffixes=("_x", "_y")):
    """
    pandas style merge

    Parameters:
    left (pl.DataFrame): Left DataFrame
    right (pl.DataFrame): Right DataFrame
    on (str or list): Column(s) to join on
    how (str): Type of join - "inner", "left", "right", "outer"
    suffixes (tuple): Suffixes for overlapping column names

    Returns:
    pl.DataFrame or pl.LazyFrame: Merged DataFrame
    """

    # Ensure `on` is a list
    if isinstance(on, str):
        on = [on]
   
    # Get common columns (excluding join keys)
    common_cols = set(get_columns(left)) & set(get_columns(right)) - set(on)

    # Rename overlapping columns in `right` DataFrame
    left_renamed = left.rename({col: col + suffixes[0] for col in common_cols})

    # Rename overlapping columns in `right` DataFrame
    right_renamed = right.rename({col: col + suffixes[1] for col in common_cols})

    # Perform join
    df_merged = left_renamed.join(right_renamed, on=on, how=how)

    return df_merged


def select(conds, choices, default):              
    """ multiple condition statements, mirroring np.select """
    def as_expr(x):
        return x if isinstance(x, pl.Expr) else pl.lit(x)

    if len(conds) != len(choices):
        raise ValueError("Number of conditions and choices must match")

    expr = pl.when(conds[0]).then(as_expr(choices[0]))
    for cond, choice in zip(conds[1:], choices[1:]):
        expr = expr.when(cond).then(as_expr(choice))
    return expr.otherwise(as_expr(default))


def where(cond, choice, default):
    """ single condition statment, mirroring np.where """
    return select([cond], [choice], default)


def mondf(beg_date, end_date):
    return (end_date.dt.year() - beg_date.dt.year())*100 + end_date.dt.month() - beg_date.dt.month()