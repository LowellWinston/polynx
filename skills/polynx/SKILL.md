---
name: polynx
description: Use when working with Polars DataFrames and wanting Pandas/SQL-style string expressions: query/filter strings, eval/assign, multi-statement with_columns (wc), string group-by (gb), case_when, @variable substitution. Covers the polynx Python package.
---


Polynx is a string-powered expression engine on top of Polars. Use it when you want
Pandas/SQL-style string expressions (`query`, `eval`, `assign`, `wc`, `gb`) with Polars'
speed and lazy optimization. Everything else in Polars still works.

Install: `pip install polynx` (requires Python 3.9+, polars>=1.8).
Docs: https://lowellwinston.github.io/polynx/ · Source: https://github.com/LowellWinston/polynx

## Two ways to use it

```python
import polynx as plx

df = plx.DataFrame({"A": [1, 2, 3], "B": ["x", "y", None]})   # wrapper over polars.DataFrame
lf = plx.LazyFrame(...)                                        # same methods, lazy

# Or keep native Polars objects and use the registered namespace:
import polars as pl, polynx
pl.DataFrame({"A": [1, 2, 3]}).plx.query("A > 1")
```

## Core string API (works on DataFrame and LazyFrame)

| Call | Purpose |
|---|---|
| `df.query("A >= 2 & B in ['x','y']")` | filter rows |
| `df.eval("A * 2")` | return only the computed column(s) |
| `df.assign("C = A * 2")` | append computed columns |
| `df.wc("C = A * 2; D = C + 1")` | like `with_columns`; `;`-separated statements run sequentially; also accepts native `pl.Expr` |
| `df.gb("B", "S = A.sum(); M = A.mean()", with_subtotal=True)` | string group-by aggregation, optional subtotal and `All` rows |
| `df.describe(group_keys=...)` | grouped summary statistics |

Syntax notes:
- `@name` pulls a Python variable from the calling scope: `df.query("A > @threshold")`.
  Expressions containing `@` bypass the parse cache so loops see fresh values.
- Backticks quote awkward column names: ``df.query("`Score Value` > 90")``.
- Polars methods chain inside strings: `B.str.to_uppercase().str.slice(0, 2)`, `A.mean().over('B')`,
  `A.mean().over(['B','C'])`.
- Membership: `B in [...]`, `B not in [...]`. Logic: `&`, `|`, `not (...)`. Chained comparisons: `1 <= A < 4`.
- Conditionals: `case_when([c1, c2], [v1, v2], default)`, `case_when(cond, a, b)`,
  `select([...], [...], default)` (numpy.select), `where(cond, a, b)` (numpy.where).
- `mondf(beg_date, end_date)` gives months between dates. `max_horizontal(A, E)` / `min_horizontal(A, E)` work in strings.

## Convenience helpers

`dd()` dedupe (keep first, keep order) · `dsort(by)` / `asort(by)` descending/ascending sort ·
`unstack()` pivot on last two columns · `vcnt(col)` value counts · `ucnt(col)` unique count (scalar) ·
`round()`, `cum_max()` · `to_list()`, `max()`, `min()` scalar extraction · `rename([...])` rename by list ·
`size()` memory footprint · `pplot()` quick plot · `plx.merge(...)` Pandas-style merge.
Expression extension: `rolling_prod`.

## Extending

- `plx.register_udf(...)` / `plx.register_udfs_by_names(module, [names])` expose Python functions inside strings.
- `plx.clear_all_expr_caches()` clears the parsed-expression cache.

## Tips for agents

- If a string expression fails, check quoting and that column names exist; the parser follows Polars method names.
- For a full signature or docstring, run `help(plx.DataFrame.query)` etc., or see the API reference on the docs site.
- Prefer one `wc("a = ...; b = ...")` call over many chained `with_columns`.
