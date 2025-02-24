import tkinter as tk

import pandas as pd

from services import DataProcessing


class AppModel:
    """Модель приложения."""

    def __init__(self):
        # Common
        self.file_path: str | None = None
        self.file_extension: str | None = None
        self.data_processing: DataProcessing | None = None
        self.column_settings: dict[str, str] = {}
        self.sql_script: str = ""
        self.errors: list[str] = []
        # CSV
        self.delimiter_var: tk.StringVar = tk.StringVar(value=";")
        self.header_var: tk.BooleanVar = tk.BooleanVar(value=True)
        # XLSX
        self.sheet_names: list[str] = []
        self.selected_sheet_var: tk.StringVar = tk.StringVar()

    def get_sheet_names(self):
        if self.file_extension in {".xlsx", ".xls"}:
            self.sheet_names = pd.ExcelFile(self.file_path).sheet_names
        self.selected_sheet_var.set(self.sheet_names[0])
