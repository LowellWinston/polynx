# Input / Output & Merge Reference

Polynx re-exports all public Polars top-level functions with automatic argument unwrapping and return-value wrapping.

---

## Functions

### `merge`

Pandas-style join interface for `DataFrame` or `LazyFrame` with automatic column suffix handling on overlapping names.

```python
plx.merge(
    left: DataFrame | LazyFrame,
    right: DataFrame | LazyFrame,
    on: str | list[str] | None = None,
    how: str = "inner",
    suffixes: tuple[str, str] = ("_x", "_y")
) -> DataFrame | LazyFrame
```

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `left` | `DataFrame` or `LazyFrame` | *required* | Left table. |
| `right` | `DataFrame` or `LazyFrame` | *required* | Right table. |
| `on` | `str`, `list[str]`, or `None` | `None` | Join column key(s). |
| `how` | `str` | `"inner"` | Join strategy: `"inner"`, `"left"`, `"right"`, or `"outer"`. |
| `suffixes` | `tuple[str, str]` | `("_x", "_y")` | Suffixes appended to overlapping columns not in `on`. |

**Returns:**
- `DataFrame` or `LazyFrame`: Joined dataset.

**Examples:**
```python
import polynx as plx

df1 = plx.DataFrame({'id': [1, 2], 'val': [10, 20]})
df2 = plx.DataFrame({'id': [1, 2], 'val': [30, 40]})

merged = plx.merge(df1, df2, on='id', suffixes=('_a', '_b'))
# Columns: ['id', 'val_a', 'val_b']
```

---

## Inherited Polars Functions

All public Polars functions are accessible directly from the `polynx` namespace:

### Data Creation & IO
```python
# Concat DataFrames or LazyFrames
df_all = plx.concat([df1, df2])

# Reading and Writing
df = plx.read_csv("data.csv")
df = plx.read_parquet("data.parquet")
```

### Expression Builders
```python
# Column references and literals
plx.col("Sales")
plx.lit(100)

# Native conditional expressions
plx.when(plx.col("Sales") > 50).then(1).otherwise(0)
```

All functions perform deep unwrapping on inputs and wrap return types back into `polynx` instances.
