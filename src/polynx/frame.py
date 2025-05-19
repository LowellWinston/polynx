import polars as pl
from .wrapper import wrap, unwrap

class DataFrame:
    def __init__(self, *args, **kwargs):
        self._pl = pl.DataFrame(*args, **kwargs)
        self._is_wrapped = True

    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            _pl = super().__getattribute__("_pl")
            attr = getattr(_pl, name)
            if callable(attr):
                def wrapped(*args, **kwargs):
                    from polynx.wrapper import wrap, unwrap
                    return wrap(attr(*[unwrap(a) for a in args], **{k: unwrap(v) for k, v in kwargs.items()}))
                return wrapped
            return attr  
            

    def __getitem__(self, item):
        return wrap(self._pl[item])

    def __repr__(self):
        return f"PolynxDataFrame:\n{repr(self._pl)}"

    def to_polars(self):
        return self._pl
