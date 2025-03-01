import os
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
        self.sql_template_type_var: tk.StringVar = tk.StringVar(value="Тип 1")
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

    def get_extension(self):
        try:
            self.file_extension = os.path.splitext(self.file_path)[1].lower()
        except Exception:
            self.file_extension = None

    def get_csv_table_name(self):
        if self.file_path and self.file_extension == ".csv":
            return os.path.splitext(os.path.basename(self.file_path))[0].lower()
