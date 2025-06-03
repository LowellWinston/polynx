__version__ = "0.1.4"
from . import core as _core
from .utils import plx_frame_patch, plx_expr_patch, DataFrame, LazyFrame, Series, Expr, plx_merge as merge
from . import io as _io

__all__ = ["DataFrame", "LazyFrame", "Series", "Expr"]

for name in ['rolling_prod']:
    plx_expr_patch(name, getattr(_core, f"plx_{name}"))


for name in [
    'eval','assign','dd', "dsort", "asort", "unstack", 
    "pplot", "vcnt", "ucnt", "query", "eval", "wc", "gb", 
    "describe", "round", "cum_max", "to_list", "max", "min",
    "rename", "size"
]:
    plx_frame_patch(name, getattr(_core, f"plx_{name}"))


for name in _io._wrapped_functions:
    globals()[name] = getattr(_io, name)