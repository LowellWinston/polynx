# String DSL & Functions Reference

Polynx provides an integrated Domain Specific Language (DSL) for writing concise expressions inside `query()`, `eval()`, `assign()`, `wc()`, and `gb()`.

---

## Operators & Precedence

| Operator Category | Operators | Description | Examples |
|---|---|---|---|
| **Arithmetic** | `+`, `-`, `*`, `/`, `//`, `%`, `**` | Standard mathematical arithmetic | `A ** 2 - E / 10` |
| **Comparison** | `==`, `!=`, `<`, `<=`, `>`, `>=` | Chained comparisons | `1 <= A < 10` |
| **Membership** | `in`, `not in` | Set membership testing | `A in @var & B > 10` |
| **Boolean** | `&` (AND), `\|` (OR), `~` (NOT), `not` | Logical expressions | `(A > 1) & not B.is_null()` |
| **Negation** | `-`, `~`, `not` | Unary negation | `-A + 5`, `~flag` |
| **Assignment** | `=` | Column mutation in `wc()` | `Col = A * 2` |
| **Sequencing** | `;` | Separator for multiple statements | `A = 1; B = 2` |

---

## Built-in String Functions

### `case_when`

Unified conditional branching supporting both multi-condition and ternary logic.

```text
case_when(conds, choices, default)
```

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `conds` | `list[bool]` or `bool` | Condition expression(s). If a list is passed, checks sequentially. |
| `choices` | `list[Any]` or `Any` | Values corresponding to each condition. |
| `default` | `Any` | Value returned if no conditions match. |

**Examples:**
```python
# Multi-condition branching
df.wc("Tier = case_when([Score >= 90, Score >= 75], ['Gold', 'Silver'], 'Bronze')")

# Single-condition branching (ternary)
df.wc("Flag = case_when(Score > 50, 'Pass', 'Fail')")
```

---

### `select`

Multi-condition branching mirroring `numpy.select`.

```text
select(conds, choices, default)
```

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `conds` | `list[bool]` | List of boolean condition expressions. |
| `choices` | `list[Any]` | List of choices corresponding to each condition. |
| `default` | `Any` | Default fallback value. |

**Examples:**
```python
df.wc("Category = select([A == 1, A == 2], ['First', 'Second'], 'Other')")
```

---

### `where`

Single-condition branching mirroring `numpy.where`.

```text
where(cond, choice, default)
```

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `cond` | `bool` | Condition expression. |
| `choice` | `Any` | Value returned when `cond` is true. |
| `default` | `Any` | Value returned when `cond` is false. |

**Examples:**
```python
df.wc("Status = where(A >= 10, 'High', 'Low')")
```

---

### `mondf`

Calculates the difference in calendar months between two date or datetime columns.

```text
mondf(beg_date, end_date)
```

**Formula:**
$$\text{mondf} = (\text{end\_date.year} - \text{beg\_date.year}) \times 12 + (\text{end\_date.month} - \text{beg\_date.month})$$

**Examples:**
```python
df.wc("Month_Lag = mondf(Date_Col, Date_Col.shift())")
```

---

### `max_horizontal`

Computes the row-wise maximum across multiple column expressions:

```python
df.wc("Row_Max = max_horizontal(A, B, C)")
```

---

### `min_horizontal`

Computes the row-wise minimum across multiple column expressions:

```python
df.wc("Row_Min = min_horizontal(A, B, C)")
```

---

## Variable Substitution (`@var`)

Prefixing an identifier with `@` dynamically retrieves variables from the executing Python environment.

```python
target_id = 42
categories = ['A', 'B']
cutoff_date = '2022-01-01'

df.query("ID == @target_id & Cat in @categories & Date > @cutoff_date")
```

### Supported Variable Types:
- **Scalars**: Integers, floats, strings, booleans, dates.
- **Iterables**: Lists, tuples, sets.
- **Arrays & Series**: NumPy arrays, Pandas Series, Polars Series.

---

## Identifier Escaping (Backticks)

Column names that contain whitespace, hyphens, or special symbols can be enclosed in backticks (`` ` ``):

```python
df.query("`Sales Volume` > 1000 & `Customer-ID` == 'C10'")
```

---

## Polars Data Types in Strings

Reference Polars data types directly within string expressions:

| Literal in String | Mapped Polars Type |
|---|---|
| `pl.Int8`, `pl.Int16`, `pl.Int32`, `pl.Int64` | `pl.Int8`, `pl.Int16`, `pl.Int32`, `pl.Int64` |
| `pl.Float32`, `pl.Float64` | `pl.Float32`, `pl.Float64` |
| `pl.String`, `pl.Utf8` | `pl.String`, `pl.Utf8` |
| `pl.Boolean` | `pl.Boolean` |
| `pl.Date`, `pl.Datetime`, `pl.Duration`, `pl.Time` | Date/time types |
| `pl.Categorical`, `pl.Struct` | `pl.Categorical`, `pl.Struct` |

**Example:**
```python
df.wc("C_date = C.cast(pl.Date)")
```
