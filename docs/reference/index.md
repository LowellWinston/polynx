# API Reference

Welcome to the **Polynx API reference**. This section contains detailed documentation of all classes, methods, and functions provided by Polynx.

---

## Reference Sections

<div class="grid cards" markdown>

-   :material-table: __[DataFrame](dataframe.md)__

    ---

    String querying, multi-statement assignments, group aggregations, sorting, and statistical utilities.

-   :material-timer-sand: __[LazyFrame](lazyframe.md)__

    ---

    Deferred query execution, lazy string expressions, lazy column indexing, and query collection.

-   :material-format-list-numbered: __[Series](series.md)__

    ---

    Polars Series wrapper with sequence indexing, length operations, and data export.

-   :material-code-parentheses: __[Expressions (Expr)](expr.md)__

    ---

    Window aggregations, rolling product calculation, and method chaining.

-   :material-code-tags: __[String DSL Functions](dsl.md)__

    ---

    Functions callable within string expressions: `case_when`, `select`, `where`, `mondf`, horizontal operations, and `@var`.

-   :material-swap-horizontal: __[Input / Output & Merge](io.md)__

    ---

    Pandas-style `plx.merge()`, top-level Polars functions (`concat`, `read_csv`, `read_parquet`), and unwrapping.

-   :material-tune: __[Configuration & Cache](config.md)__

    ---

    Cache modes (`raw`, `hash`, `custom_lru`, `none`), capacity management, and diagnostic metrics.

-   :material-function: __[User Defined Functions (UDF)](udf.md)__

    ---

    Custom Python function registration for invocation inside string expressions.

</div>

---

## Quick Reference Table

| Function / Method | Category | Description |
|---|---|---|
| [`df.query(query_str)`](dataframe.md#query) | DataFrame | Filter rows using string expressions with variable substitution |
| [`df.eval(query_str, mode)`](dataframe.md#eval) | DataFrame | Evaluate mathematical or string expressions returning calculated columns |
| [`df.assign(query_str)`](dataframe.md#assign) | DataFrame | Append calculated columns evaluated from string expressions |
| [`df.wc(*args, **kwargs)`](dataframe.md#wc) | DataFrame | Extended `with_columns` supporting multi-statement assignment strings |
| [`df.gb(gp_keys, expr, with_subtotal)`](dataframe.md#gb) | DataFrame | Group by with string aggregation expressions and optional subtotals |
| [`df.describe(group_keys, ...)`](dataframe.md#describe) | DataFrame | Extended descriptive statistics supporting group keys |
| [`df.dd()`](dataframe.md#dd) | DataFrame | Deduplicate rows keeping first occurrence and maintaining order |
| [`df.dsort(by)`](dataframe.md#dsort) | DataFrame | Sort rows in descending order |
| [`df.asort(by)`](dataframe.md#asort) | DataFrame | Sort rows in ascending order |
| [`df.unstack()`](dataframe.md#unstack) | DataFrame | Pivot DataFrame using last two columns as keys and values |
| [`df.vcnt(col)`](dataframe.md#vcnt) | DataFrame | Value counts grouped by column(s), sorted descending |
| [`df.ucnt(col)`](dataframe.md#ucnt) | DataFrame | Total distinct / unique row count as a scalar integer |
| [`df.round(decimal)`](dataframe.md#round) | DataFrame | Round all floating-point columns to specified decimal places |
| [`df.cum_max()`](dataframe.md#cum_max) | DataFrame | Cumulative maximum across all floating-point columns |
| [`df.to_list(col_name)`](dataframe.md#to_list) | DataFrame | Extract column values directly as a Python list |
| [`df.max(col_name)`](dataframe.md#max) | DataFrame | Extract scalar maximum value from a column |
| [`df.min(col_name)`](dataframe.md#min) | DataFrame | Extract scalar minimum value from a column |
| [`df.size(unit, return_size)`](dataframe.md#size) | DataFrame | Inspect and report estimated memory footprint |
| [`df.rename(new_cols)`](dataframe.md#rename) | DataFrame | Rename columns using either a dictionary mapping or a list of new names |
| [`df.pplot(*args, **kwargs)`](dataframe.md#pplot) | DataFrame | Quick plotting via Pandas plotting API |
| [`df.to_polars()`](dataframe.md#to_polars) | Interop | Return native `polars.DataFrame` |
| [`df.to_pandas()`](dataframe.md#to_pandas) | Interop | Return native `pandas.DataFrame` |
| [`expr.rolling_prod(...)`](expr.md#rolling_prod) | Expr | Rolling window product via log-sum-exp |
| [`plx.merge(left, right, ...)`](io.md#merge) | Functions | Pandas-style DataFrame join with automatic overlapping column suffixes |
| [`case_when(conds, choices, default)`](dsl.md#case_when) | String DSL | Conditional branching supporting multi-condition lists or ternary pairs |
| [`select(conds, choices, default)`](dsl.md#select) | String DSL | Multi-condition branching mirroring `numpy.select` |
| [`where(cond, choice, default)`](dsl.md#where) | String DSL | Ternary condition branching mirroring `numpy.where` |
| [`mondf(beg_date, end_date)`](dsl.md#mondf) | String DSL | Calculate difference in months between two date/datetime columns |
| [`max_horizontal(...)`](dsl.md#max_horizontal) | String DSL | Compute row-wise maximum across columns |
| [`min_horizontal(...)`](dsl.md#min_horizontal) | String DSL | Compute row-wise minimum across columns |
| [`plx.register_udf(name, fn)`](udf.md#register_udf) | UDF | Register Python function for use inside string expressions |
| [`plx.config.set_cache_mode(mode)`](config.md#set_cache_mode) | Config | Configure expression caching backend (`raw`, `hash`, `custom_lru`, `none`) |
| [`plx.clear_all_expr_caches()`](config.md#clear_all_expr_caches) | Config | Clear all internal expression caches |
