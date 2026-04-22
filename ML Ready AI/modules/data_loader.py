"""
modules/data_loader.py — MODULE 3
Reads the uploaded file into a Pandas DataFrame.
Supports: CSV, Excel (.xlsx/.xls), JSON, XML, HTML
"""

import pandas as pd


# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json', 'xml', 'html', 'htm'}


def allowed_file(filename: str) -> bool:
    """
    Check if the uploaded filename has an allowed extension.
    Returns True if allowed, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_dataframe(filepath: str) -> pd.DataFrame:
    """
    Read a file from 'filepath' and return a Pandas DataFrame.

    Supported formats:
      .csv          → pd.read_csv()
      .xlsx / .xls  → pd.read_excel()   (needs openpyxl / xlrd)
      .json         → pd.read_json()
      .xml          → pd.read_xml()      (needs lxml)
      .html / .htm  → pd.read_html()[0]  (returns a list; we take first table)

    Raises:
      ValueError   — if the extension is not supported
      Exception    — passes through Pandas parse errors
    """
    ext = filepath.rsplit('.', 1)[1].lower()

    if ext == 'csv':
        df = pd.read_csv(filepath)

    elif ext in ('xlsx', 'xls'):
        df = pd.read_excel(filepath)

    elif ext == 'json':
        df = pd.read_json(filepath)

    elif ext == 'xml':
        df = pd.read_xml(filepath)

    elif ext in ('html', 'htm'):
        # read_html returns a list of tables; use the first one
        tables = pd.read_html(filepath)
        if not tables:
            raise ValueError("No HTML table found in the uploaded file.")
        df = tables[0]

    else:
        raise ValueError(f"Unsupported file format: .{ext}")

    return df
