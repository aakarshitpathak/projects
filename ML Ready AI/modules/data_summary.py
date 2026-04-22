"""
modules/data_summary.py — MODULE 4
Generates a clean summary of the DataFrame:
  • Shape (rows × columns)
  • Column names + data types
  • Missing value counts
  • Basic descriptive statistics (describe())
"""

import pandas as pd


def get_summary(df: pd.DataFrame) -> dict:
    """
    Returns a dictionary containing all summary information
    needed to render the summary.html template.

    Keys returned:
      rows          – int
      cols          – int
      columns_info  – list of dicts {name, dtype, missing, missing_pct}
      stats         – dict-of-dicts from df.describe() (numeric columns)
      preview       – list of lists (first 5 rows as raw values)
      preview_cols  – list of column names (for table header)
    """

    # ── Basic shape ────────────────────────────────────────
    rows, cols = df.shape

    # ── Per-column info ────────────────────────────────────
    columns_info = []
    for col in df.columns:
        missing_count = int(df[col].isna().sum())
        missing_pct   = round((missing_count / rows) * 100, 1) if rows > 0 else 0.0
        columns_info.append({
            'name'        : col,
            'dtype'       : str(df[col].dtype),
            'missing'     : missing_count,
            'missing_pct' : missing_pct,
        })

    # ── Descriptive statistics (numeric columns only) ──────
    # Transpose so each column becomes a row → easier to loop in Jinja
    desc = df.describe(include='number')    # rows: count mean std min 25% 50% 75% max
    stats_dict = desc.round(3).to_dict()    # {col_name: {stat: val, ...}}

    # ── Preview (first 5 rows) ─────────────────────────────
    preview_df   = df.head(5)
    preview_cols = list(preview_df.columns)
    # Convert each row to a plain list so Jinja can iterate
    preview_rows = [list(row) for row in preview_df.values]

    return {
        'rows'         : rows,
        'cols'         : cols,
        'columns_info' : columns_info,
        'stats'        : stats_dict,
        'preview_cols' : preview_cols,
        'preview_rows' : preview_rows,
    }
