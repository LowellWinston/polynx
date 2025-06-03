import polars as pl
from .wrapper import wrap, unwrap

class Expr:
    def __init__(self, *args, **kwargs):
        self._pl = pl.Expr(*args, **kwargs)
        self._is_wrapped = True

    def __getattr__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            _pl = super().__getattribute__("_pl")
            attr = getattr(_pl, name)
            if callable(attr):
                def wrapped(*args, **kwargs):
                    from .wrapper import wrap, unwrap
                    return wrap(attr(*[unwrap(a) for a in args], **{k: unwrap(v) for k, v in kwargs.items()}))
                return wrapped
            return attr  

    def __repr__(self):
        return f"PolynxExpr:\n{repr(self._pl)}"

    def to_polars(self):
        return self._pl
