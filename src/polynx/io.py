import polars as pl
from .wrapper import wrap
import types
import inspect

_wrapped_functions = {}

def is_public_function(name):
    return not name.startswith("_") and isinstance(getattr(pl, name), types.FunctionType)

# Optionally skip certain functions you know aren't useful
SKIP_NAMES = {"options", "config"}

for name in dir(pl):
    if name in SKIP_NAMES:
        continue
    if not is_public_function(name):
        continue

    fn = getattr(pl, name)

    # Use the signature to ensure it returns something wrap-able
    sig = inspect.signature(fn)

    # Only include if it's likely to return a Polars object
    # (We'll wrap anyway, and let wrap() handle fallback)
    def make_wrapped(fn):
        def wrapped_fn(*args, **kwargs):
            return wrap(fn(*args, **kwargs))
        wrapped_fn.__name__ = fn.__name__
        wrapped_fn.__doc__ = fn.__doc__
        return wrapped_fn

    try:
        globals()[name] = make_wrapped(fn)
        _wrapped_functions[name] = fn
    except Exception:
        # In case wrap fails for something weird
        pass
