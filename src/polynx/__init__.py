__version__ = "0.1.11"
from . import core
from .utils import plx_frame_patch, plx_expr_patch, DataFrame, LazyFrame, Series, Expr, plx_merge as merge
from . import io 
from .expr_parser import register_udfs_by_names, register_udf, parse_polars_expr
from . import utils 

__all__ = ["DataFrame", "LazyFrame", "Series", "Expr"]

for name in ['rolling_prod']:
    plx_expr_patch(name, getattr(core, f"plx_{name}"))

for name in [
    'eval','assign','dd', "dsort", "asort", "unstack", 
    "pplot", "vcnt", "ucnt", "query", "eval", "wc", "gb", 
    "describe", "round", "cum_max", "to_list", "max", "min",
    "rename", "size", "to_pandas"
]:
    plx_frame_patch(name, getattr(core, f"plx_{name}"))

for name in io._wrapped_functions:
    globals()[name] = getattr(io, name)

register_udfs_by_names(utils, ['select', 'where', 'mondf'])    

