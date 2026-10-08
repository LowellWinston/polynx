# Caching & Performance

Parsing string expressions involves generating an Abstract Syntax Tree (AST) through Lark. For applications running repetitive transformations or building pipelines across thousands of partitions, repeated parsing can introduce unnecessary latency.

Polynx includes an internal expression caching subsystem to eliminate parsing overhead.

---

## Cache Modes

Polynx provides four caching backends:

| Mode | Description | Best For |
|---|---|---|
| `"raw"` (default) | Standard dictionary keyed by raw query string | Typical analytical scripts |
| `"hash"` | Dictionary keyed by SHA1 hash of query string | Long or complex queries |
| `"custom_lru"` | Fixed-size LRU cache | Memory-constrained or long-running servers |
| `"none"` | Disables caching completely | Debugging or testing |

### Configuring the Cache

```python
import polynx as plx

# Set caching mode
plx.config.set_cache_mode("custom_lru")

# Configure capacity (for custom_lru)
plx.config.set_cache_max_size(2000)

# Check active settings
mode = plx.config.get_cache_mode()
max_size = plx.config.get_cache_max_size()
```

---

## `@var` and Changing Values

When an expression contains variable substitution syntax (`@var`), Polynx skips the exact-string result cache, so a changed variable is never served stale:

```python
for i in [1, 2, 3]:
    df.query("A == @i")   # @i is re-read on every call
```

Polynx also keeps a **template cache**: literals (numbers and quoted strings) are stripped from the expression, the parse tree for that shape is compiled once, and only the literal values are bound per call. Loops such as `A > 1`, `A > 2`, ... and `@var` queries therefore avoid re-parsing even though no two strings are identical. Setting the cache mode to `"none"` disables it.

---

## Cache Diagnostics & Maintenance

Inspect cache state and clear memory when necessary:

```python
import polynx as plx

# Inspect cache items
cache_contents = plx.expr_parser.get_expr_cache()

# Inspect size
current_size = plx.expr_parser.get_expr_cache_size()

# Inspect hit/miss statistics
stats = plx.expr_parser.get_expr_cache_stats()
print(f"Hits: {stats['hit']}, Misses: {stats['miss']}")

# Reset cache and metrics
plx.clear_all_expr_caches()
plx.expr_parser.reset_expr_cache_stats()
```
