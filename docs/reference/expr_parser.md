# API Reference: Expression Parser & Caching

::: polynx.expr_parser
    options:
      show_root_heading: false
      members:
        - parse_polars_expr
        - register_udf
        - register_udfs_by_names
        - register_udfs_from_module
        - clear_all_expr_caches
        - get_expr_cache
        - get_expr_cache_size
        - get_expr_cache_stats
        - reset_expr_cache_stats

::: polynx.config
    options:
      show_root_heading: true
      members:
        - set_cache_mode
        - get_cache_mode
        - set_cache_max_size
        - get_cache_max_size
