---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.1
  kernelspec:
    display_name: venv
    language: python
    name: python3
---

```python
import polynx as plx
```

- Supports all polars functions


```python
df = plx.DataFrame({
    'A':[1, 2, 3, 4], 
    'B': ['abc', 'bc', 'aaa', None], 
    'C': ['2023-01-01','2021-01-01','2009-11-01','2000-11-11'],
    'E': [1.1, 2.1, 3.5, 0]}
).wc("C.str.to_datetime(format='%Y-%m-%d',time_unit='ns').dt.date()")

df
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (4, 4)</small><table border="1" class="dataframe"><thead><tr><th>A</th><th>B</th><th>C</th><th>E</th></tr><tr><td>i64</td><td>str</td><td>date</td><td>f64</td></tr></thead><tbody><tr><td>1</td><td>&quot;abc&quot;</td><td>2023-01-01</td><td>1.1</td></tr><tr><td>2</td><td>&quot;bc&quot;</td><td>2021-01-01</td><td>2.1</td></tr><tr><td>3</td><td>&quot;aaa&quot;</td><td>2009-11-01</td><td>3.5</td></tr><tr><td>4</td><td>null</td><td>2000-11-11</td><td>0.0</td></tr></tbody></table></div>



- Pandas style query function with chaind comparison, variable substituion in string expression


```python
var1 = 1
var2 = 3
var3 = ['bc']
query_str =  "@var1 <= A < @var2 & C.dt.year() >=2020 & B in @var3"
df.query(query_str);
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (1, 4)</small><table border="1" class="dataframe"><thead><tr><th>A</th><th>B</th><th>C</th><th>E</th></tr><tr><td>i64</td><td>str</td><td>date</td><td>f64</td></tr></thead><tbody><tr><td>2</td><td>&quot;bc&quot;</td><td>2021-01-01</td><td>2.1</td></tr></tbody></table></div>



- String operation


```python
query_str = "B.str.contains('a|b')"
#query_str = " B.str.ends_with('c')"
df.query(query_str);
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (3, 4)</small><table border="1" class="dataframe"><thead><tr><th>A</th><th>B</th><th>C</th><th>E</th></tr><tr><td>i64</td><td>str</td><td>date</td><td>f64</td></tr></thead><tbody><tr><td>1</td><td>&quot;abc&quot;</td><td>2023-01-01</td><td>1.1</td></tr><tr><td>2</td><td>&quot;bc&quot;</td><td>2021-01-01</td><td>2.1</td></tr><tr><td>3</td><td>&quot;aaa&quot;</td><td>2009-11-01</td><td>3.5</td></tr></tbody></table></div>



- Year month comparison in string format


```python
var5 ='2001-01-01'
var3 = '2020-01-01'
query_str = " @var5 < C < @var3 "
df.query(query_str)
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (1, 4)</small><table border="1" class="dataframe"><thead><tr><th>A</th><th>B</th><th>C</th><th>E</th></tr><tr><td>i64</td><td>str</td><td>date</td><td>f64</td></tr></thead><tbody><tr><td>2</td><td>&quot;bc&quot;</td><td>2021-01-01</td><td>2.1</td></tr></tbody></table></div>



- `in` and `not in` 


```python
query_str = " B in ['aaa','bc']"
df.query(query_str)
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (2, 4)</small><table border="1" class="dataframe"><thead><tr><th>A</th><th>B</th><th>C</th><th>E</th></tr><tr><td>i64</td><td>str</td><td>date</td><td>f64</td></tr></thead><tbody><tr><td>2</td><td>&quot;bc&quot;</td><td>2021-01-01</td><td>2.1</td></tr><tr><td>3</td><td>&quot;aaa&quot;</td><td>2009-11-01</td><td>3.5</td></tr></tbody></table></div>



- Math calcuation


```python
query_str = " A ** 2 - E > 1"
df.query(query_str)
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (3, 4)</small><table border="1" class="dataframe"><thead><tr><th>A</th><th>B</th><th>C</th><th>E</th></tr><tr><td>i64</td><td>str</td><td>date</td><td>f64</td></tr></thead><tbody><tr><td>2</td><td>&quot;bc&quot;</td><td>2021-01-01</td><td>2.1</td></tr><tr><td>3</td><td>&quot;aaa&quot;</td><td>2009-11-01</td><td>3.5</td></tr><tr><td>4</td><td>null</td><td>2000-11-11</td><td>0.0</td></tr></tbody></table></div>



