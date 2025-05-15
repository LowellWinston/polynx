import polars as pl

class Series:
    def __init__(self, *args, **kwargs):
        self._pl = pl.Series(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._pl, name)

    def __repr__(self):
        return f"PolynxSeries:\n{repr(self._pl)}"
    
    def to_polars(self):
        return self._pl
