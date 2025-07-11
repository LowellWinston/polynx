CACHE_MODE = "raw"
CACHE_MAX_SIZE = 1000

def set_cache_mode(mode: str):
    global CACHE_MODE
    if mode not in {"raw", "hash", "custom_lru"}:
        raise ValueError(f"Invalid CACHE_MODE: {mode}")
    CACHE_MODE = mode

def get_cache_mode() -> str:
    return CACHE_MODE

def set_cache_max_size(size: int):
    global CACHE_MAX_SIZE
    if not isinstance(size, int) or size <= 0:
        raise ValueError("CACHE_MAX_SIZE must be a positive integer")
    CACHE_MAX_SIZE = size

def get_cache_max_size() -> int:
    return CACHE_MAX_SIZE
