from .utils import *
from .constant import *
from .expr_parser import parse_polars_expr


def plx_query(self, query_str):
    """ Equivalent of query in pandas """
    df_schema = get_schema(self)
    return self._pl.filter(parse_polars_expr(query_str, df_schema))


def plx_eval(self, query_str, mode='select'):
    """ Equivalent of eval in pandas """
    df_schema = get_schema(self)
    if isinstance(query_str, str):
        parsed_expr = parse_polars_expr(query_str, df_schema)
        #print(parsed_expr)
    else:
        parsed_expr = [parse_polars_expr(_str, df_schema)[0] for _str in query_str]
        #[print(i) for i in parsed_expr]
    if mode =='select':
        return self._pl.select(parsed_expr)
    else:
        return self._pl.with_columns(parsed_expr)


def plx_assign(self, query_str):
    return pl_eval(self, query_str, 'assign')


def plx_dd(self):
	return self._pl.unique(maintain_order=True)


def plx_dsort(self, by=None):
    if by is None:
        by = list(get_schema(self).keys())
    return self._pl.sort(by, descending=True)


def plx_asort(self, by=None):
    if by is None:
        by = list(get_schema(self).keys())
    return self._pl.sort(by, descending=False)


def plx_unstack(self):    
    columns = list(get_schema(self).keys())
    if isinstance(self, LazyFrame):
        self_eager = self._pl.collect()            
    else:
        self_eager = self
    index_cols = len(columns)-2
    return self_eager.pivot(index=columns[:index_cols], on=columns[-2], values=columns[-1], aggregate_function='first').sort(columns[:index_cols])


def plx_plot(self, *args, **kwargs):
    """ Use Pandas Plot. Note that polars has built-in plot function using either altAir """
    if isinstance(self, LazyFrame):
        self_eager = self._pl.collect()            
    else:
        self_eager = self
    self_pd = self_eager.to_pandas()
    index = self_eager.columns[0]
    self_pd.set_index(index).plot(*args, **kwargs)


def plx_vcnt(self, col=None):
    if col is None:      
        col = list(get_schema(self).keys())
    result = self._pl.group_by(col).agg(pl.count()).dsort('count')
    if isinstance(result, LazyFrame):
        result = result.collect()
    return result


def plx_ucnt(self, col=None):
    if col is None:      
        col = list(get_schema(self).keys())  
    self_col = self._pl.select(pl.col(col)).unique(maintain_order=True).count()
    if isinstance(self_col, LazyFrame):
        self_col_eager = self_col.collect()            
    else:
        self_col_eager = self_col
    return self_col_eager.row(0)[0]


def plx_rolling_prod(expr, *args, **kwargs):
    return expr.log().rolling_sum(*args, **kwargs).exp()


def plx_query(self, query_str):
    """ Equivalent of query in pandas """
    df_schema = get_schema(self)
    return self._pl.filter(parse_polars_expr(query_str, df_schema))


def plx_eval(self, query_str, mode='select'):
    """ Equivalent of eval in pandas """
    df_schema = get_schema(self)
    if isinstance(query_str, str):
        parsed_expr = parse_polars_expr(query_str, df_schema)
        #print(parsed_expr)
    else:
        parsed_expr = [parse_polars_expr(_str, df_schema)[0] for _str in query_str]
        #[print(i) for i in parsed_expr]
    if mode =='select':
        return self._pl.select(parsed_expr)
    else:
        return self._pl.with_columns(parsed_expr)


# Polynx version of with_columns
def plx_wc(self, *args, **kwargs):
    if kwargs:
        return self._pl.with_columns(*args, **kwargs)

    def _append(_list, _expr):
        if isinstance(_expr, list) or isinstance(_expr, tuple):
            return _list + _expr
        else:
            _list.append(_expr)
            return _list
   
    results = []    
    for arg in args:
        if isinstance(arg, list) or isinstance(arg, tuple):
            for i in arg:
                results = _append(results, to_plx_expr(self, i))                
        else:
            results = _append(results, to_plx_expr(self, arg))    
    return self._pl.with_columns(results)


# Polynx Groupby
def plx_agg(self, gp_keys, expr):
    df_schema = get_schema(self)    
    parsed_tree, cols = parse_polars_expr(query_str=expr, df_schema=df_schema, return_cols=True)
    self = self._pl.wc(
        [pl.col(col).cast(pl.Float64) for col in cols if is_numeric_dtype(df_schema[col])]
    )
    return self._pl.group_by(gp_keys).agg(parsed_tree).sort(gp_keys)


