import polynx
import polynx as plx
import numpy as np

df = plx.DataFrame({
    'A':[1, 2, 3, 4], 
    'B': ['abc', 'bc', 'aaa', None], 
    'C': ['2023-01-01','2021-01-01','2009-11-01','2000-11-11'],
    'E': [1.1, 2.1, 3.5, 0]}
).wc(plx.col('C').str.to_datetime(format='%Y-%m-%d',time_unit='ns').dt.date())

var1 = 0
var2 = 10
var4 = ['abc']
var5 = '2001-01-01'
var3 = '2020-01-01'
var6 = np.array(range(df.shape[0]))

for query_str in ["@var1 <= A < @var2 & C.dt.year() >=2020 & B in @var4", "B.str.contains('a|b')", "C >'2010-01-01' & A > 1", " B in ['aaa','bc']", 
                  " A == 1", " A ** 2 - E > 1", "@var5 < C < @var3 ", 
                  " B.str.ends_with('c')", " not (B.is_null() & A.is_not_null())", "A.rolling_prod(window_size=3, min_samples=1).over('B') < 2",
                  "A ** 2 - E > 1"
                  ]:
    print(query_str)
    print(df.query(query_str))
    
for query_str in ["select([A <1, B in ['abc']], [1, E], @var1)"]:
    print(query_str)
    print(df.wc(query_str))

print("Test gb", df.gb('B', 'A.sum()'))
print("Test gb with subtotal", df.gb('B', 'A.sum()', with_subtotal=True))
print("Test plx.concat:", plx.concat([df, df]))
print("Test lazy.describe:", df.lazy().describe())
print("Tests describe:", df.describe(group_keys='B', selected_columns=['A','E']).round())
print('✅ Function ran successfully')
print("type(plx.DataFrame) = ", type(plx.DataFrame))
print("type(plx.LazyFrame) = ", type(plx.LazyFrame))
print("type(plx.Series) = ", type(plx.Series))
print("type(plx.Expr) = ", type(plx.Expr))
print("Test alias", df.eval(" (A + 1).alias('A')"))
num = 4
print("Test var in arithimatic calcultion", df.eval(" where(A>1, 1 + E.pow(@num/12), 0)"))
print("cached expr", polynx.expr_parser.get_expr_cache())