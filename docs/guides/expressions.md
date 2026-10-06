# Expression Engine

Polynx includes an AST-based string expression parser built on [Lark](https://github.com/lark-parser/lark) that parses string statements into native Polars expression trees.

---

## Row Filtering with `query()`

The `.query()` method provides an intuitive, high-level syntax for row filtering:

```python
import polynx as plx

df = plx.DataFrame({
    'A': [1, 2, 3, 4],
    'B': ['abc', 'bc', 'aaa', None],
    'C': ['2023-01-01', '2021-01-01', '2009-11-01', '2000-11-11'],
    'E': [1.1, 2.1, 3.5, 0.0]
}).wc("C = C.str.to_date('%Y-%m-%d')")
```

### Chained Comparisons
```python
df.query("1 <= A < 4")
df.query("'2001-01-01' < C < '2022-01-01'")
```

### Logical Operators and Negation
Use `&` (AND), `|` (OR), `~` (Bitwise NOT), or the keyword `not`:
```python
df.query("A > 1 & E < 3.0")
df.query("not (B.is_null() & A.is_not_null())")
```

### Set Membership (`in` and `not in`)
```python
df.query("B in ['aaa', 'bc']")
df.query("B not in ['abc']")
```

### String Operations
```python
df.query("B.str.contains('a|b')")
df.query("B.str.ends_with('c')")
df.query("B.str.starts_with('a')")
```

### Arithmetic Filtering
```python
df.query("A ** 2 - E > 1")
```

---

## Variable Substitution (`@var`)

Prefixing a variable with `@` dynamically pulls its value from the surrounding Python scope:

```python
low_bound = 1
high_bound = 3
target_categories = ['bc', 'aaa']

df.query("@low_bound <= A < @high_bound & B in @target_categories")
```

Supported variable types include:
- Scalars: numbers, strings, booleans, dates
- Sequences: lists, tuples, numpy arrays, pandas Series, polars Series

### Safety in Loops
Polynx automatically bypasses expression caching whenever `@` is detected in the query string, ensuring that loop iterations with changing variables execute accurately:

```python
results = []
for val in [1, 2, 3]:
    sub_df = df.query("A == @val")
    results.append(sub_df)
```

---

## Multi-Statement Assignments with `wc()`

The `.wc()` (shorthand for `with_columns`) method allows sequential column assignments separated by semicolons (`;`):

```python
df_enriched = df.wc(
    "A_sum = A.sum().over('B');"
    "E_mean = E.mean();"
    "Normalized_E = E / E_mean"
)
```

You can also mix string expressions and native Polars expressions:
```python
import polars as pl

df_enriched = df.wc(
    "Flag = A > 2",
    pl.col("E") * 10
)
```

---

## Expression Evaluation: `eval()` and `assign()`

- **`df.eval(expr_str, mode='select')`**: Evaluates the expression and returns only the calculated column(s).
- **`df.assign(expr_str)`**: Evaluates the expression and returns the entire DataFrame with the new columns appended.

```python
# Returns single column DataFrame with result
df.eval("(A ** 2 - E) / (10 - A)")

# Appends new column to DataFrame
df.assign("Result = (A ** 2 - E) / (10 - A)")
```

---

## Conditional Branching

Polynx provides built-in conditional logic functions inside string expressions:

### `case_when(conds, choices, default)`
A unified conditional function that supports both multi-condition and single-condition branching:

```python
# Multi-condition: pass lists of conditions and choices
df.wc("Tier = case_when([A < 2, B in ['bc']], ['Bronze', 'Silver'], 'Gold')")

# Single-condition: pass single condition and choice
df.wc("High_Flag = case_when(A > 2, 1, 0)")
```

### `select(conds, choices, default)`
Mirrors `numpy.select` for multi-condition branching:

```python
df.wc("Category = select([A == 1, A == 2], ['First', 'Second'], 'Other')")
```

### `where(cond, choice, default)`
Mirrors `numpy.where` for ternary branching:

```python
df.wc("Status = where(A >= 3, 'High', 'Low')")
```

---

## Date Arithmetic: `mondf()`

Calculate the number of elapsed months between two date/datetime columns:

```python
df.wc("month_gap = mondf(C, C.shift())")
```

Calculated via: `(end_date.year - beg_date.year) * 12 + end_date.month - beg_date.month`.

---

## Horizontal Aggregations

Polars' horizontal aggregations are available in string expressions:

```python
df.wc(
    "row_max = max_horizontal(A, E);"
    "row_min = min_horizontal(A, E)"
)
```

---

## Window Functions with `.over()`

Compute windowed calculations over one or more grouping keys:

```python
# Single key
df.wc("B_avg = A.mean().over('B')")

# Multiple keys
df.wc("Multi_avg = A.mean().over(['B', 'C'])")
```

---

## Column Names with Spaces (Backticks)

Wrap column identifiers containing spaces, dashes, or special characters in backticks (`` ` ``):

```python
df_space = plx.DataFrame({"Total Revenue": [100, 200], "Customer ID": [1, 2]})
df_space.query("`Total Revenue` > 150 & `Customer ID` == 2")
```

---

## Custom UDF Registration

Register custom Python functions to invoke them inside string expressions:

```python
import polynx as plx

def square_plus_c(x, c=1):
    return x ** 2 + c

# Register function
plx.register_udf("square_plus_c", square_plus_c)

# Use in string expression
df.wc("Custom_Calc = square_plus_c(A, 5)")
```

You can also register functions by name from an existing module:

```python
import math
plx.register_udfs_by_names(math, ['sin', 'cos', 'sqrt'])
```
