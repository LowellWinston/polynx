"""Reproducible benchmark: native Polars vs polynx string expressions vs pandas.

    python benchmarks/bench.py                 # default sizes
    python benchmarks/bench.py --sizes 1000 1000000 --repeat 30

Scenarios (per call, median of --repeat runs; each includes the filter/collect):
  native          hand-written Polars expression
  polynx (same)   the same query string every call (expression cache hit)
  polynx (loop)   the string changes every call (e.g. a threshold in a loop), so only the
                  template cache can help
  polynx (cold)   expression caching disabled: the full parse cost on every call
  pandas.query    DataFrame.query on an equivalent pandas frame
"""
import argparse
import statistics
import time

import pandas as pd
import polars as pl

import polynx as plx
from polynx import config

QUERY = "A > {t} & B in ['x', 'y'] & A * 2 < {u}"


def make_data(n):
    return {"A": list(range(n)), "B": ["x", "y", "z", "w"] * (n // 4) + ["x"] * (n % 4)}


def timeit(fn, repeat):
    fn()  # warm-up
    runs = []
    for i in range(repeat):
        t0 = time.perf_counter()
        fn(i)
        runs.append(time.perf_counter() - t0)
    return statistics.median(runs)


def bench(n, repeat):
    data = make_data(n)
    pdf, pld, plxdf = pd.DataFrame(data), pl.DataFrame(data), plx.DataFrame(data)
    hi = n // 2
    res = {}

    def native(i=0):
        t = i % 50
        pld.filter((pl.col("A") > t) & pl.col("B").is_in(["x", "y"]) & (pl.col("A") * 2 < hi))

    res["native"] = timeit(native, repeat)

    config.set_cache_mode("raw")
    plx.clear_all_expr_caches()
    same = QUERY.format(t=5, u=hi)
    res["polynx (same)"] = timeit(lambda i=0: plxdf.query(same), repeat)

    plx.clear_all_expr_caches()
    # fresh literal every call, including the warm-up call
    counter = iter(range(10**9))
    res["polynx (loop)"] = timeit(
        lambda i=0: plxdf.query(QUERY.format(t=next(counter), u=hi + next(counter))), repeat
    )

    config.set_cache_mode("none")
    res["polynx (cold)"] = timeit(lambda i=0: plxdf.query(same), repeat)
    config.set_cache_mode("raw")

    res["pandas.query"] = timeit(lambda i=0: pdf.query(same), repeat)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", type=int, nargs="+", default=[1_000, 100_000, 5_000_000])
    ap.add_argument("--repeat", type=int, default=20)
    a = ap.parse_args()

    print(f"polars {pl.__version__}, pandas {pd.__version__}, polynx {getattr(plx, '__version__', '?')}\n")
    rows = [(n, bench(n, a.repeat)) for n in a.sizes]
    names = list(rows[0][1])
    print("| rows | " + " | ".join(names) + " |")
    print("|---:|" + "---:|" * len(names))
    for n, r in rows:
        print(f"| {n:,} | " + " | ".join(f"{r[k] * 1e3:.3f} ms" for k in names) + " |")
    print("\n(median per call; lower is better)")


if __name__ == "__main__":
    main()