- Pandas style eval function


```python
query_str = " (A ** 2 - E)/(10-A)"
df.eval(query_str)
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (4, 1)</small><table border="1" class="dataframe"><thead><tr><th>A</th></tr><tr><td>f64</td></tr></thead><tbody><tr><td>-0.011111</td></tr><tr><td>0.2375</td></tr><tr><td>0.785714</td></tr><tr><td>2.666667</td></tr></tbody></table></div>



- negation


```python
query_str = " not (B.is_null() & A.is_not_null())"
df.query(query_str)
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (3, 4)</small><table border="1" class="dataframe"><thead><tr><th>A</th><th>B</th><th>C</th><th>E</th></tr><tr><td>i64</td><td>str</td><td>date</td><td>f64</td></tr></thead><tbody><tr><td>1</td><td>&quot;abc&quot;</td><td>2023-01-01</td><td>1.1</td></tr><tr><td>2</td><td>&quot;bc&quot;</td><td>2021-01-01</td><td>2.1</td></tr><tr><td>3</td><td>&quot;aaa&quot;</td><td>2009-11-01</td><td>3.5</td></tr></tbody></table></div>



- wc extends with_columns to support multipe statement assignments


```python
df.wc("A.sum().over('B').alias('H'); E.mean().alias('E_mean')")
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (4, 6)</small><table border="1" class="dataframe"><thead><tr><th>A</th><th>B</th><th>C</th><th>E</th><th>H</th><th>E_mean</th></tr><tr><td>i64</td><td>str</td><td>date</td><td>f64</td><td>i64</td><td>f64</td></tr></thead><tbody><tr><td>1</td><td>&quot;abc&quot;</td><td>2023-01-01</td><td>1.1</td><td>1</td><td>1.675</td></tr><tr><td>2</td><td>&quot;bc&quot;</td><td>2021-01-01</td><td>2.1</td><td>2</td><td>1.675</td></tr><tr><td>3</td><td>&quot;aaa&quot;</td><td>2009-11-01</td><td>3.5</td><td>3</td><td>1.675</td></tr><tr><td>4</td><td>null</td><td>2000-11-11</td><td>0.0</td><td>4</td><td>1.675</td></tr></tbody></table></div>



- Extend describe for group by 


```python
df.describe(group_keys='B', selected_columns=['A','E']).round()
```

- Extend group_by to work with string expressions


```python
df.gb('B', " A.sum(); E.mean()")
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (4, 3)</small><table border="1" class="dataframe"><thead><tr><th>B</th><th>A</th><th>E</th></tr><tr><td>str</td><td>f64</td><td>f64</td></tr></thead><tbody><tr><td>null</td><td>4.0</td><td>0.0</td></tr><tr><td>&quot;aaa&quot;</td><td>3.0</td><td>3.5</td></tr><tr><td>&quot;abc&quot;</td><td>1.0</td><td>1.1</td></tr><tr><td>&quot;bc&quot;</td><td>2.0</td><td>2.1</td></tr></tbody></table></div>



- Support lazyframe


```python
df.lazy().wc("E = 1").collect()
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (4, 4)</small><table border="1" class="dataframe"><thead><tr><th>A</th><th>B</th><th>C</th><th>E</th></tr><tr><td>i64</td><td>str</td><td>date</td><td>i32</td></tr></thead><tbody><tr><td>1</td><td>&quot;abc&quot;</td><td>2023-01-01</td><td>1</td></tr><tr><td>2</td><td>&quot;bc&quot;</td><td>2021-01-01</td><td>1</td></tr><tr><td>3</td><td>&quot;aaa&quot;</td><td>2009-11-01</td><td>1</td></tr><tr><td>4</td><td>null</td><td>2000-11-11</td><td>1</td></tr></tbody></table></div>


