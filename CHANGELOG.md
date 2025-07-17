# Changelog

## [0.1.1] - 2025-05-20
- Initial release

## [0.1.2] - 2025-05-22
- Added select and when function to mirror np.select and np.when for string expression
- Added plx_merge, a pandas style merge for polynx
- Add size function for dataframe
- Wrap describe for groupby
- Expand rename function to work with list

## [0.1.3] - 2025-05-30
- Bugfix: Support complex variable substituion such as a very long list

## [0.1.4] - 2025-06-03
- Bugfix: plx.Series.cut error
- Feature: Assignment supports list, tuple, np.ndarray, pd.Series, pl.Series and plx.Series
- Feature: Add pl.String, pl.Struct, pl.Duration to supported datatype
- Feature: Add rolling_prod for Expr

## [0.1.5] - 2025-06-06
- Bugfix: Add deep_unwrap in io module to accomodate polars built-in functions like pl.concat, etc.
- Feature: polynx inherits all functions in the namespace of polars

## [0.1.6] - 2025-06-06
- Feature: add subtotal function to the aggregation function gb

## [0.1.7] - 2025-06-10
- Bugfix: use pl.concat instead of polynx.concat in core.py

## [0.1.8] - 2025-06-11
- Bugfix: unshadow polynx.DataFrame, polynx.LazyFrame, polynx.Expr, polynx.Series
- Bugfix: .alias() is not parsed correctly
- Bugfix: Resolve variable substitution inside arithmatic calculations

## [0.1.9] - 2025-06-12
- Bugfix: .over() to support list as argument
- Add project logo

## [0.1.10] - 2025-06-12
- Add readme_renderer[md] to enable logo display in PyPi

## [0.1.11] - 2025-0710
- Added UDF registration function to better manage UDF inside string parser
- Added cache function for string parser so that it will cache all parsed expression to avoid repeated parsing the same string expression

## [0.1.12] - 2025-0717
- Bugfix: to_pandas() now works with DataFrame, LazyFrame and Series
- Lowered dependency package requirements