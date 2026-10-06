import polynx as plx
import polars as pl
import numpy as np

# 1. Quick Start
df = plx.DataFrame({
    'A': [1, 2, 3, 4],
    'B': ['abc', 'bc', 'aaa', None],
    'C': ['2023-01-01', '2021-01-01', '2009-11-01', '2000-11-11'],
    'E': [1.1, 2.1, 3.5, 0.0]
}).wc("C = C.str.to_date('%Y-%m-%d')")

# 2. Query
var1, var2 = 1, 3
var3 = ['bc']
q1 = df.query("@var1 <= A < @var2 & C.dt.year() >= 2020 & B in @var3")
assert q1.shape[0] == 1

# String ops & date comparison
q2 = df.query("B.str.contains('a|b')")
assert q2.shape[0] == 3

q3 = df.query("'2001-01-01' < C < '2020-01-01'")
assert q3.shape[0] == 1

q4 = df.query("B in ['aaa', 'bc']")
assert q4.shape[0] == 2

q5 = df.query("A ** 2 - E > 1")
assert q5.shape[0] == 3

q6 = df.query("not (B.is_null() & A.is_not_null())")
assert q6.shape[0] == 3

# 3. eval & assign
ev1 = df.eval("(A ** 2 - E) / (10 - A)")
assert ev1.shape == (4, 1)

df_asgn = df.assign("Score = A * 10 + E")
assert 'Score' in df_asgn.columns

# 4. wc with multi-statements
df_wc = df.wc("A_sum = A.sum().over('B'); E_mean = E.mean()")
assert 'A_sum' in df_wc.columns and 'E_mean' in df_wc.columns

# 5. case_when, select, where
df_cw1 = df.wc("D = case_when([A < 2, B in ['bc']], [10, 20], 99)")
assert df_cw1['D'].to_list() == [10, 20, 99, 99]

df_cw2 = df.wc("D = case_when(A > 2, 1, 0)")
assert df_cw2['D'].to_list() == [0, 0, 1, 1]

df_sel = df.wc("D = select([A == 1, A == 2], ['first', 'second'], 'other')")
assert df_sel['D'].to_list() == ['first', 'second', 'other', 'other']

df_wh = df.wc("D = where(A > 2, 'high', 'low')")
assert df_wh['D'].to_list() == ['low', 'low', 'high', 'high']

# 6. mondf
df_mondf = df.wc("m_diff = mondf(C, C.shift()); C_lag = C.shift()")
assert df_mondf['m_diff'].to_list() == [None, 24, 134, 108]

# 7. horizontal functions
df_horiz = df.wc("max_val = max_horizontal(A, E); min_val = min_horizontal(A, E)")
assert 'max_val' in df_horiz.columns

# 8. groupby gb with subtotal
gb1 = df.gb('B', 'A.sum(); E.mean()')
assert gb1.shape == (4, 3)

gb2 = df.gb('B', 'A.sum()', with_subtotal=True)
assert 'All' in gb2['B'].to_list()

# 9. describe
desc = df.describe(group_keys='B', selected_columns=['A', 'E']).round(2)
assert 'A_mean' in desc.columns

# 10. convenience methods
assert df.dd().shape == df.shape
assert df.dsort('A')['A'].to_list()[0] == 4
assert df.asort('A')['A'].to_list()[0] == 1
assert df.vcnt('B').shape[0] == 4
assert df.ucnt('A') == 4
assert df.round(1)['E'].to_list()[0] == 1.1
assert df.cum_max()['E'].to_list() == [1.1, 2.1, 3.5, 3.5]
assert df.to_list('A') == [1, 2, 3, 4]
assert df.max('A') == 4
assert df.min('A') == 1
sz = df.size(unit='kb', return_size=True)
assert sz > 0
renamed = df.rename(['colA', 'colB', 'colC', 'colE'])
assert renamed.columns == ['colA', 'colB', 'colC', 'colE']

# 11. unstack
unstack_df = plx.DataFrame({
    'id': [1, 1, 2, 2],
    'attr': ['x', 'y', 'x', 'y'],
    'val': [10, 20, 30, 40]
}).unstack()
assert 'x' in unstack_df.columns and 'y' in unstack_df.columns

# 12. plx.merge
m1 = plx.DataFrame({'id': [1, 2], 'val': [10, 20]})
m2 = plx.DataFrame({'id': [1, 2], 'val': [30, 40]})
merged = plx.merge(m1, m2, on='id', suffixes=('_left', '_right'))
assert 'val_left' in merged.columns and 'val_right' in merged.columns

# 13. rolling_prod
rp = df.select(plx.col('A').rolling_prod(window_size=2, min_samples=1))
assert rp['A'].to_list()[0] == 1.0

# 14. lazyframe
lazy_res = df.lazy().wc("Z = A * 2").query("Z > 4").collect()
assert lazy_res.shape == (2, 5)

# 15. caching
plx.config.set_cache_mode("raw")
assert plx.config.get_cache_mode() == "raw"
plx.clear_all_expr_caches()
assert len(plx.expr_parser.get_expr_cache()) == 0

# 16. custom UDF
def double_val(x):
    return x * 2

plx.register_udf("double_val", double_val)
udf_df = df.wc("Dbl = double_val(A)")
assert udf_df['Dbl'].to_list() == [2, 4, 6, 8]

# 17. interop
assert isinstance(df.to_polars(), pl.DataFrame)
assert len(df.to_pandas()) == 4

print("All README code examples verified successfully!")
