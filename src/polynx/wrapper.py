import polars as pl

def unwrap(obj):
    if hasattr(obj, "_pl"):
        return obj._pl
    return obj

def wrap(obj):
    from .frame import DataFrame
    from .lazyframe import LazyFrame
    from .series import Series
    from .expr import Expr

    if isinstance(obj, pl.DataFrame):
        return DataFrame(obj)
    elif isinstance(obj, pl.LazyFrame):
        return LazyFrame(obj)
    elif isinstance(obj, pl.Series):
        return Series(obj)
    elif isinstance(obj, pl.Expr):
        return Expr(obj)
    return obj
