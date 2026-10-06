# First-Class LazyFrames

Polynx treats `LazyFrame` as a first-class citizen. Every string expression, assignment, and utility method is fully patched onto `LazyFrame`.

---

## Lazy Execution Pipeline

Build entire query pipelines with strings and execute them with `.collect()`:

```python
import polynx as plx

# Initialize eager DataFrame and convert to lazy
df = plx.DataFrame({
    'category': ['A', 'A', 'B', 'B'],
    'val': [10, 20, 30, 40]
})
lazy_df = df.lazy()

# Build pipeline lazily
pipeline = (
    lazy_df
    .wc("val_doubled = val * 2")
    .query("val_doubled > 30")
    .gb("category", "val_doubled.sum()")
)

# Execute query plan
result = pipeline.collect()
print(result)
```

---

## Lazy Indexing Syntax

Polynx enhances `LazyFrame` with natural indexing syntax:

```python
# Select a single column lazily
lazy_df['val']

# Select multiple columns lazily
lazy_df[['category', 'val']]

# Filter rows using an expression
lazy_df[plx.col('val') > 15]
```

---

## Lazy Conversions

Convert directly to Pandas or Polars:

```python
# .to_pandas() automatically calls .collect() under the hood
pandas_df = lazy_df.to_pandas()

# Retrieve underlying native polars.LazyFrame
native_lazy = lazy_df.to_polars()
```
