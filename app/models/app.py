import tkinter as tk

import pandas as pd


class AppModel:
    """Модель приложения."""

    def __init__(self):
        # Common
        self.file_name: str | None = None
        self.file_extension: str | None = None
        self.df: pd.DataFrame | None = None
        self.table_name_var = tk.StringVar()
        self.column_settings: dict[str, str] = {}
        self.sql_script: str = ""
        self.errors: list[str] = []
        # CSV
        self.delimiter_var: tk.StringVar = tk.StringVar(value=",")
        self.header_var: tk.BooleanVar = tk.BooleanVar(value=True)
        # XLSX
        self.sheet_names: list[str] = []
        self.selected_sheet_var: tk.StringVar = tk.StringVar(value=",")
