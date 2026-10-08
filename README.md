<p align="center">
  <img src="https://github.com/LowellWinston/polynx/raw/master/assets/logo.png" width="120" alt="Polynx logo"/>
</p>

# Polynx

[![PyPI version](https://img.shields.io/pypi/v/polynx.svg?logo=pypi)](https://pypi.org/project/polynx/)
[![GitHub release](https://img.shields.io/github/v/release/LowellWinston/polynx?logo=github)](https://github.com/LowellWinston/polynx/releases)
[![Documentation](https://img.shields.io/badge/docs-GitHub_Pages-blue.svg)](https://lowellwinston.github.io/polynx/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**Polynx** is a string-powered Polars expression engine with extended DataFrame and LazyFrame utilities. It brings the intuitive, concise string syntax of Pandas and SQL (such as query filtering, variable substitution, multi-statement evaluation, and conditional branching like `case_when`) directly to Polars while preserving Polars' blazing-fast execution and lazy query optimization.

---

## Table of Contents

- [Key Features](#key-features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [String Expression Engine](#string-expression-engine)
  - [Row Filtering with `query()`](#row-filtering-with-query)
  - [Variable Substitution (`@var`)](#variable-substitution-var)
  - [Multi-Statement Assignments with `wc()`](#multi-statement-assignments-with-wc)
  - [Expression Evaluation with `eval()` and `assign()`](#expression-evaluation-with-eval-and-assign)
  - [Conditional Logic: `case_when()`, `select()`, and `where()`](#conditional-logic-case_when-select-and-where)
  - [Date Arithmetic & `mondf()`](#date-arithmetic--mondf)
  - [Horizontal Operations: `max_horizontal()` & `min_horizontal()`](#horizontal-operations-max_horizontal--min_horizontal)
  - [Window Expressions & Method Chaining](#window-expressions--method-chaining)
  - [Column Names with Spaces (Backticks)](#column-names-with-spaces-backticks)
- [Extended DataFrame & LazyFrame Utilities](#extended-dataframe--lazyframe-utilities)
  - [Deduplication with `dd()`](#deduplication-with-dd)
  - [Convenient Sorting: `dsort()` & `asort()`](#convenient-sorting-dsort--asort)
  - [Pivoting with `unstack()`](#pivoting-with-unstack)
  - [Value & Unique Counts: `vcnt()` & `ucnt()`](#value--unique-counts-vcnt--ucnt)
  - [String-Powered GroupBy with `gb()` & Subtotals](#string-powered-groupby-with-gb--subtotals)
  - [Extended Grouped Summary Statistics with `describe()`](#extended-grouped-summary-statistics-with-describe)
  - [Float Utilities: `round()` & `cum_max()`](#float-utilities-round--cum_max)
  - [Scalar Extraction & List Conversion: `to_list()`, `max()`, `min()`](#scalar-extraction--list-conversion-to_list-max-min)
  - [Rename by List: `rename()`](#rename-by-list-rename)
  - [Memory Footprint Inspection: `size()`](#memory-footprint-inspection-size)
  - [Quick Visualization with `pplot()`](#quick-visualization-with-pplot)
  - [Pandas-Style Merge: `plx.merge()`](#pandas-style-merge-plxmerge)
- [Extended Polars Expressions](#extended-polars-expressions)
  - [Rolling Product: `rolling_prod()`](#rolling-product-rolling_prod)
- [First-Class LazyFrame Support](#first-class-lazyframe-support)
- [Performance & Coming from pandas](#performance--coming-from-pandas)
- [Expression Parser Caching](#expression-parser-caching)
- [Custom UDF Registration](#custom-udf-registration)
- [Polars & Pandas Interoperability](#polars--pandas-interoperability)
- [Using Polynx with AI Agents](#using-polynx-with-ai-agents)
- [Contributing](#contributing)
- [License](#license)

---

## Key Features

- **String Expression Engine**: Write filtering, mathematical calculations, and column mutations using clean string expressions.
- **Variable Substitution (`@var`)**: Reference external variables, lists, arrays, or dates directly within string expressions.
- **Conditional Branching (`case_when`, `select`, `where`)**: Express complex conditional logic in string queries without verbose nested `.when().then().otherwise()` chains.
- **Multi-Statement Assignments**: Assign multiple columns sequentially separated by semicolons (`;`) in `.wc()` or `.assign()`.
- **String GroupBy Aggregations (`gb`)**: Run aggregate calculations using string expressions, with automatic subtotal rows via `with_subtotal=True`.
- **Extended Statistical Summaries**: Grouped descriptive statistics via `.describe(group_keys=...)`.
- **Convenience Utilities**: Shorthand helpers for deduplication (`dd`), sorting (`dsort`/`asort`), pivoting (`unstack`), counting (`vcnt`/`ucnt`), and memory reporting (`size`).
- **Extended Expressions**: Window rolling product (`rolling_prod`) for Polars expressions.
- **Full LazyFrame Support**: All string methods and convenience methods work seamlessly on both eager `DataFrame` and lazy `LazyFrame`.
- **Expression Caching & Diagnostics**: High-performance LRU and hashing caching for parsed expressions, plus a template cache so loops with changing values (`A > 1`, `A > 2`, ...) or `@var` don't re-parse each time.
- **Seamless Polars Compatibility**: Fully wraps Polars; all standard Polars functions and methods (`plx.concat`, `plx.col`, etc.) are natively supported.

---

## Installation

### Via PyPI (Recommended)

```bash
pip install polynx
```

### From Source

```bash
git clone https://github.com/LowellWinston/polynx.git
cd polynx
pip install .
```

---

## Quick Start

```python
import polynx as plx

# Create a Polynx DataFrame (wraps polars.DataFrame)
df = plx.DataFrame({
    'A': [1, 2, 3, 4],
    'B': ['abc', 'bc', 'aaa', None],
    'C': ['2023-01-01', '2021-01-01', '2009-11-01', '2000-11-11'],
    'E': [1.1, 2.1, 3.5, 0.0]
}).wc("C = C.str.to_date('%Y-%m-%d')")

# Filter using query with variable substitution
threshold = 2
result = df.query("A >= @threshold & B in ['bc', 'aaa']")
print(result)
```

### Native Polars Namespace (`df.plx.*`)

You can also use Polynx methods directly on native Polars DataFrames and LazyFrames without creating a `plx.DataFrame` wrapper:

```python
import polars as pl
import polynx  # registers the .plx namespace on Polars DataFrames and LazyFrames

df = pl.DataFrame({'A': [1, 2, 3], 'B': [10, 20, 30]})
result = df.plx.query("A > 1 & B >= 20").plx.assign("C = A + B")
```

---

## String Expression Engine

### Row Filtering with `query()`

`df.query(query_str)` provides an intuitive filtering interface similar to Pandas' `.query()`, powered by Polars:

```python
# Chained comparison & logical operators
df.query("1 <= A < 4 & E > 1.0")

# Negation and null checks
df.query("not (B.is_null() & A.is_not_null())")

# Mathematical expressions in filters
df.query("A ** 2 - E > 1")

# String operations
df.query("B.str.contains('a|b')")
df.query("B.str.ends_with('c')")

# Date comparisons with strings
df.query("'2001-01-01' < C < '2020-01-01'")

# Membership testing
df.query("B in ['aaa', 'bc']")
df.query("B not in ['abc']")
```

### Variable Substitution (`@var`)

Prefixing an identifier with `@` pulls the variable dynamically from surrounding scopes:

```python
min_val = 1
max_val = 3
target_categories = ['bc', 'aaa']
cutoff_date = '2010-01-01'

df.query("@min_val <= A <= @max_val & B in @target_categories & C > @cutoff_date")
```

Variables can be numbers, strings, lists, numpy arrays, or dates. Polynx automatically disables expression caching for expressions containing `@` so loop variable updates are always respected:

```python
tmp = plx.DataFrame()
for i in [10, 20]:
    print(tmp.wc("A = @i"))
```

### Multi-Statement Assignments with `wc()`

The `.wc()` method extends Polars' `with_columns()` by supporting multi-statement assignment strings separated by semicolons (`;`):

```python
# Multiple sequential assignments in a single call
df_new = df.wc("A_sum = A.sum().over('B'); E_mean = E.mean(); Ratio = A / E_mean")

# Mix string expressions and native Polars expressions
import polars as pl
df_new = df.wc(
    "Flag = A > 2",
    pl.col("E") * 100
)
```

### Expression Evaluation with `eval()` and `assign()`

- `df.eval(query_str, mode='select')`: Evaluates an expression and returns only the calculated column(s).
- `df.assign(query_str)`: Convenience shorthand for `df.eval(query_str, mode='assign')`, appending the calculated columns to the DataFrame.

```python
# Return calculated column
df.eval("(A ** 2 - E) / (10 - A)")

# Append calculated column
df.assign("Score = A * 10 + E")
```

### Conditional Logic: `case_when()`, `select()`, and `where()`

Polynx provides built-in conditional branching functions inside string expressions, eliminating deeply nested Polars `.when().then()` expressions:

#### `case_when(conds, choices, default)`

Unified conditional branching that handles both multiple conditions and single conditions:

```python
# Multi-condition branching (conditions list, choices list, default)
df.wc("Tier = case_when([A < 2, B in ['bc']], ['Bronze', 'Silver'], 'Gold')")

# Single-condition branching (condition, choice, default)
df.wc("Is_High = case_when(A > 2, 1, 0)")
```

#### `select(conds, choices, default)`

Mirrors `numpy.select` for multi-condition branching:

```python
df.wc("Category = select([A == 1, A == 2], ['First', 'Second'], 'Other')")
```

#### `where(cond, choice, default)`

Mirrors `numpy.where` for ternary branching:

```python
df.wc("Status = where(A >= 3, 'High', 'Low')")
```

### Date Arithmetic & `mondf()`

Calculate the month difference between two dates/datetimes with `mondf(beg_date, end_date)`:

```python
df.wc("Months_Diff = mondf(C, C.shift()); Prev_Date = C.shift()")
```

### Horizontal Operations: `max_horizontal()` & `min_horizontal()`

Polars' horizontal aggregations are registered and directly usable inside string expressions:

```python
df.wc("Row_Max = max_horizontal(A, E); Row_Min = min_horizontal(A, E)")
```

### Window Expressions & Method Chaining

String expressions support Polars window operations via `.over()` (accepting single column names or lists of column names) and dynamic method chaining:

```python
# Window aggregation over a column
df.wc("Group_Mean = A.mean().over('B')")

# Window aggregation over multiple columns
df.wc("Multi_Group_Mean = A.mean().over(['B', 'C'])")

# Method chaining
df.wc("Processed = B.str.to_uppercase().str.slice(0, 2)")
```

### Column Names with Spaces (Backticks)

Reference columns with spaces or special characters using backticks (`` ` ``):

```python
df_special = plx.DataFrame({"First Name": ["Alice", "Bob"], "Score Value": [85, 92]})
df_special.query("`Score Value` > 90 & `First Name` == 'Bob'")
```

---

## Extended DataFrame & LazyFrame Utilities

Polynx patches both `DataFrame` and `LazyFrame` with productivity helpers:

### Deduplication with `dd()`

Deduplicates rows while maintaining order and keeping the first occurrence:

```python
df.dd()  # Equivalent to df.unique(maintain_order=True, keep='first')
```

### Convenient Sorting: `dsort()` & `asort()`

Quick descending and ascending sorting:

```python
# Descending sort (defaults to all columns if by is omitted)
df.dsort('A')

# Ascending sort
df.asort('A')
```

### Pivoting with `unstack()`

Pivots a DataFrame using the last two columns as the pivot key and value column, sorted by index:

```python
df_piv = plx.DataFrame({
    'id': [1, 1, 2, 2],
    'attribute': ['height', 'weight', 'height', 'weight'],
    'value': [180, 75, 165, 60]
})

df_piv.unstack()
```

### Value & Unique Counts: `vcnt()` & `ucnt()`

```python
# Frequency count grouped by column(s), sorted descending by count
df.vcnt('B')

# Total distinct/unique count as a scalar
count = df.ucnt('A')
```

### String-Powered GroupBy with `gb()` & Subtotals

Aggregate grouped data with string expressions. Enable `with_subtotal=True` to automatically append hierarchical subtotal rows and an `'All'` total summary row:

```python
# Group by with string aggregation
df.gb('B', "A.sum(); E.mean()")

# Group by with subtotal row ('All')
df.gb('B', "A.sum()", with_subtotal=True)
```

### Extended Grouped Summary Statistics with `describe()`

Extends Polars' `.describe()` to support grouping by keys for selected columns:

```python
# Computes count, null_count, mean, std, min, 25%, 50%, 75%, max grouped by 'B'
df.describe(group_keys='B', selected_columns=['A', 'E']).round(2)
```

### Float Utilities: `round()` & `cum_max()`

- `df.round(decimal=2)`: Rounds all floating-point columns across the DataFrame.
- `df.cum_max()`: Calculates the cumulative maximum for all floating-point columns.

```python
df.round(2)
df.cum_max()
```

### Scalar Extraction & List Conversion: `to_list()`, `max()`, `min()`

Extract column values quickly without verbose `.get_column().to_list()` calls:

```python
# Extract column to a Python list (defaults to first column if col_name is omitted)
values = df.to_list('A')  # [1, 2, 3, 4]

# Extract scalar max and min values
max_val = df.max('A')    # 4
min_val = df.min('A')    # 1
```

### Rename by List: `rename()`

In addition to Polars' standard dictionary rename syntax, Polynx allows renaming columns by supplying a list of new names matching the number of columns:

```python
df.rename(['Col_1', 'Col_2', 'Col_3', 'Col_4'])
```

### Memory Footprint Inspection: `size()`

Prints the estimated DataFrame memory footprint and optionally returns the size:

```python
# Prints size to console
df.size(unit='kb')

# Return numeric value
size_in_mb = df.size(unit='mb', return_size=True)
```

### Quick Visualization with `pplot()`

Provides pandas-style `.plot()` directly from a Polynx DataFrame, setting the first column as index:

```python
df.select(['A', 'E']).pplot(kind='line')     # plx.DataFrame / plx.LazyFrame
pl_df.select(['A', 'E']).plx.pplot(kind='line')  # native polars objects
```

### Pandas-Style Merge: `plx.merge()`

Merges two DataFrames or LazyFrames with automatic suffix handling for overlapping column names:

```python
left = plx.DataFrame({'id': [1, 2], 'val': [10, 20]})
right = plx.DataFrame({'id': [1, 2], 'val': [30, 40]})

merged = plx.merge(left, right, on='id', how='inner', suffixes=('_left', '_right'))
```

---

## Extended Polars Expressions

Polynx patches `Expr` with additional mathematical operations:

### Rolling Product: `rolling_prod()`

Computes the rolling product across a window (evaluated numerically via log transform and rolling sum):

```python
df.select(plx.col('A').rolling_prod(window_size=2, min_samples=1))
```

---

## First-Class LazyFrame Support

All Polynx methods are fully compatible with `LazyFrame`. Operations are deferred until `.collect()`:

```python
lazy_df = df.lazy()

result = (
    lazy_df
    .wc("A_doubled = A * 2")
    .query("A_doubled > 4")
    .collect()
)

# Convenient indexing on LazyFrames
lazy_df['A']                   # Select column
lazy_df[['A', 'B']]            # Select multiple columns
lazy_df[pl.col('A') > 2]       # Filter rows lazily

# Convert LazyFrame to Pandas directly (collects automatically)
pandas_df = lazy_df.to_pandas()
```

---

## Performance & Coming from pandas

Polynx parses your string once into a native Polars expression, so the work itself runs in Polars' Rust engine. Compared with `pandas.query`:

| Rows | Polars (hand-written) | **polynx** | pandas `query` |
|---:|---:|---:|---:|
| 1,000 | 0.31 ms | **0.28 ms** | 1.71 ms |
| 100,000 | 1.34 ms | **1.24 ms** | 4.82 ms |
| 5,000,000 | 48.2 ms | **48.8 ms** | 115 ms |

*Median per call for `A > 5 & B in ['x', 'y'] & A * 2 < N`, repeated queries. Run `python benchmarks/bench.py` to reproduce on your machine, including the uncached and changing-value cases.*

| pandas | polynx |
|---|---|
| `df.query("A > 2 and B == 'x'")` | `df.query("A > 2 & B == 'x'")` |
| `df.eval("C = A * 2")` | `df.assign("C = A * 2")` |
| `df.query("A > @t")` | `df.query("A > @t")` |
| ``df.query("`Score Value` > 90")`` | ``df.query("`Score Value` > 90")`` |
| `df.groupby("B").agg(...)` | `df.gb("B", "S = A.sum(); M = A.mean()")` |

Unlike pandas, polynx works on `LazyFrame` as well, so Polars can optimize the whole query.

---

## Expression Parser Caching

Polynx caches parsed Lark expression trees to eliminate parsing overhead on repeated queries.

### Cache Modes

Configure caching behavior via `plx.config`:

- `"raw"` (default): In-memory dictionary cache keyed by expression string.
- `"hash"`: SHA1-hashed cache for expressions.
- `"custom_lru"`: LRU cache with configurable capacity.
- `"none"`: Disables caching completely.

```python
import polynx as plx

# Change cache mode
plx.config.set_cache_mode("custom_lru")
plx.config.set_cache_max_size(2000)

# Check active configuration
print(plx.config.get_cache_mode())       # 'custom_lru'
print(plx.config.get_cache_max_size())   # 2000
```

### Cache Diagnostics & Management

```python
# Inspect cached expressions
cache = plx.expr_parser.get_expr_cache()
cache_size = plx.expr_parser.get_expr_cache_size()

# Clear cache and reset statistics
plx.clear_all_expr_caches()
plx.expr_parser.reset_expr_cache_stats()
```

> **Note**: Queries using `@var` skip the exact-string cache so changed variable values are never stale. Their parse tree is still cached as a template, and `@var` values are re-read on every call.

---

## Custom UDF Registration

Register custom Python functions to call them directly within string expressions:

```python
import polynx as plx

# 1. Register a single function
def add_bonus(score, multiplier=1.1):
    return score * multiplier

plx.register_udf("add_bonus", add_bonus)

# Use inside string expressions
df = plx.DataFrame({'A': [10, 20, 30]})
df.wc("Bonus = add_bonus(A, 1.25)")

# 2. Register functions by name from a module
import math
plx.register_udfs_by_names(math, ['sin', 'cos', 'sqrt'])
```

---

## Polars & Pandas Interoperability

Polynx is designed as a drop-in enhancement to Polars:

- **Polars Function Inheritance**: All Polars top-level functions (`concat`, `col`, `lit`, `when`, `read_csv`, `read_parquet`, etc.) are exposed directly through `polynx` with automatic wrapping and unwrapping:
  ```python
  import polynx as plx
  df_combined = plx.concat([df, df])
  ```
- **Conversion to Polars**: Call `.to_polars()` on any DataFrame, LazyFrame, Series, or Expr to retrieve native Polars objects.
- **Conversion to Pandas**: Call `.to_pandas()` on any DataFrame, LazyFrame, or Series.

---

## Using Polynx with AI Agents

Polynx ships a concise API guide for coding agents, no MCP server required:

```bash
pip install polynx
python -m polynx          # prints the agent guide (or: polynx.agent_guide())
```

- [`src/polynx/AGENTS.md`](src/polynx/AGENTS.md): the bundled guide
- [`skills/polynx/SKILL.md`](skills/polynx/SKILL.md): drop-in Claude Code skill (copy into `.claude/skills/polynx/`)
- [`llms.txt`](https://lowellwinston.github.io/polynx/llms.txt) and an [ARD](https://github.com/ards-project/ard-spec) manifest at `/.well-known/ard.json` on the docs site

---

## Contributing

We welcome contributions! If you'd like to help improve Polynx:
1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

---

## License

This project is licensed under the MIT License - see the [LICENSE](file:///home/ubuntu/polynx/LICENSE) file for details.
