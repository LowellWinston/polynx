import polars as pl

class LazyFrame:
    def __init__(self, *args, **kwargs):
        self._pl = pl.LazyFrame(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._pl, name)

    def __getitem__(self, item):
        if isinstance(item, str): # df["col"]
            return self._pl.select(item)
        elif isinstance(item, list): # df[["col1", "col2"]]
            return self._pl.select(item)
        elif isinstance(item, pl.Expr): # df[pl.col("col") > 5] → Filtering
            return self._pl.filter(item)
        else:
            raise TypeError(f"Unsupported index type: {type(item)}")

    def __repr__(self):
        return f"PolynxLazyFrame:\n{repr(self._pl)}"

    def to_polars(self):
        return self._pl
