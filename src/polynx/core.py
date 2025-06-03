from . import utils as _utils
from .expr_parser import parse_polars_expr
from .wrapper import unwrap, wrap
import polars as pl
import numpy as np
from .utils import select, where, mondf

def plx_query(self, query_str):
    """ Equivalent of query in pandas """
    df_schema = _utils.get_schema(self)
    return self.filter(parse_polars_expr(query_str, df_schema))


def plx_eval(self, query_str, mode='select'):
    """ Equivalent of eval in pandas """
    df_schema = _utils.get_schema(self)
    if isinstance(query_str, str):
        parsed_expr = parse_polars_expr(query_str, df_schema)        
    else:
        parsed_expr = [parse_polars_expr(_str, df_schema)[0] for _str in query_str]       
    if mode =='select':
        return self.select(parsed_expr)
    else:
        return self.with_columns(parsed_expr)


def plx_assign(self, query_str):
    return plx_eval(self, query_str, 'assign')


def plx_dd(self):
	return self.unique(maintain_order=True)


def plx_dsort(self, by=None):
    if by is None:
        by = _utils.get_columns(self)
    return self.sort(by, descending=True)


def plx_asort(self, by=None):
    if by is None:
        by = _utils.get_columns(self)
    return self.sort(by, descending=False)


def plx_unstack(self):    
    columns = list(_utils.get_schema(self).keys())
    if isinstance(self, _utils.LazyFrame):
        self_eager = self.collect()            
    else:
        self_eager = self
    index_cols = len(columns)-2
    return self_eager.pivot(index=columns[:index_cols], on=columns[-2], values=columns[-1], aggregate_function='first').sort(columns[:index_cols])


def plx_pplot(self, *args, **kwargs):
    """ Use Pandas Plot. Note that polars has built-in plot function using either altAir """
    if isinstance(self, _utils.LazyFrame):
        self_eager = self.collect()            
    else:
        self_eager = self
    self_pd = self_eager.to_pandas()
    index = self_eager.columns[0]
    self_pd.set_index(index).plot(*args, **kwargs)


def plx_vcnt(self, col=None):    
    if col is None:      
        col = list(_utils.get_schema(self).keys())
    result = self.group_by(col).agg(pl.count()).dsort('count')
    if isinstance(result, _utils.LazyFrame):
        result = result.collect()
    return result


def plx_ucnt(self, col=None):
    if col is None:      
        col = _utils.get_columns(self)
    self_col = self.select(pl.col(col)).unique(maintain_order=True).count()
    if isinstance(self_col, _utils.LazyFrame):
        self_col_eager = self_col.collect()            
    else:
        self_col_eager = self_col
    return self_col_eager.row(0)[0]


# Polynx version of with_columns
def plx_wc(self, *args, **kwargs):
    if kwargs:
        return self.with_columns(*args, **kwargs)

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
                results = _append(results, _utils.to_plx_expr(self, i))                
        else:
            results = _append(results, _utils.to_plx_expr(self, arg))    
    return self.with_columns(results)


# Polynx Groupby
def plx_gb(self, gp_keys, expr):
    df_schema = _utils.get_schema(self)    
    parsed_tree, cols = parse_polars_expr(query_str=expr, df_schema=df_schema, return_cols=True)
    self = self.wc(
        [pl.col(col).cast(pl.Float64) for col in cols if _utils.is_numeric_dtype(df_schema[col])]
    )
    return self.group_by(gp_keys).agg(parsed_tree).sort(gp_keys)


