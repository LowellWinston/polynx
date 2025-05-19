import polars as pl
from .wrapper import wrap, unwrap


class LazyFrame:
    def __init__(self, *args, **kwargs):
        self._pl = pl.LazyFrame(*args, **kwargs)

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

    def __getitem__(self, item):
        if isinstance(item, str): # df["col"]
            return wrap(self._pl.select(item))
        elif isinstance(item, list): # df[["col1", "col2"]]
            return wrap(self._pl.select(item))
        elif isinstance(item, pl.Expr): # df[pl.col("col") > 5] → Filtering
            return wrap(self._pl.filter(item))
        else:
            raise TypeError(f"Unsupported index type: {type(item)}")

    def __repr__(self):
        return f"PolynxLazyFrame:\n{repr(self._pl)}"

    def to_polars(self):
        return self._pl

    def collect(self, *args, **kwargs):
        return DataFrame(self._pl.collect(*args, **kwargs))

