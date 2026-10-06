import pytest
import polars as pl
import numpy as np
import polynx as plx
from polynx import DataFrame, LazyFrame, Series, Expr
from polynx.config import set_cache_mode, get_cache_mode, set_cache_max_size, get_cache_max_size
from polynx.expr_parser import get_expr_cache, clear_all_expr_caches, register_udf

@pytest.fixture
def sample_df():
    return plx.DataFrame({
        'A': [1, 2, 3, 4],
        'B': ['abc', 'bc', 'aaa', None],
        'C': ['2023-01-01', '2021-01-01', '2009-11-01', '2000-11-11'],
        'E': [1.1, 2.1, 3.5, 0.0]
    }).wc("C.str.to_date('%Y-%m-%d')")

def test_query_and_eval(sample_df):
    var1, var2 = 1, 3
    var3 = ['bc']
    res = sample_df.query("@var1 <= A < @var2 & B in @var3")
    assert res.shape == (1, 4)
    assert res['A'].to_list()[0] == 2

    # eval select
    ev = sample_df.eval("(A ** 2 - E)/(10 - A)")
    assert ev.shape == (4, 1)

    # assign
    asgn = sample_df.assign("F = A * 10")
    assert 'F' in asgn.columns
    assert asgn['F'].to_list()[0] == 10

def test_wc_multiple_statements(sample_df):
    df2 = sample_df.wc("A_sum = A.sum().over('B'); E_mean = E.mean()")
    assert 'A_sum' in df2.columns
    assert 'E_mean' in df2.columns

def test_case_when(sample_df):
    # case_when with multiple conditions
    var1 = 99
    res = sample_df.wc("D = case_when([A < 2, B in ['bc']], [10, 20], @var1)")
    assert res['D'].to_list() == [10, 20, 99, 99]

    # case_when with single condition (np.where style)
    res2 = sample_df.wc("D = case_when(A > 2, 1, 0)")
    assert res2['D'].to_list() == [0, 0, 1, 1]

    # select and where directly
    res3 = sample_df.wc("D = select([A == 1, A == 2], [100, 200], 0)")
    assert res3['D'].to_list() == [100, 200, 0, 0]

    res4 = sample_df.wc("D = where(A == 1, 100, 0)")
    assert res4['D'].to_list() == [100, 0, 0, 0]

def test_mondf(sample_df):
    res = sample_df.wc("m_diff = mondf(C, C.shift())")
    assert 'm_diff' in res.columns
    assert res['m_diff'].to_list() == [None, 24, 134, 108]

def test_gb_with_subtotal(sample_df):
    gb_res = sample_df.gb('B', 'A.sum()', with_subtotal=True)
    assert 'All' in gb_res['B'].to_list()
    total_a = gb_res.filter(pl.col('B') == 'All')['A'].to_list()[0]
    assert total_a == 10.0

def test_convenience_methods(sample_df):
    # dd
    assert sample_df.dd().shape == sample_df.shape

    # dsort & asort
    assert sample_df.dsort('A')['A'].to_list()[0] == 4
    assert sample_df.asort('A')['A'].to_list()[0] == 1

    # vcnt & ucnt
    assert sample_df.vcnt('B').shape[0] == 4
    assert sample_df.ucnt('A') == 4

    # round & cum_max
    rounded = sample_df.round(1)
    assert rounded['E'].to_list()[0] == 1.1

    cum = sample_df.cum_max()
    assert cum['E'].to_list() == [1.1, 2.1, 3.5, 3.5]

    # to_list, max, min
    assert sample_df.to_list('A') == [1, 2, 3, 4]
    assert sample_df.max('A') == 4
    assert sample_df.min('A') == 1

    # rename with list
    renamed = sample_df.rename(['col1', 'col2', 'col3', 'col4'])
    assert renamed.columns == ['col1', 'col2', 'col3', 'col4']

    # size
    sz = sample_df.size(unit='kb', return_size=True)
    assert sz > 0

    # describe groupby
    desc = sample_df.describe(group_keys='B', selected_columns=['A', 'E'])
    assert 'A_mean' in desc.columns

def test_unstack():
    df = plx.DataFrame({
        'id': [1, 1, 2, 2],
        'attr': ['x', 'y', 'x', 'y'],
        'val': [10, 20, 30, 40]
    })
    unstacked = df.unstack()
    assert 'x' in unstacked.columns
    assert 'y' in unstacked.columns

def test_merge():
    df1 = plx.DataFrame({'id': [1, 2], 'val': [10, 20]})
    df2 = plx.DataFrame({'id': [1, 2], 'val': [30, 40]})
    merged = plx.merge(df1, df2, on='id', suffixes=('_left', '_right'))
    assert 'val_left' in merged.columns
    assert 'val_right' in merged.columns

def test_rolling_prod():
    df = plx.DataFrame({'A': [1.0, 2.0, 3.0, 4.0]})
    res = df.select(plx.col('A').rolling_prod(window_size=2, min_samples=1))
    vals = [round(x, 2) for x in res['A'].to_list()]
    assert vals == [1.0, 2.0, 6.0, 12.0]

def test_lazyframe_support(sample_df):
    lazy = sample_df.lazy()
    res = lazy.wc("Z = A * 2").query("Z > 4").collect()
    assert res.shape == (2, 5)

    # LazyFrame indexing
    col_a = lazy['A'].collect()
    assert col_a.columns == ['A']

def test_cache_control():
    set_cache_mode("raw")
    assert get_cache_mode() == "raw"
    set_cache_max_size(500)
    assert get_cache_max_size() == 500
    clear_all_expr_caches()
    assert len(get_expr_cache()) == 0

def test_udf_registration(sample_df):
    def custom_add(col, val):
        return col + val

    register_udf("custom_add", custom_add)
    res = sample_df.wc("G = custom_add(A, 5)")
    assert res['G'].to_list() == [6, 7, 8, 9]

def test_interop(sample_df):
    # to_polars & to_pandas
    pl_df = sample_df.to_polars()
    assert isinstance(pl_df, pl.DataFrame)
    pd_df = sample_df.to_pandas()
    assert pd_df.shape == (4, 4)

    # plx top-level functions
    concatenated = plx.concat([sample_df, sample_df])
    assert concatenated.shape == (8, 4)

def test_series_and_df_dunders(sample_df):
    assert len(sample_df) == 4
    s = sample_df['A']
    assert len(s) == 4
    assert s[0] == 1
    assert s[1] == 2

def test_in_and_not_in_positioning():
    df = plx.DataFrame({'A': [1, 2, 3], 'B': [10, 20, 30]})
    var = [1, 2]

    # in followed by AND
    res1 = df.query("A in @var & B > 10")
    assert res1.shape == (1, 2)
    assert res1['A'].to_list() == [2]

    # literal list followed by AND
    res2 = df.query("A in [1, 2] & B > 10")
    assert res2.shape == (1, 2)
    assert res2['A'].to_list() == [2]

    # not in followed by AND
    res3 = df.query("A not in @var & B > 10")
    assert res3.shape == (1, 2)
    assert res3['A'].to_list() == [3]

    res4 = df.query("A not in [1, 2] & B > 10")
    assert res4.shape == (1, 2)
    assert res4['A'].to_list() == [3]

    # in followed by OR
    res5 = df.query("A in [1] | B > 20")
    assert res5.shape == (2, 2)
    assert res5['A'].to_list() == [1, 3]

    # inside case_when
    cw = df.wc("C = case_when([A in @var & B > 10], [999], 0)")
    assert cw['C'].to_list() == [0, 999, 0]
