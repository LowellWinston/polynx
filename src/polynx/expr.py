import polars as pl
from .wrapper import wrap, unwrap

class Expr:
    def __init__(self, *args, **kwargs):
        self._pl = pl.Expr(*args, **kwargs)

    def __getattr__(self, name):
        attr = getattr(self._pl, name)

        if callable(attr):
            def wrapped(*args, **kwargs):
                args = [unwrap(a) for a in args]
                kwargs = {k: unwrap(v) for k, v in kwargs.items()}
                result = attr(*args, **kwargs)
                return wrap(result)
            return wrapped

        return attr  

    def __repr__(self):
        return f"PolynxExpr:\n{repr(self._pl)}"

    def to_polars(self):
        return self._pl
