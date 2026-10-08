import polars as pl
import pytest

import polynx as plx
from polynx import config, expr_parser as ep

SCHEMA = {"A": 1, "B": 2, "A1": 3, "Score Value": 4, "D": 5}

CASES = [
    "A > 5", "A>-5", "A - 5", "A -5", "A*2.5+1e3 < .5", "1 <= A < 4", "B in ['x','y']",
    "B == \"it's\"", "B.str.slice(0, 2)", "A1 + 2", "`Score Value` > 90", "D >= '2024-01-05'",
    "D in ['2024-01-05','2024-02-01']", "B.cast(pl.Int64)", "B.cast('Int64')",
    "A = 3; B = A + 4", "A > +5", "A**-2", "-A + 3", "B == 'a\\'b'", "A.mean().over('B')",
]


def _ser(r):
    items = r if isinstance(r, list) else [r]
    return [i.meta.serialize(format="json") if isinstance(i, pl.Expr) else repr(i)
            for i in (plx.wrapper.unwrap(x) for x in items)]


@pytest.fixture(autouse=True)
def _restore_cache_mode():
    old = config.get_cache_mode()
    yield
    config.set_cache_mode(old)
    ep.clear_all_expr_caches()


@pytest.mark.parametrize("q", CASES)
def test_templated_parse_matches_plain_parse(q):
    config.set_cache_mode("none")
    expected = _ser(ep.parse_pl_expr(q, SCHEMA, {}))
    config.set_cache_mode("raw")
    ep.clear_all_expr_caches()
    assert _ser(ep.parse_pl_expr(q, SCHEMA, {})) == expected


def test_template_reused_with_new_literals():
    config.set_cache_mode("raw")
    ep.clear_all_expr_caches()
    df = plx.DataFrame({"A": list(range(10)), "B": ["x", "y"] * 5})
    for t in range(10):
        assert df.query(f"A > {t} & B in ['x', 'y']").shape[0] == 9 - t
    assert len(ep._tpl_cache) == 1


def test_at_variable_not_stale_in_loop():
    df = plx.DataFrame({"A": list(range(10))})
    for t in (2, 5, 7):
        assert df.query("A > @t").shape[0] == 9 - t


def test_func_call_does_not_eval_expression_text():
    # builtins/dunder names must not be reachable from an expression string
    for q in ("__import__('math')", "open('x')", "eval('1')", "exec('1')"):
        with pytest.raises(Exception):
            ep.parse_pl_expr(q, SCHEMA, {})


def test_func_call_allows_safe_builtins_udfs_and_scope():
    assert ep.parse_pl_expr("abs(-3)", SCHEMA, {}) == [3.0]
    assert ep.parse_pl_expr("double(4)", SCHEMA, {"double": lambda x: x * 2}) == [8]
