# Polynx

<p align="center">
  <img src="https://github.com/LowellWinston/polynx/raw/master/assets/logo.png" width="130" alt="Polynx logo"/>
</p>

**String-powered Polars expression engine with extended DataFrame and LazyFrame utilities.**

[![PyPI version](https://img.shields.io/pypi/v/polynx.svg)](https://pypi.org/project/polynx/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## What is Polynx?

**Polynx** bridges the gap between the intuitive, concise expression syntax of Pandas/SQL and the ultra-fast execution engine of [Polars](https://pola.rs). 

With Polynx, you can write filtering criteria, multi-statement mutations, conditional branching (`case_when`, `select`, `where`), and group aggregations using simple string expressions without verbose nested method calls—all while retaining the speed, thread safety, and query planning of Polars.

---

## Key Highlights

- **String-Powered Queries**: Query DataFrames with Pandas-like syntax: `df.query("@min_val <= A < @max_val & B in @cats")`.
- **Conditional Branching (`case_when`)**: Cleanly handle multi-branch logic (`case_when([cond1, cond2], [res1, res2], default)`) without nested `.when().then().otherwise()` structures.
- **Multi-Statement Assignments (`wc`)**: Mutate and create multiple columns in a single call with semicolon-separated assignments: `df.wc("A_sum = A.sum().over('B'); E_mean = E.mean()")`.
- **First-Class LazyFrames**: Every string operation, aggregation, and filter runs seamlessly in both eager `DataFrame` and lazy `LazyFrame` contexts.
- **Extended DataFrame Utilities**: Shorthand helpers for deduplication (`dd`), sorting (`dsort`/`asort`), pivoting (`unstack`), counting (`vcnt`/`ucnt`), and summary statistics (`describe(group_keys=...)`).
- **High-Performance Caching**: Built-in LRU and hash expression caching with automatic cache-bypassing when dynamic loop variables are detected.
- **100% Polars Interoperability**: Transparent wrappers around Polars types; all Polars functions and methods are inherited and available out of the box.

---

## Quick Example

```python
import polynx as plx

# Create a DataFrame
df = plx.DataFrame({
    'A': [1, 2, 3, 4],
    'B': ['abc', 'bc', 'aaa', None],
    'C': ['2023-01-01', '2021-01-01', '2009-11-01', '2000-11-11'],
    'E': [1.1, 2.1, 3.5, 0.0]
}).wc("C = C.str.to_date('%Y-%m-%d')")

# Filter rows using string expressions with variable substitution
threshold = 2
result = df.query("A >= @threshold & B.str.contains('a|b')")

# Add conditional logic and multi-statement assignments
enhanced = result.wc(
    "Tier = case_when([A < 3, B in ['bc']], ['Bronze', 'Silver'], 'Gold');"
    "Score = A * 10 + E"
)
```

Ready to dive in? Check out the [Getting Started](getting-started.md) guide!