# Describe Series
def describe_series(series) -> DataFrame:  
    series_eager = series
    if isinstance(series, LazyFrame):
        series_eager = series.collect()

    non_null = series_eager.drop_nulls()
    if non_null.is_empty():
        values = [0, series_eager.len()] + [None] * 7
    if non_null.dtype in [pl.Utf8, pl.Categorical, pl.Boolean]:
        _top, _freq = non_null.value_counts()
        values = [
            non_null.len(),
            series.null_count(),
            non_null.unique().count(),  # unique
            non_null.value_counts(sort=True).row(0)[0],  # top
            non_null.value_counts(sort=True).row(0)[1] # freq            
        ]
        stats = ["count", "nulls", "unique", "top", "freq"]    
    else:
        try:
            _std = non_null.std()                  
        except:
            _std = None            
           
        stats = ["count", "nulls", "mean", 'std', "min", "25%", "50%", "75%", "max"]        
        if is_datetime_dtype(non_null.dtype):
            qtl_25 = non_null.cast(pl.Int32).quantile(0.25, "nearest")
            qtl_75 = non_null.cast(pl.Int32).quantile(0.75, "nearest")
        else:
            qtl_25 = non_null.quantile(0.25, "nearest")
            qtl_75 = non_null.quantile(0.75, "nearest")
       
        stats_list = [
            non_null.mean(),
            _std,
            non_null.min(),
            qtl_25,
            non_null.median(),
            qtl_75,
            non_null.max()  
        ]
       
        def to_date_fmt(x):
            if x is None:
                return x
            return pl.Series([x]).cast(pl.Date)[0].strftime("%Y-%m-%d")

        if is_datetime_dtype(non_null.dtype):
            stats_list = [to_date_fmt(i) for i in stats_list]

        values = [non_null.len(),series.null_count()] + stats_list
    return DataFrame({'stats': stats, non_null.name : values}, strict=False)


# Decribe DataFrame or LazyFrame
def describe_frame(df) -> DataFrame:
    df_eager = df
    if isinstance(df, LazyFrame):
        df_eager = df.collect()  

    df_num = DataFrame()
    df_other = DataFrame()

    def merge_stats(df1, df2):
        if df1.is_empty():
            return df2
        else:
            return df1.join(df2, on="stats")

    for col, dtype in zip(df_eager.columns, df_eager.dtypes):
        if dtype in [pl.Utf8, pl.Categorical, pl.Boolean]:
            df_other = merge_stats(df_other, describe_series(df_eager[col]))
        else:
            df_num = merge_stats(df_num, describe_series(df_eager[col]))        
   
    if df_other.is_empty():
        if ~df_num.is_empty():          
            return df_num
    elif df_num.is_empty():
        return df_str
    return df_num, df_other


# Describe Groupby
def describe_groupby(df, group_keys, selected_columns):  
    
    df_schema = get_schema(df)
    if isinstance(selected_columns, str):
        selected_columns = [selected_columns]
    numeric_cols = [
        col for col in selected_columns 
        if is_numeric_dtype(df_schema[col]) and col not in group_keys
    ]

    aggs = []
    for col in numeric_cols:
        aggs.extend([
            pl.col(col).count().alias("count"),
            pl.col(col).null_count().alias("nulls"),
            pl.col(col).mean().alias("mean"),
            pl.col(col).std().alias("std"),
            pl.col(col).min().alias("min"),
            pl.col(col).quantile(0.25, "nearest").alias("25%"),
            pl.col(col).median().alias("50%"),
            pl.col(col).quantile(0.75, "nearest").alias("75%"),
            pl.col(col).max().alias("max"),
        ])

    result = df.group_by(group_keys).agg(aggs)
    if isinstance(result, LazyFrame):
        result = result.collect()
    return result


# Generic describe handler
def plx_describe(obj, group_keys=None, selected_columns=None):
    if group_keys is not None:
        return describe_groupby(obj, group_keys, selected_columns)
       
    if isinstance(obj, pl.Series):
        return describe_series(obj)
   
    elif isinstance(obj, (DataFrame, LazyFrame)):
        return describe_frame(obj)

    else:
        raise TypeError("Unsupported type. Must be Series, DataFrame, Expr, or GroupBy.")


def plx_round(self, decimal=2):
    """ Rounds all float columns in the DataFrame X decimal places """
    df_schema = get_schema(self)
    return self._pl.with_columns(
        [pl.col(col).round(decimal) for col in list(df_schema.keys()) if is_flt_dtype(df_schema[col])]
    )


def plx_cum_max(self):
    """ Rounds all float columns in the DataFrame X decimal places """
    df_schema = get_schema(self)
    return self._pl.with_columns(
        [pl.col(col).cum_max() for col in list(df_schema.keys()) if is_flt_dtype(df_schema[col])]
    )


def plx_to_list(df, col_name=None):        
    if col_name is None:
        df_columns = columns(df)    
        col_name = df_columns[0]
    df_earger = df.get_column(col_name)
    if isinstance(df, LazyFrame):
        df_earger = df_earger.collect()
    return df_earger.to_list()


def plx_max(df, col_name=None):
    if col_name is None:
        df_columns = columns(df)  
        col_name = df_columns[0]
    df_earger = df.select(pl.col(col_name).max())
    if isinstance(df, LazyFrame):
        df_earger = df_earger.collect()
    return df_earger.item()


def plx_min(df, col_name=None):
    if col_name is None:
        df_columns = columns(df)  
        col_name = df_columns[0]
    df_earger = df.select(pl.col(col_name).min())
    if isinstance(df, LazyFrame):
        df_earger = df_earger.collect()
    return df_earger.item()    
