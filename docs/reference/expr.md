# Expressions (Expr) Reference

`polynx.Expr` wraps `polars.Expr` and provides extended mathematical operations.

---

## Extended Expression Methods

### `rolling_prod`

Compute the rolling product across a moving window.

Evaluated numerically via log-transformation:
$$\text{rolling\_prod}(x) = \exp\left(\text{rolling\_sum}(\log(x))\right)$$

```python
expr.rolling_prod(*args, **kwargs) -> Expr
```

**Parameters:**
Takes the same window parameters as `polars.Expr.rolling_sum`:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `window_size` | `str` or `int` | *required* | The length of the window (number of rows or duration string). |
| `min_samples` | `int` | `1` | Minimum number of non-null observations required. |
| `weights` | `list[float]` or `None` | `None` | Optional sequence of weights. |

**Returns:**
- `Expr`: Expression computing the rolling product.

**Examples:**
```python
import polynx as plx

df = plx.DataFrame({'val': [1.0, 2.0, 3.0, 4.0]})
df.select(plx.col('val').rolling_prod(window_size=2, min_samples=1))
```

---

## Windowing with `.over()`

Polynx's string expression parser supports the `.over()` method accepting either a single column string or a list of columns:

```python
# Single grouping key
df.wc("group_mean = val.mean().over('category')")

# Multiple grouping keys
df.wc("multi_group_mean = val.mean().over(['region', 'category'])")
```

---

## Conversions

### `to_polars`

Retrieve the underlying native `polars.Expr`.

```python
expr.to_polars() -> polars.Expr
```
