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