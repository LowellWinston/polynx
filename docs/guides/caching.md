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

## Automatic Cache Bypass for `@var`

When an expression contains variable substitution syntax (`@var`), Polynx **automatically bypasses the cache**. This prevents stale variables from causing bugs when queries run in loops with updating variables:

```python
# Caching is automatically disabled here so @i is always re-evaluated
for i in [1, 2, 3]:
    df.query("A == @i")
```

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
