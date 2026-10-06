# User Defined Functions (UDF) Reference

Register custom Python functions to call them directly inside Polynx string expressions.

---

## Functions

### `register_udf`

Register a single Python function under a given identifier name.

```python
plx.register_udf(name: str, fn: callable) -> None
```

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `name` | `str` | Name of the function as it will be called in string expressions. |
| `fn` | `callable` | Python callable. |

**Example:**
```python
import polynx as plx

def add_tax(price, tax_rate=0.08):
    return price * (1 + tax_rate)

plx.register_udf("add_tax", add_tax)

df = plx.DataFrame({'price': [100.0, 200.0]})
df.wc("total = add_tax(price, 0.10)")
```

---

### `register_udfs_by_names`

Register multiple functions from a module by their names.

```python
plx.register_udfs_by_names(module: Any, names: list[str]) -> None
```

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `module` | module object | Python module containing the functions. |
| `names` | `list[str]` | List of function names to register. |

**Example:**
```python
import math
import polynx as plx

plx.register_udfs_by_names(math, ["sin", "cos", "log10"])

df = plx.DataFrame({'x': [1.0, 10.0, 100.0]})
df.wc("log_val = log10(x)")
```

---

### `register_udfs_from_module`

Scan and register all public functions in a given module.

```python
plx.expr_parser.register_udfs_from_module(module: Any) -> None
```

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `module` | module object | Python module whose public functions will be registered. |
