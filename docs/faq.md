# FAQ

### Why not just use Polars directly?

You can, and polynx doesn't replace it. Native Polars is a good choice when your expressions are fixed in code. polynx is shorter for quick filters and column math, and it lets an expression live in a string (a config, a notebook cell, generated code). You can mix both in the same pipeline.

### How much overhead does polynx add?

For a repeated query, essentially none: the string becomes a native Polars expression and Polars does the work. A string seen for the first time costs about 0.1 ms to parse; after that it is cached, and loops with changing values (`A > 1`, `A > 2`, ...) reuse a parsed template. See the [benchmark](https://github.com/LowellWinston/polynx#performance--coming-from-pandas) and run `benchmarks/bench.py` to measure on your own data.

### How is it different from `pl.sql_expr` / `SQLContext`?

Polars' SQL support parses faster (it is written in Rust, roughly 30 µs per expression against polynx's ~100 µs), but it uses SQL syntax. polynx follows pandas/Python syntax: `@var` variables, method chaining such as `A.mean().over('B')`, backticked column names, `case_when`, and user-defined functions.

### Does it use `eval()`? Is it safe?

Expression text is parsed by a grammar and is never passed to Python's `eval()`. The functions a string can call are limited to a small set of builtins, functions you register with `register_udf`, and names in the calling scope. It is not a sandbox: `@name` and bare function names resolve against the caller's scope, so a string can use anything the calling code can see. Don't evaluate strings from untrusted users where sensitive objects are in scope.

### Does it work with `LazyFrame`?

Yes. Every string method works on eager and lazy frames, and Polars' optimizer still sees the whole query.

### Do I have to wrap my DataFrames?

No. Besides the wrapper classes (`plx.DataFrame`, `plx.LazyFrame`), importing `polynx` registers a `.plx` namespace on native Polars objects: `pl_df.plx.query("A > 2")`.

### Which Python and Polars versions are supported?

CI runs on Python 3.9 to 3.13, and also against the minimum supported Polars (1.8) as well as the latest release.

### I found a bug or want new syntax. Where do I go?

Questions and syntax ideas belong in [Discussions](https://github.com/LowellWinston/polynx/discussions). Bugs with a reproducible example go in [Issues](https://github.com/LowellWinston/polynx/issues); please include your polynx and Polars versions.
