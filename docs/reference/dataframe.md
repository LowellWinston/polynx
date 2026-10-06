# DataFrame Reference

`polynx.DataFrame` is a transparent wrapper around `polars.DataFrame` that inherits all native Polars methods while adding string expression capabilities and productivity helpers.

```python
import polynx as plx

df = plx.DataFrame(data)
```

!!! note "Standard Polars DataFrame Methods"
    `polynx.DataFrame` inherits all native Polars methods (e.g. `.filter()`, `.select()`, `.join()`, `.group_by()`, `.pivot()`, etc.).
    
    This page documents only the **Polynx-specific extension methods**. For native Polars DataFrame methods, please refer to the [Official Polars DataFrame Reference](https://docs.pola.rs/api/python/stable/reference/dataframe/index.html).

---

## String Expression Methods

### `query`

Filter rows of the DataFrame using an intuitive string expression.

```python
df.query(query_str: str) -> DataFrame
```

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `query_str` | `str` | A filter expression string supporting comparison operators, boolean logic (`&`, `|`, `~`, `not`), membership (`in`, `not in`), string methods, and variable substitution (`@var`). |

**Returns:**
- `DataFrame`: A filtered DataFrame containing only matching rows.

**Examples:**
```python
# Simple comparison
df.query("A > 10")

# Chained comparison with variables
min_val, max_val = 1, 5
df.query("@min_val <= A < @max_val & B in ['x', 'y']")

# Date and string filtering
df.query("Date > '2022-01-01' & Name.str.contains('admin')")
```

---

### `eval`

Evaluate an expression or mathematical operation string.

```python
df.eval(query_str: str | list[str], mode: str = "select") -> DataFrame
```

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `query_str` | `str` or `list[str]` | *required* | The expression string or list of expression strings to evaluate. |
| `mode` | `str` | `"select"` | Evaluation mode. `"select"` returns only the evaluated columns. `"assign"` appends the evaluated columns to the DataFrame. |

**Returns:**
- `DataFrame`: Evaluated columns in `"select"` mode, or the mutated DataFrame in `"assign"` mode.

**Examples:**
```python
# Select mode (returns only the calculated column)
df.eval("(A ** 2 - E) / (10 - A)")

# Multiple expressions
df.eval(["A * 2", "E + 10"])
```

---

### `assign`

Convenience alias for `df.eval(query_str, mode="assign")`. Appends evaluated columns to the DataFrame.

```python
df.assign(query_str: str | list[str]) -> DataFrame
```

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `query_str` | `str` or `list[str]` | Assignment string (e.g., `"New_Col = A * 10"`). |

**Returns:**
- `DataFrame`: The DataFrame with new column(s) appended.

**Examples:**
```python
df.assign("Total_Score = (A * 10) + E")
```

---

### `wc`

Extended `with_columns` supporting multi-statement assignment strings separated by semicolons (`;`), lists of expressions, and native Polars expressions.

```python
df.wc(*args, **kwargs) -> DataFrame
```

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `*args` | `str`, `Expr`, or `list` | Expression strings, multi-statement strings, or Polars expressions. |
| `**kwargs` | `Expr` | Standard Polars keyword column assignments. |

**Returns:**
- `DataFrame`: The DataFrame with updated or added columns.

**Examples:**
```python
# Multi-statement string assignment
df.wc("A_sum = A.sum().over('B'); E_mean = E.mean(); Ratio = A / E_mean")

# Mixing strings and native Polars expressions
import polars as pl
df.wc("Flag = A > 2", pl.col("E") * 100)
```

---

### `gb`

String-powered group-by aggregation with optional hierarchical subtotal rows.

```python
df.gb(gp_keys: str | list[str], expr: str, with_subtotal: bool = False) -> DataFrame
```

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `gp_keys` | `str` or `list[str]` | *required* | One or more column names to group by. |
| `expr` | `str` | *required* | Semicolon-separated string aggregation expressions (e.g. `"A.sum(); E.mean()"`). |
| `with_subtotal` | `bool` | `False` | When `True`, automatically appends hierarchical subtotal rows and an `'All'` summary row. |

**Returns:**
- `DataFrame`: Aggregated DataFrame sorted by group keys.

**Examples:**
```python
# Basic aggregation
df.gb("Category", "Sales.sum(); Margin.mean()")

# Multi-key with subtotal
df.gb(["Region", "Category"], "Sales.sum()", with_subtotal=True)
```

---

## Descriptive Statistics & Summaries

### `describe`

Extended summary statistics. When `group_keys` is provided, computes grouped summary metrics (count, null_count, mean, std, min, quantiles, max) across numeric columns.

```python
df.describe(
    group_keys: str | list[str] | None = None,
    selected_columns: list[str] | None = None,
    percentiles: tuple[float, ...] = (0.25, 0.5, 0.75),
    interpolation: str = "nearest"
) -> DataFrame
```

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `group_keys` | `str`, `list[str]`, or `None` | `None` | Column(s) to group by for statistics. If `None`, calls Polars' native `.describe()`. |
| `selected_columns` | `list[str]` or `None` | `None` | Numeric columns to summarize. Defaults to all numeric columns. |
| `percentiles` | `tuple[float, ...]` | `(0.25, 0.5, 0.75)` | Quantiles to compute. |
| `interpolation` | `str` | `"nearest"` | Quantile interpolation method. |

**Returns:**
- `DataFrame`: Summary statistics table.

**Examples:**
```python
# Grouped summary statistics
df.describe(group_keys="Category", selected_columns=["Sales", "Profit"]).round(2)
```

---

## Convenience Utilities

### `dd`

Deduplicate rows while maintaining row order and keeping the first occurrence.

```python
df.dd() -> DataFrame
```

**Returns:**
- `DataFrame`: Unique rows preserving original order (equivalent to `df.unique(maintain_order=True, keep='first')`).

---

### `dsort`

Sort rows in descending order.

```python
df.dsort(by: str | list[str] | None = None) -> DataFrame
```

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `by` | `str`, `list[str]`, or `None` | `None` | Column(s) to sort by. If `None`, sorts by all columns. |

---

### `asort`

Sort rows in ascending order.

```python
df.asort(by: str | list[str] | None = None) -> DataFrame
```

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `by` | `str`, `list[str]`, or `None` | `None` | Column(s) to sort by. If `None`, sorts by all columns. |

---

### `unstack`

Pivot long-form data using the last two columns as the pivot key and value columns, sorted by the remaining index columns.

```python
df.unstack() -> DataFrame
```

**Returns:**
- `DataFrame`: Pivoted DataFrame.

---

### `vcnt`

Compute value frequency counts for specified column(s), sorted in descending order by count.

```python
df.vcnt(col: str | list[str] | None = None) -> DataFrame
```

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `col` | `str`, `list[str]`, or `None` | `None` | Column(s) to count. Defaults to all columns. |

---

### `ucnt`

Compute the total distinct / unique count of rows or values.

```python
df.ucnt(col: str | list[str] | None = None) -> int
```

**Returns:**
- `int`: Scalar integer count of distinct values.

---

### `round`

Round all floating-point columns across the DataFrame.

```python
df.round(decimal: int = 2) -> DataFrame
```

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `decimal` | `int` | `2` | Number of decimal places. |

---

### `cum_max`

Calculate the cumulative maximum across all floating-point columns.

```python
df.cum_max() -> DataFrame
```

---

### `to_list`

Extract values of a column directly into a native Python list.

```python
df.to_list(col_name: str | None = None) -> list
```

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `col_name` | `str` or `None` | `None` | Target column name. Defaults to the first column. |

---

### `max`

Extract scalar maximum value from a column.

```python
df.max(col_name: str | None = None) -> Any
```

---

### `min`

Extract scalar minimum value from a column.

```python
df.min(col_name: str | None = None) -> Any
```

---

### `size`

Print estimated DataFrame memory footprint and optionally return the float value.

```python
df.size(unit: str = "mb", return_size: bool = False) -> float | None
```

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `unit` | `str` | `"mb"` | Unit: `"b"`, `"kb"`, `"mb"`, or `"gb"`. |
| `return_size` | `bool` | `False` | When `True`, returns the float size. |

---

### `rename`

Enhanced column rename. Accepts either a dictionary mapping or a list of new column names matching the DataFrame's width.

```python
df.rename(new_cols: list[str] | dict[str, str]) -> DataFrame
```

**Examples:**
```python
# Rename by list
df.rename(["Col_A", "Col_B", "Col_C"])

# Rename by dict (standard Polars)
df.rename({"Old": "New"})
```

---

### `pplot`

Quick plotting using Pandas' `plot()` interface, setting the first column as the index.

```python
df.pplot(*args, **kwargs)
```

---

## Interoperability & Conversions

### `to_polars`

Retrieve the underlying native `polars.DataFrame`.

```python
df.to_polars() -> polars.DataFrame
```

---

### `to_pandas`

Convert to a `pandas.DataFrame`.

```python
df.to_pandas() -> pandas.DataFrame
```
