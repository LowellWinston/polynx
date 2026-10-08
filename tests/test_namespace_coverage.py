import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import polars as pl
import pytest

import polynx as plx
from polynx import core

# plx_* helpers that intentionally have no native-namespace counterpart
_DF_SKIP = {"rolling_prod"}                 # Expr extension
_LF_SKIP = {"rolling_prod", "size"}         # LazyFrame has no estimated_size


def _core_names():
    return {n[4:] for n in dir(core) if n.startswith("plx_")}


@pytest.mark.parametrize("make,skip", [
    (lambda: pl.DataFrame({"a": [1]}).plx, _DF_SKIP),
    (lambda: pl.LazyFrame({"a": [1]}).plx, _LF_SKIP),
])
def test_namespace_exposes_every_core_helper(make, skip):
    ns = make()
    missing = sorted(n for n in _core_names() - skip if not hasattr(ns, n))
    assert not missing, f"missing from the .plx namespace: {missing}"


@pytest.mark.parametrize("frame", [
    lambda d: plx.DataFrame(d),
    lambda d: plx.LazyFrame(d),
    lambda d: plx.LazyFrame(d).query("y > 4"),
    lambda d: pl.DataFrame(d).plx,
    lambda d: pl.LazyFrame(d).plx,
])
def test_pplot_draws_on_all_frame_types(frame):
    plt.close("all")
    frame({"x": [1, 2, 3], "y": [4, 5, 7]}).pplot(kind="line")
    assert plt.get_fignums()
    plt.close("all")
