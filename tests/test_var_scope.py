import polynx as plx

threshold = 5  # module level: must lose to any function-local value


def _inner(df):
    threshold = 1
    return df.query("A > @threshold")["A"].to_list()


def _outer(df):
    threshold = 9
    return _inner(df)


def test_at_var_innermost_scope_wins():
    df = plx.DataFrame({"A": [0, 1, 2, 3]})
    assert _inner(df) == [2, 3]
    assert _outer(df) == [2, 3]


def test_at_var_falls_back_to_outer_scope():
    df = plx.DataFrame({"A": [0, 5, 6, 7]})
    assert df.query("A > @threshold")["A"].to_list() == [6, 7]
