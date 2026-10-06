# Getting Started

## Installation

### Via PyPI (Recommended)

Install Polynx via `pip`:

```bash
pip install polynx
```

### From Source

Clone the GitHub repository and install it in editable mode:

```bash
git clone https://github.com/LowellWinston/polynx.git
cd polynx
pip install -e .
```

---

## Core Concept: Drop-in Polars Wrapper

Polynx wraps Polars' `DataFrame`, `LazyFrame`, `Series`, and `Expr`. Any operation valid in Polars is valid in Polynx:

```python
import polynx as plx
import polars as pl

# Create a Polynx DataFrame
df = plx.DataFrame({
    'category': ['X', 'X', 'Y', 'Y'],
    'val1': [10, 20, 30, 40],
    'val2': [1.5, 2.5, 3.5, 4.5]
})

# Access native Polars methods directly
print(df.shape)
print(df.columns)
print(df.schema)

# Access all top-level Polars functions directly via plx
df2 = plx.concat([df, df])
```

---

## Conversions

You can convert between Polynx and native Polars or Pandas DataFrames at any time:

```python
# Convert to native Polars
native_polars_df = df.to_polars()
assert isinstance(native_polars_df, pl.DataFrame)

# Convert to Pandas
pandas_df = df.to_pandas()
```

---

## Your First Polynx Workflow

Here is a typical workflow demonstrating how Polynx streamlines common data analysis steps:

```python
import polynx as plx

# 1. Initialize data
df = plx.DataFrame({
    'user_id': [101, 102, 103, 104],
    'tier': ['silver', 'gold', 'bronze', 'silver'],
    'spend': [150.0, 450.0, 50.0, 220.0],
    'active': [True, True, False, True]
})

# 2. Filter using query with variable substitution
target_spend = 100.0
active_customers = df.query("spend >= @target_spend & active == True")

# 3. Add calculated columns using wc (with_columns)
enriched = active_customers.wc(
    "discount = case_when(spend > 300, 0.20, 0.10);"
    "net_spend = spend * (1 - discount);"
    "mean_tier_spend = spend.mean().over('tier')"
)

# 4. Aggregate with group-by and subtotal
summary = enriched.gb('tier', 'spend.sum(); net_spend.sum()', with_subtotal=True)
print(summary)
```

Proceed to the [Expression Engine Guide](guides/expressions.md) for full syntax details.
