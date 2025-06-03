import polars as pl

POLARS_TYPES = {
    "Int8":         pl.Int8,
    "Int16":        pl.Int16,
    "Int32":        pl.Int32,
    "Int64":        pl.Int64,
    "Float64":      pl.Float64,
    "Float32":      pl.Float32,
    "Utf8":         pl.Utf8,
    "String":       pl.String,
    "Boolean":      pl.Boolean,
    "Date":         pl.Date,
    "Datetime":     pl.Datetime,
    "Duration":     pl.Duration,
    "Time" :        pl.Time,
    "Categorical":  pl.Categorical,
    "Struct":       pl.Struct
}

PL_INT_DTYPES = {
    pl.Int8, pl.Int16, pl.Int32, pl.Int64,
    pl.UInt8, pl.UInt16, pl.UInt32
}

PL_FLT_DTYPES = {pl.Float32, pl.Float64}

PL_DATETIME_DTYPE = {pl.Datetime, pl.Date}

PL_NUMERIC_DTYPES = PL_INT_DTYPES.union(PL_FLT_DTYPES)