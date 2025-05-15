import polars as pl

class DataFrame:
    def __init__(self, data):
        self._pl = pl.DataFrame(data)

    def __getattr__(self, name):
        return getattr(self._pl, name)

    def __getitem__(self, item):
        return self._pl[item]

    def __repr__(self):
        return f"PolynxDataFrame:\n{repr(self._pl)}"

    def to_polars(self):
        return self._pl
