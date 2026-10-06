# Configuration & Cache Reference

Polynx provides global configuration settings and cache management tools in `polynx.config` and `polynx.expr_parser`.

---

## Configuration Functions

### `set_cache_mode`

Configure the caching backend used by the string expression engine.

```python
plx.config.set_cache_mode(mode: str) -> None
```

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `mode` | `str` | Caching mode: `"raw"`, `"hash"`, `"custom_lru"`, or `"none"`. |

**Modes:**
- `"raw"`: In-memory dictionary indexed by raw query string.
- `"hash"`: SHA1 hashed cache for query strings.
- `"custom_lru"`: Fixed-capacity LRU cache.
- `"none"`: Disables caching completely.

---

### `get_cache_mode`

Retrieve the current active caching mode.

```python
plx.config.get_cache_mode() -> str
```

---

### `set_cache_max_size`

Configure maximum cache size for caching backends.

```python
plx.config.set_cache_max_size(size: int) -> None
```

---

### `get_cache_max_size`

Retrieve current maximum cache size setting.

```python
plx.config.get_cache_max_size() -> int
```

---

## Cache Diagnostics & Management

### `clear_all_expr_caches`

Clear all in-memory expression caches across all backends.

```python
plx.clear_all_expr_caches() -> None
```

---

### `get_expr_cache`

Retrieve the dictionary representation of the currently active cache.

```python
plx.expr_parser.get_expr_cache() -> dict
```

---

### `get_expr_cache_size`

Retrieve the number of items stored in the current cache.

```python
plx.expr_parser.get_expr_cache_size() -> int
```

---

### `get_expr_cache_stats`

Retrieve a dictionary containing cache hit and miss counts.

```python
plx.expr_parser.get_expr_cache_stats() -> dict[str, int]
# Returns: {'hit': int, 'miss': int}
```

---

### `reset_expr_cache_stats`

Reset hit and miss counters back to zero.

```python
plx.expr_parser.reset_expr_cache_stats() -> None
```
