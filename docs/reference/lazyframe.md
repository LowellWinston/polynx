# LazyFrame Reference

`polynx.LazyFrame` wraps `polars.LazyFrame` with the complete suite of Polynx string expression methods and enhanced lazy indexing.

```python
import polynx as plx

lazy_df = plx.DataFrame(data).lazy()
```

!!! note "Standard Polars LazyFrame Methods"
    `polynx.LazyFrame` inherits all native Polars lazy operations and optimization passes.
    
    This page covers only the **Polynx-specific lazy extensions**. For standard Polars LazyFrame methods, please refer to the [Official Polars LazyFrame Reference](https://docs.pola.rs/api/python/stable/reference/lazyframe/index.html).

---

## Lazy Execution Model

All operations on a `LazyFrame` are deferred into a query plan and executed only when `.collect()` is called:

```python
result = (
    lazy_df
    .wc("A_doubled = A * 2")
    .query("A_doubled > 10")
    .collect()
)
```

---

## Methods Inherited from DataFrame

The following methods are implemented for `LazyFrame` and operate lazily:

- **[`query(query_str)`](dataframe.md#query)**: Filters the lazy query plan using string expressions.
- **[`eval(query_str, mode)`](dataframe.md#eval)**: Evaluates string expressions lazily.
- **[`assign(query_str)`](dataframe.md#assign)**: Appends new computed columns lazily.
- **[`wc(*args, **kwargs)`](dataframe.md#wc)**: Multi-statement column mutations lazily.
- **[`gb(gp_keys, expr, with_subtotal)`](dataframe.md#gb)**: String-powered group by aggregations lazily.
- **[`dd()`](dataframe.md#dd)**: Deduplication maintaining order.
- **[`dsort(by)`](dataframe.md#dsort)**: Descending sort.
- **[`asort(by)`](dataframe.md#asort)**: Ascending sort.
- **[`describe(...)`](dataframe.md#describe)**: Evaluates and summarizes metrics.
- **[`round(decimal)`](dataframe.md#round)**: Rounds all float columns lazily.
- **[`cum_max()`](dataframe.md#cum_max)**: Cumulative maximum lazily.
- **[`rename(new_cols)`](dataframe.md#rename)**: Rename by list or dict.
- **[`unstack()`](dataframe.md#unstack)**: Pivoting (collects to eager automatically).
- **[`to_list(col_name)`](dataframe.md#to_list)**: Collects and extracts column list.
- **[`max(col_name)`](dataframe.md#max)** / **[`min(col_name)`](dataframe.md#min)**: Collects and returns scalar.

---

## Lazy Indexing Syntax

Polynx enhances `LazyFrame` with bracket indexing:

### Column Selection
```python
# Select single column
lazy_df['column_name']

# Select multiple columns
lazy_df[['col_a', 'col_b']]
```

### Expression Filtering
```python
import polars as pl

# Filter rows lazily via indexing
lazy_df[pl.col('A') > 5]
```

---

## Interoperability & Conversions

### `collect`

Execute the query plan and materialize a `polynx.DataFrame`.

```python
lazy_df.collect() -> polynx.DataFrame
```

---

### `to_polars`

Retrieve the underlying native `polars.LazyFrame`.

```python
lazy_df.to_polars() -> polars.LazyFrame
```

---

### `to_pandas`

Collects the lazy frame and converts the result into a `pandas.DataFrame`.

```python
lazy_df.to_pandas() -> pandas.DataFrame
```
