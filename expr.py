import polars as pl

class Expr:
    def __init__(self, *args, **kwargs):
        self._pl = pl.Expr(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._pl, name)    

    def __repr__(self):
        return f"PolynxExpr:\n{repr(self._pl)}"

    def to_polars(self):
        return self._pl
