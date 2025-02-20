import tkinter as tk
from tkinter import ttk, Canvas
from tkinter.ttk import Frame


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tab2SQL")
        self.geometry("1200x600")
        self.minsize(1200, 600)
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True)
        self._config_frame(main_frame)
        self._code_frame(main_frame)

    def _config_frame(self, frame: Frame) -> None:
        config_frame = ttk.Frame(frame, width=500)
        config_frame.pack(side='left', fill='y', expand=False)
        config_frame.pack_propagate(False)
        self._file_settings_frame(config_frame)
        self._options_frame(config_frame)
        self._table_frame(config_frame)
        self._headers_frame(config_frame)
        self._columns_canvas(config_frame)

    def _columns_canvas(self, frame: Frame) -> None:
        columns_canvas = tk.Canvas(frame)
        columns_canvas.pack(side="left", fill="both", expand=True)
        self._columns_canvas_scrollbar(frame, columns_canvas)

    @staticmethod
    def _columns_canvas_scrollbar(frame: Frame, canvas: Canvas) -> None:
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

    def _file_settings_frame(self, frame: Frame) -> None:
        file_settings_frm = ttk.Frame(frame)
        file_settings_frm.pack(padx=10, pady=5, fill='x')
        self._select_file_button(file_settings_frm)
        self._file_label(file_settings_frm)
        self._help_button(file_settings_frm)

    @staticmethod
    def _select_file_button(frame: Frame) -> None:
        select_file_btn = ttk.Button(frame, text="Выбрать файл")
        select_file_btn.pack(side='left')

    @staticmethod
    def _file_label(frame: Frame) -> None:
        file_lbl = ttk.Label(frame, text="Файл не выбран")
        file_lbl.pack(side='left', padx=10)

    @staticmethod
    def _help_button(frame: Frame) -> None:
        help_btn = ttk.Button(frame, text="Типы")
        help_btn.pack(side='right', padx=5)

    def _options_frame(self, frame: Frame) -> None:
        options_frm = ttk.Frame(frame)
        options_frm.pack(padx=10, pady=5, fill='x')
        self._excel_frame(options_frm)
        self._csv_frame(options_frm)

    def _excel_frame(self, frame: Frame) -> None:
        excel_frm = ttk.Frame(frame)
        excel_frm.pack(padx=5, pady=5, fill='x')
        ttk.Label(excel_frm, text="Выберите лист:").pack(side='left')
        self._sheet_combobox(excel_frm)

    @staticmethod
    def _sheet_combobox(frame: Frame) -> None:
        sheet_cb = ttk.Combobox(frame, state="readonly")
        sheet_cb.pack(side='left', padx=5)

    def _csv_frame(self, frame: Frame) -> None:
        csv_frm = ttk.Frame(frame)
        csv_frm.pack(padx=5, pady=5, fill='x')
        ttk.Label(csv_frm, text="Разделитель:").pack(side='left')
        self._delimiter_entry(csv_frm)
        self._header_checkbox(csv_frm)

    @staticmethod
    def _delimiter_entry(frame: Frame) -> None:
        delimiter_entry = ttk.Entry(frame, width=5)
        delimiter_entry.pack(side='left', padx=5)

    @staticmethod
    def _header_checkbox(frame: Frame) -> None:
        header_cb = ttk.Checkbutton(frame, text="Заголовок")
        header_cb.pack(side='left', padx=5)

    def _table_frame(self, frame: Frame) -> None:
        table_frm = ttk.Frame(frame)
        table_frm.pack(padx=10, pady=5, fill='x')
        ttk.Label(table_frm, text="Имя таблицы:").pack(side='left')
        self._table_entry(table_frm)
        self._generate_sql_button(table_frm)

    @staticmethod
    def _table_entry(frame: Frame) -> None:
        table_name = tk.StringVar()
        table_ent = ttk.Entry(frame, textvariable=table_name, width=30)
        table_ent.pack(side='left', padx=5)

    @staticmethod
    def _generate_sql_button(frame: Frame) -> None:
        generate_sql_btn = ttk.Button(frame, text="Сгенерировать код")
        generate_sql_btn.pack(side='right', padx=5)

    @staticmethod
    def _headers_frame(frame: Frame) -> None:
        headers_frm = ttk.Frame(frame)
        headers_frm.pack(padx=10, pady=(5, 0), fill='x')
        ttk.Label(headers_frm, text="Имя столбца", width=20, anchor="center").grid(row=0, column=0, padx=5)
        ttk.Label(headers_frm, text="Тип (наш)", width=15, anchor="center").grid(row=0, column=1, padx=5)
        ttk.Label(headers_frm, text="Новый тип", width=15, anchor="center").grid(row=0, column=2, padx=5)
        ttk.Label(headers_frm, text="Включить", width=10, anchor="center").grid(row=0, column=3, padx=5)

    def _code_frame(self, frame: Frame) -> None:
        code_frame = ttk.Frame(frame)
        code_frame.pack(side='right', fill='both', expand=True)
        self._sql_text(code_frame)
        self._code_buttons_frame(code_frame)

    @staticmethod
    def _sql_text(frame: Frame) -> None:
        sql_txt = tk.Text(frame)
        sql_txt.pack(padx=10, pady=5, fill='both', expand=True)

    def _code_buttons_frame(self, frame: Frame) -> None:
        buttons_frame = ttk.Frame(frame)
        buttons_frame.pack(padx=10, pady=5, fill='x')
        self._copy_all_button(buttons_frame)
        self._errors_button(buttons_frame)

    @staticmethod
    def _copy_all_button(frame: Frame) -> None:
        copy_all_btn = ttk.Button(frame, text="Копировать все")
        copy_all_btn.pack(side='left', padx=5)

    @staticmethod
    def _errors_button(frame: Frame) -> None:
        errors_btn = ttk.Button(frame, text="Ошибки")
        errors_btn.pack(side='right', padx=5)