# Describe Groupby
def describe_groupby(self, group_keys, selected_columns, percentiles=(0.25,0.5,0.75), interpolation='nearest'):
    df = unwrap(self)
    df_schema = _utils.get_schema(df)

    if isinstance(selected_columns, str):
        selected_columns = [selected_columns]

    numeric_cols = [
        col for col in selected_columns 
        if _utils.is_numeric_dtype(df_schema[col]) and col not in group_keys
    ]

    aggs = []
    for col in numeric_cols:
        aggs.extend([
            pl.col(col).count().alias(f"{col}_count"),
            pl.col(col).null_count().alias(f"{col}_nulls"),
            pl.col(col).mean().alias(f"{col}_mean"),
            pl.col(col).std().alias(f"{col}_std"),
            pl.col(col).min().alias(f"{col}_min")] +
            [pl.col(col).quantile(q, interpolation).alias(f"{col}_{int(q*100)}%") for q in percentiles] +
            [pl.col(col).max().alias(f"{col}_max")]
        )

    result = df.group_by(group_keys).agg(aggs)
    if isinstance(result, pl.LazyFrame):
        result = result.collect()
    return wrap(result)


def plx_describe(self, percentiles=(0.25,0.5,0.75), interpolation='nearest', group_keys=None, selected_columns=None):
    if group_keys is not None:
        if selected_columns is None:            
            selected_columns = _utils.get_columns(self)
        return describe_groupby(self, group_keys, selected_columns, percentiles, interpolation)
    
    # Use built-in Polars describe
    return wrap(unwrap(self).describe(percentiles=percentiles, interpolation=interpolation))


def plx_round(self, decimal=2):
    """ Rounds all float columns in the DataFrame X decimal places """
    df_schema = _utils.get_schema(self)
    return self.with_columns(
        [pl.col(col).round(decimal) for col in _utils.get_columns(self) if _utils.is_flt_dtype(df_schema[col])]
    )


def plx_cum_max(self):
    """ Rounds all float columns in the DataFrame X decimal places """
    df_schema = _utils.get_schema(self)
    return self.with_columns(
        [pl.col(col).cum_max() for col in list(df_schema.keys()) if _utils.is_flt_dtype(df_schema[col])]
    )


def plx_to_list(self, col_name=None): 
    df = self       
    if col_name is None:
        df_columns = _utils.get_columns(df)    
        col_name = df_columns[0]
    df_earger = df.get_column(col_name)
    if isinstance(df, _utils.LazyFrame):
        df_earger = df_earger.collect()
    return df_earger.to_list()


def plx_max(self, col_name=None):
    df = self
    if col_name is None:
        df_columns = _utils.get_columns(df)  
        col_name = df_columns[0]
    df_earger = df.select(pl.col(col_name).max())
    if isinstance(df, _utils.LazyFrame):
        df_earger = df_earger.collect()
    return df_earger.item()


def plx_min(self, col_name=None):
    df = self
    if col_name is None:
        df_columns = _utils.get_columns(df)  
        col_name = df_columns[0]
    df_earger = df.select(pl.col(col_name).min())
    if isinstance(df, _utils.LazyFrame):
        df_earger = df_earger.collect()
    return df_earger.item()    

def plx_to_pandas(self):
    if isinstance(self, (_utils.DataFrame, _utils.Series)):
        return self.to_pandas()
    else:
        raise(f"It is not a polynx.DataFrame or polynx.Series object and cannot be converted to pandas!")
    

def plx_size(df, unit='mb', return_size=False):
    _size = np.round(df.estimated_size(unit),2)  
    print(f"DataFrame size: {_size} {unit.upper()}")      
    if return_size:
        return _size
    

def plx_rename(self, *args, **kwargs):
    if len(args) == 1 and isinstance(args[0], list):
        cur_cols = _utils.columns(self)
        new_cols = args[0]
        if len(cur_cols) != len(new_cols):
            raise ValueError("Length of new column names must match the number of columns in the DataFrame.")      
        for i in range(len(new_cols)):            
            self = wrap(unwrap(self).rename({cur_cols[i]: new_cols[i]}))
        #print(self.collect())
        return self
    else:
        return wrap(unwrap(self).rename(*args, **kwargs))


def plx_rolling_prod(self, *args, **kwargs):
    return self.log().rolling_sum(*args, **kwargs).exp()

