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

## [0.1.13] - 2025-07-24
- Updated dd to handle columns with missing value
- Added case_when to unite select and where function
- Replace list[str] with List[str] to be compatible with Python 3.8 or below
- Register max_horizontal and min_horizontal from polars

## [0.1.14] - 2025-10-02
- Bugfix: case_when and clear_all_expr_caches buf fix 
- Added clear_all_expr_caches to __init__.py

## [0.1.15] - 2025-10-02
- Features: Add non-cache mode as an option to disable cache mode and disable cache for variable substituion

## [0.1.17] - 2026-10-06
- Docs: Comprehensive update of README.md covering all engine and DataFrame features
- Docs: Full MkDocs Material documentation site with automated GitHub Pages deployment
- CI: Add GitHub Actions workflow for automated PyPI publishing with Trusted Publishing (OIDC)
- Fix: Fix package directory discovery in setup.py for src/ layout
- Features: Add __getitem__ and __len__ to Series and __len__ to DataFrame
- Maintenance: Fix pl.count() deprecation warning in plx_vcnt

## [0.1.18] - 2026-10-06
- Fix (#1): Fix operator precedence for 'in' and 'not in' when followed by logical connectors (& / |)

## [0.1.19] - 2026-10-06
- Features: Add native Polars namespace extension (.plx) on DataFrame and LazyFrame
- Fix: Fix LazyFrame compatibility in to_list(), max(), and min()
- Performance: Vectorize column renaming in plx_rename
- Performance: Optimize unique counting in plx_ucnt using native n_unique()
- Logging: Clean library logging in plx_size
- Typing: Add PEP 561 py.typed marker file
- CI: Add automated multi-version Python test workflow (3.9 - 3.12)
- CI: Automate wheel attachment to GitHub Releases on publish

## [0.1.20] - 2026-10-07
- Agents: Bundle AGENTS.md usage guide in the package; add polynx.agent_guide() and python -m polynx
- Agents: Add skills/polynx/SKILL.md, llms.txt and ARD manifest (.well-known/ard.json) on the docs site
- Metadata: Add keywords and Source/Agent Guide project URLs
