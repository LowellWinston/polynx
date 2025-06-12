import polars as pl
from .wrapper import wrap, unwrap
#import inspect

_wrapped_functions = {}
polynx_types = ["DataFrame", "LazyFrame", "Series", "Expr"]
def is_public_callable(name):
    return not name.startswith("_") and callable(getattr(pl, name)) and name not in polynx_types

# Optionally skip certain functions you know aren't useful
SKIP_NAMES = {"options", "config"}

def deep_unwrap(obj):
    from collections.abc import Mapping, Sequence

    # Avoid treating strings as Sequence
    if isinstance(obj, (list, tuple)):
        return type(obj)(deep_unwrap(x) for x in obj)
    elif isinstance(obj, dict):
        return {deep_unwrap(k): deep_unwrap(v) for k, v in obj.items()}   
    elif isinstance(obj, set):
        return set(deep_unwrap(x) for x in obj)
    else:
        try:
            return unwrap(obj)
        except Exception:
            return obj


for name in dir(pl):    
    if name in SKIP_NAMES:
        continue
    if not is_public_callable(name):
        continue

    fn = getattr(pl, name)

    def make_wrapped(fn):
        def wrapped_fn(*args, **kwargs):            
            unwrapped_args = deep_unwrap(args)
            unwrapped_kwargs = deep_unwrap(kwargs)
            return wrap(fn(*unwrapped_args, **unwrapped_kwargs))
        wrapped_fn.__name__ = name
        wrapped_fn.__doc__ = getattr(fn, '__doc__', '')
        return wrapped_fn

    try:
        globals()[name] = make_wrapped(fn)
        _wrapped_functions[name] = fn
    except Exception:
        # In case wrap fails for something weird
        pass
