# Extended DataFrame Utilities

Polynx patches both `DataFrame` and `LazyFrame` with common productivity utilities inspired by Pandas and SQL.

---

## Deduplication: `dd()`

Deduplicates rows while maintaining row order and keeping the first occurrence:

```python
import polynx as plx

df = plx.DataFrame({'A': [1, 1, 2, 3], 'B': ['x', 'x', 'y', 'z']})
df.dd()
```

*(Equivalent to `df.unique(maintain_order=True, keep='first')`)*

---

## Sorting: `dsort()` and `asort()`

Quick descending and ascending sorting:

```python
# Sort descending by specific column(s)
df.dsort('A')

# If 'by' is omitted, sorts by all columns
df.dsort()

# Sort ascending
df.asort('A')
```

---

## Pivoting: `unstack()`

Pivots a DataFrame using the last two columns as the pivot key and value columns, sorted by index:

```python
df_long = plx.DataFrame({
    'user_id': [1, 1, 2, 2],
    'metric': ['score', 'level', 'score', 'level'],
    'val': [95, 3, 80, 2]
})

df_long.unstack()
```

---

## Value & Unique Counts: `vcnt()` and `ucnt()`

### Frequency Counts with `vcnt(col=None)`
Computes frequency counts of values in specified column(s), sorted in descending order:

```python
# Value count on column 'B'
df.vcnt('B')

# If omitted, computes frequency across all columns
df.vcnt()
```

### Unique Count with `ucnt(col=None)`
Returns the total number of distinct rows/values as an integer scalar:

```python
distinct_count = df.ucnt('A')
```

---

## String GroupBy: `gb()`

Aggregate grouped data with string expressions.

```python
# Group by 'B' and calculate sum of A and mean of E
df.gb('B', "A.sum(); E.mean()")
```

### Automatic Subtotals & Total Row
Enable `with_subtotal=True` to compute hierarchical subtotals and an `'All'` summary row:

```python
df.gb('B', "A.sum()", with_subtotal=True)
```

For multi-key groupings (`df.gb(['Region', 'City'], ...)`), `with_subtotal=True` calculates intermediate totals for each higher level before appending the global summary.

---

## Grouped Descriptive Statistics: `describe()`

Extends Polars' native `.describe()` by supporting grouping keys:

```python
# Computes count, null_count, mean, std, min, 25%, 50%, 75%, max grouped by 'B'
df.describe(group_keys='B', selected_columns=['A', 'E']).round(2)
```

---

## Float Utilities: `round()` and `cum_max()`

- **`df.round(decimal=2)`**: Rounds all floating-point columns across the DataFrame without having to list them manually.
- **`df.cum_max()`**: Computes cumulative maximum across all floating-point columns.

```python
df.round(2)
df.cum_max()
```

---

## Scalar Extraction & List Conversion

- **`df.to_list(col_name=None)`**: Extracts column as a Python list (defaults to first column).
- **`df.max(col_name=None)`**: Returns scalar maximum value.
- **`df.min(col_name=None)`**: Returns scalar minimum value.

```python
a_values = df.to_list('A')  # [1, 2, 3, 4]
max_a = df.max('A')         # 4
min_a = df.min('A')         # 1
```

---

## Rename by List: `rename()`

In addition to Polars' standard dictionary rename syntax, Polynx allows renaming columns with a list of new names matching the number of columns:

```python
df.rename(['Col_1', 'Col_2', 'Col_3', 'Col_4'])
```

---

## Memory Footprint: `size()`

Prints the estimated DataFrame memory footprint and optionally returns the size:

```python
# Print to console (DataFrame size: 0.12 MB)
df.size(unit='mb')

# Return numeric size value
size_kb = df.size(unit='kb', return_size=True)
```

---

## Quick Visualization: `pplot()`

Provides pandas-style `.plot()` directly from a Polynx DataFrame, setting the first column as index:

```python
df.select(['Date', 'Revenue']).pplot(kind='line')         # plx.DataFrame / plx.LazyFrame
pl_df.select(['Date', 'Revenue']).plx.pplot(kind='line')  # native polars objects
```

---

## Pandas-Style Merge: `plx.merge()`

Merges two DataFrames or LazyFrames with automatic suffix handling for overlapping column names:

```python
left = plx.DataFrame({'id': [1, 2], 'val': [10, 20]})
right = plx.DataFrame({'id': [1, 2], 'val': [30, 40]})

merged = plx.merge(left, right, on='id', how='inner', suffixes=('_left', '_right'))
```

---

## Window Rolling Product: `Expr.rolling_prod()`

Polynx patches `plx.Expr` with a rolling product calculation (numerically computed via log-sum-exp):

```python
df.select(plx.col('A').rolling_prod(window_size=2, min_samples=1))
```
