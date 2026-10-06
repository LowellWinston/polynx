# Series Reference

`polynx.Series` is a transparent wrapper around `polars.Series` providing Python sequence protocol methods (`__getitem__`, `__len__`) and data conversion utilities.

```python
import polynx as plx

s = plx.Series("name", [1, 2, 3, 4])
```

---

## Sequence Protocol Methods

### `__getitem__`

Index elements or slices directly:

```python
s = plx.Series("A", [10, 20, 30])

s[0]   # 10
s[1]   # 20
s[-1]  # 30
```

---

### `__len__`

Retrieve the length of the series using standard Python `len()`:

```python
len(s)  # 3
```

---

## Interoperability & Conversions

### `to_polars`

Retrieve the underlying native `polars.Series`.

```python
s.to_polars() -> polars.Series
```

---

### `to_pandas`

Convert the series to a `pandas.Series`.

```python
s.to_pandas() -> pandas.Series
```

---

## Delegated Polars Methods

All native Polars `Series` methods (e.g., `.sum()`, `.mean()`, `.std()`, `.filter()`, `.cast()`, `.str`, `.dt`) are dynamically delegated and automatically wrap results back into `polynx.Series`.
