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
    from .groupby import GroupBy  

    if getattr(obj, "_is_wrapped", False):
        return obj 
    
    if isinstance(obj, pl.DataFrame):
        return DataFrame(obj)
    elif isinstance(obj, pl.LazyFrame):
        #print(obj)
        new_obj = LazyFrame()
        new_obj._pl = obj
        return new_obj
    elif isinstance(obj, pl.Series):
        new_obj = Series()
        new_obj._pl = obj
        return new_obj
    elif isinstance(obj, pl.Expr):
        new_obj = Expr()
        new_obj._pl = obj
        return new_obj
    elif isinstance(obj, (pl.dataframe.group_by.GroupBy, pl.lazyframe.group_by.LazyGroupBy)):
        return GroupBy(obj)
    return obj
