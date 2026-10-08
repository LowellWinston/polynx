import polars as pl
from . import core
from .frame import DataFrame
from .lazyframe import LazyFrame
from .wrapper import unwrap


@pl.api.register_dataframe_namespace("plx")
class PolynxDataFrameNamespace:
    """Polynx namespace extension for native polars.DataFrame."""

    def __init__(self, df: pl.DataFrame):
        self._df = df

    def query(self, query_str: str) -> pl.DataFrame:
        return unwrap(core.plx_query(self._df, query_str))

    def eval(self, query_str, mode: str = "select"):
        return unwrap(core.plx_eval(self._df, query_str, mode=mode))

    def assign(self, query_str):
        return unwrap(core.plx_assign(self._df, query_str))

    def wc(self, *args, **kwargs):
        return unwrap(core.plx_wc(self._df, *args, **kwargs))

    def gb(self, gp_keys, expr: str, with_subtotal: bool = False):
        return unwrap(core.plx_gb(self._df, gp_keys, expr, with_subtotal=with_subtotal))

    def vcnt(self, col=None):
        return unwrap(core.plx_vcnt(self._df, col=col))

    def ucnt(self, col=None):
        return core.plx_ucnt(self._df, col=col)

    def dd(self):
        return unwrap(core.plx_dd(self._df))

    def dsort(self, by=None):
        return unwrap(core.plx_dsort(self._df, by=by))

    def asort(self, by=None):
        return unwrap(core.plx_asort(self._df, by=by))

    def unstack(self):
        return unwrap(core.plx_unstack(self._df))

    def describe(self, percentiles=(0.25, 0.5, 0.75), interpolation="nearest", group_keys=None, selected_columns=None):
        return unwrap(core.plx_describe(self._df, percentiles=percentiles, interpolation=interpolation, group_keys=group_keys, selected_columns=selected_columns))

    def round(self, decimal: int = 2):
        return unwrap(core.plx_round(self._df, decimal=decimal))

    def cum_max(self):
        return unwrap(core.plx_cum_max(self._df))

    def to_list(self, col_name=None):
        return core.plx_to_list(self._df, col_name=col_name)

    def max(self, col_name=None):
        return core.plx_max(self._df, col_name=col_name)

    def min(self, col_name=None):
        return core.plx_min(self._df, col_name=col_name)

    def size(self, unit: str = "mb", return_size: bool = False):
        return core.plx_size(self._df, unit=unit, return_size=return_size)

    def rename(self, *args, **kwargs):
        return unwrap(core.plx_rename(self._df, *args, **kwargs))

    def pplot(self, *args, **kwargs):
        return core.plx_pplot(self._df, *args, **kwargs)

    def to_polynx(self) -> DataFrame:
        return DataFrame(self._df)


@pl.api.register_lazyframe_namespace("plx")
class PolynxLazyFrameNamespace:
    """Polynx namespace extension for native polars.LazyFrame."""

    def __init__(self, lf: pl.LazyFrame):
        self._lf = lf

    def query(self, query_str: str) -> pl.LazyFrame:
        return unwrap(core.plx_query(self._lf, query_str))

    def eval(self, query_str, mode: str = "select"):
        return unwrap(core.plx_eval(self._lf, query_str, mode=mode))

    def assign(self, query_str):
        return unwrap(core.plx_assign(self._lf, query_str))

    def wc(self, *args, **kwargs):
        return unwrap(core.plx_wc(self._lf, *args, **kwargs))

    def gb(self, gp_keys, expr: str, with_subtotal: bool = False):
        return unwrap(core.plx_gb(self._lf, gp_keys, expr, with_subtotal=with_subtotal))

    def vcnt(self, col=None):
        return unwrap(core.plx_vcnt(self._lf, col=col))

    def ucnt(self, col=None):
        return core.plx_ucnt(self._lf, col=col)

    def dd(self):
        return unwrap(core.plx_dd(self._lf))

    def dsort(self, by=None):
        return unwrap(core.plx_dsort(self._lf, by=by))

    def asort(self, by=None):
        return unwrap(core.plx_asort(self._lf, by=by))

    def unstack(self):
        return unwrap(core.plx_unstack(self._lf))

    def describe(self, percentiles=(0.25, 0.5, 0.75), interpolation="nearest", group_keys=None, selected_columns=None):
        return unwrap(core.plx_describe(self._lf, percentiles=percentiles, interpolation=interpolation, group_keys=group_keys, selected_columns=selected_columns))

    def round(self, decimal: int = 2):
        return unwrap(core.plx_round(self._lf, decimal=decimal))

    def cum_max(self):
        return unwrap(core.plx_cum_max(self._lf))

    def to_list(self, col_name=None):
        return core.plx_to_list(self._lf, col_name=col_name)

    def max(self, col_name=None):
        return core.plx_max(self._lf, col_name=col_name)

    def min(self, col_name=None):
        return core.plx_min(self._lf, col_name=col_name)

    def rename(self, *args, **kwargs):
        return unwrap(core.plx_rename(self._lf, *args, **kwargs))

    def pplot(self, *args, **kwargs):
        return core.plx_pplot(self._lf, *args, **kwargs)

    def to_polynx(self) -> LazyFrame:
        return LazyFrame(self._lf)
