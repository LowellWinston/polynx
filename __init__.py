from .utils import plx_frame_patch, plx_expr_patch, plx_series_patch
from .core import *

__all__ = ["DataFrame", "LazyFrame", "Series", "Expr"]

plx_frame_patch('eval', plx_eval)
plx_frame_patch('assign', plx_assign)
plx_frame_patch('dd', plx_dd)
plx_frame_patch('dsort', plx_dsort)
plx_frame_patch('asort', plx_asort)
plx_frame_patch('unstack', plx_unstack)    
plx_frame_patch('pplot', plx_plot)
plx_frame_patch('vcnt', plx_vcnt)
plx_frame_patch('ucnt', plx_ucnt)
plx_frame_patch('query', plx_query)
plx_frame_patch('eval', plx_eval)
plx_frame_patch('wc', plx_wc)
plx_frame_patch('gb', plx_agg)
plx_frame_patch('describe', plx_describe)
plx_frame_patch('round', plx_round)
plx_frame_patch('cum_max', plx_cum_max)
plx_frame_patch('to_list', plx_to_list)
plx_frame_patch('max', plx_max)
plx_frame_patch('min', plx_min)
plx_series_patch('describe', plx_describe)
plx_expr_patch('rolling_prod', plx_rolling_prod)

def from_pandas(obj):
    if isinstance(obj, pd.DataFrame):
        return DataFrame(pl.from_pandas(obj))
    else:
        raise TypeError("Expected a pandas.DataFrame")