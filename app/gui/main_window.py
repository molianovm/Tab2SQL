import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from utils.widget_builder import WidgetBuilder
from models.app import AppModel
from services import DataLoaderFactory, DataProcessing
from utils.errors import CSVParseError
from utils.logger import VALUE_FORMATTER_ERRORS
from utils.sql_formatter import SQLFormatterFactory
from utils.value_formatter import ValueFormatterFactory


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tab2SQL")
        self.geometry("1200x600")
        self.minsize(1200, 600)
        self.builder = WidgetBuilder()
        self.model = AppModel()  # Модель содержит data_processing (экземпляр DataProcessing)

        self.main_frame = None
        self.settings_frame = None
        self.code_frame = None

        self.create_widgets()

    def create_widgets(self):
        self._build_main_frame()
        self.code_frame = CodeFrame(self.main_frame, self.builder, self.model)
        # Передаем ссылку на CodeFrame, чтобы после генерации SQL можно было обновить текст кнопки ошибок
        self.settings_frame = SettingsFrame(self.main_frame, self.builder, self.model, code_frame=self.code_frame)

    def _build_main_frame(self):
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)


class SettingsFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel, code_frame):
        self.parent = parent
        self.builder = builder
        self.model = model
        self.code_frame = code_frame

        self.settings_frame = None
        self.file_settings_and_types_frame = None
        self.file_parse_options_frame = None
        self.table_name_and_code_generate_frame = None
        self.headers_frame = None
        self.columns_config_frame = None

        self.create_widgets()

    def create_widgets(self):
        self.settings_frame = self.builder.frame(
            self.parent,
            pack_options={'side': 'left', 'fill': 'y', 'expand': False},
            width=500
        )
        self.file_settings_and_types_frame = FileSettingsAndTypesFrame(
            self.settings_frame, self.builder, self.model, update_callback=self.on_file_selected
        )
        self.file_parse_options_frame = FileParseOptionsFrame(
            self.settings_frame, self.builder, self.model, update_callback=self.on_sheet_changed
        )
        self.table_name_and_code_generate_frame = TableNameAndCodeGenerateFrame(
            self.settings_frame, self.builder, self.model, code_frame=self.code_frame
        )
        self.headers_frame = HeadersFrame(self.settings_frame, self.builder, self.model)
        self.columns_config_frame = ColumnsConfigFrame(self.settings_frame, self.builder, self.model)

    def on_file_selected(self):
        if self.model.file_extension == ".csv":
            self.file_parse_options_frame.update_csv_options()
            self.table_name_and_code_generate_frame.update_for_csv()
            self.columns_config_frame.update_for_csv()
        elif self.model.file_extension in (".xlsx", ".xls"):
            self.file_parse_options_frame.update_excel_options()
            self.table_name_and_code_generate_frame.update_for_excel()
            self.columns_config_frame.update_for_excel()

    def on_sheet_changed(self):
        self.table_name_and_code_generate_frame.update_for_excel()
        self.columns_config_frame.update_for_excel()


class FileSettingsAndTypesFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel, update_callback):
        self.parent = parent
        self.builder = builder
        self.model = model
        self.update_callback = update_callback

        self.file_settings_and_types_frame = None
        self.select_file_button = None
        self.file_name_label = None
        self.columns_types_button = None

        self.create_widgets()

    def create_widgets(self):
        self.file_settings_and_types_frame = self.builder.frame(
            self.parent, pack_options={'padx': 10, 'pady': 5, 'fill': 'x'}
        )
        self.select_file_button = self.builder.button(
            self.file_settings_and_types_frame,
            text="Выбрать файл",
            command=self.select_file,
            pack_options={'side': 'left'}
        )
        self.file_name_label = self.builder.label(
            self.file_settings_and_types_frame,
            text="Файл не выбран",
            pack_options={'side': 'left', 'padx': 10}
        )
        self.columns_types_button = self.builder.button(
            self.file_settings_and_types_frame,
            text="Типы",
            command=self.show_types,
            pack_options={'side': 'right', 'padx': 5}
        )

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл",
            filetypes=[("Excel and CSV files", "*.xlsx *.xls *.csv")]
        )
        if file_path:
            self.model.file_path = file_path
            self.file_name_label.config(text=self.model.file_path)
            self.model.file_extension = os.path.splitext(self.model.file_path)[1]
            if self.model.file_extension == ".csv":
                df, table_name = DataLoaderFactory().load_data(
                    file_path=self.model.file_path,
                    delimiter=self.model.delimiter_var.get(),
                    header=self.model.header_var.get()
                )
            elif self.model.file_extension in (".xlsx", ".xls"):
                self.model.get_sheet_names()
                df, table_name = DataLoaderFactory().load_data(
                    file_path=self.model.file_path,
                    sheet_name=self.model.selected_sheet_var.get()
                )
            self.model.data_processing = DataProcessing(df, table_name)
            self.model.table_name_var.set(self.model.data_processing.table.name)
            self.update_callback()
            print("Загружена таблица:", self.model.data_processing.table)

    def show_types(self):
        factory = ValueFormatterFactory()
        types_info = "\n".join([f"{k} - {v}" for k, v in factory.types.items()])
        messagebox.showinfo("Поддерживаемые типы", types_info)


class FileParseOptionsFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel, update_callback):
        self.parent = parent
        self.builder = builder
        self.model = model
        self.update_callback = update_callback

        self.file_parse_options_frame = None
        self.csv_options_frame = None
        self.excel_options_frame = None

        self.create_widgets()

    def create_widgets(self):
        self.file_parse_options_frame = self.builder.frame(
            self.parent, pack_options={'padx': 10, 'pady': 5, 'fill': 'x'}
        )
        self.csv_options_frame = CSVOptionsFrame(
            self.file_parse_options_frame, self.builder, self.model
        )
        self.excel_options_frame = ExcelOptionsFrame(
            self.file_parse_options_frame, self.builder, self.model, update_callback=self.update_callback
        )
        self.csv_options_frame.hide()
        self.excel_options_frame.hide()

    def update_csv_options(self):
        self.csv_options_frame.update_options()
        self.excel_options_frame.hide()

    def update_excel_options(self):
        self.excel_options_frame.update_options()
        self.csv_options_frame.hide()


class CSVOptionsFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel):
        self.parent = parent
        self.builder = builder
        self.model = model

        self.csv_options_frame = None
        self.delimiter_label = None
        self.delimiter_entry = None
        self.header_checkbutton = None

        self.create_widgets()

    def create_widgets(self):
        self.csv_options_frame = self.builder.frame(
            self.parent, pack_options={'padx': 5, 'pady': 5, 'fill': 'x'}
        )
        self.delimiter_label = self.builder.label(
            self.csv_options_frame, text="Разделитель:", pack_options={'side': 'left'}
        )
        self.delimiter_entry = self.builder.entry(
            self.csv_options_frame,
            width=5,
            pack_options={'side': 'left', 'padx': 5},
            textvariable=self.model.delimiter_var
        )
        self.delimiter_entry.bind("<Return>", self.on_csv_options_change)
        self.header_checkbutton = self.builder.checkbutton(
            self.csv_options_frame,
            text="Заголовок",
            pack_options={'side': 'left', 'padx': 5},
            variable=self.model.header_var,
            command=self.on_csv_options_change
        )

    def on_csv_options_change(self, event=None):
        if self.model.file_path and self.model.file_extension == ".csv":
            delimiter = self.model.delimiter_var.get()
            header = self.model.header_var.get()
            try:
                df, table_name = DataLoaderFactory().load_data(
                    file_path=self.model.file_path,
                    delimiter=delimiter,
                    header=header
                )
            except CSVParseError as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить CSV: {e}")
                return
            self.model.data_processing = DataProcessing(df, table_name)
            base_name = os.path.splitext(os.path.basename(self.model.file_path))[0]
            self.model.table_name_var.set(base_name.lower())
            print("CSV обновлён:", self.model.data_processing.table)

    def update_options(self):
        self.delimiter_entry.delete(0, tk.END)
        self.delimiter_entry.insert(0, ",")
        self.csv_options_frame.pack(fill="x")

    def hide(self):
        self.csv_options_frame.pack_forget()


class ExcelOptionsFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel, update_callback):
        self.parent = parent
        self.builder = builder
        self.model = model
        self.update_callback = update_callback

        self.excel_options_frame = None
        self.sheet_label = None
        self.sheet_combobox = None

        self.create_widgets()

    def create_widgets(self):
        self.excel_options_frame = self.builder.frame(
            self.parent, pack_options={'padx': 5, 'pady': 5, 'fill': 'x'}
        )
        self.sheet_label = self.builder.label(
            self.excel_options_frame, text="Выберите лист:", pack_options={'side': 'left'}
        )
        self.sheet_combobox = self.builder.combobox(
            self.excel_options_frame,
            pack_options={'side': 'left', 'padx': 5},
            state="readonly"
        )
        self.sheet_combobox.bind("<<ComboboxSelected>>", lambda event: self.load_excel())

    def update_options(self):
        self.sheet_combobox["values"] = self.model.sheet_names
        current = self.model.selected_sheet_var.get()
        if current and current in self.model.sheet_names:
            self.sheet_combobox.set(current)
        else:
            self.sheet_combobox.set(self.model.sheet_names[0])
            self.model.selected_sheet_var.set(self.model.sheet_names[0])
        self.excel_options_frame.pack(fill="x")

    def load_excel(self):
        sheet_name = self.sheet_combobox.get()
        self.model.selected_sheet_var.set(sheet_name)
        if self.model.file_path and self.model.file_extension in (".xlsx", ".xls"):
            df, table_name = DataLoaderFactory().load_data(
                file_path=self.model.file_path,
                sheet_name=sheet_name
            )
            self.model.data_processing = DataProcessing(df, table_name)
            self.model.table_name_var.set(self.model.data_processing.table.name)
            print("Excel загружен:", self.model.data_processing.table)
            self.update_callback()

    def hide(self):
        self.excel_options_frame.pack_forget()


class TableNameAndCodeGenerateFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel, code_frame):
        self.parent = parent
        self.builder = builder
        self.model = model
        self.code_frame = code_frame

        self.table_name_and_code_generate_frame = None
        self.table_name_entry = None
        self.generate_code_button = None

        self.create_widgets()

    def create_widgets(self):
        self.table_name_and_code_generate_frame = self.builder.frame(
            self.parent, pack_options={'padx': 10, 'pady': 5, 'fill': 'x'}
        )
        self.builder.label(
            self.table_name_and_code_generate_frame,
            text="Имя таблицы:",
            pack_options={'side': 'left'}
        )
        self.table_name_entry = self.builder.entry(
            self.table_name_and_code_generate_frame,
            textvariable=self.model.table_name_var,
            width=30,
            pack_options={'side': 'left', 'padx': 5}
        )
        self.table_name_entry.bind("<Return>", lambda event: self.set_table_name())
        self.generate_code_button = self.builder.button(
            self.table_name_and_code_generate_frame,
            text="Генерация кода",
            command=self.generate_sql,
            pack_options={'side': 'right', 'padx': 5}
        )

    def set_table_name(self):
        new_name = self.table_name_entry.get()
        self.model.data_processing.table.name = new_name
        self.model.table_name_var.set(new_name)
        print("Имя таблицы обновлено:", new_name)

    def update_for_csv(self):
        base_name = os.path.splitext(os.path.basename(self.model.file_path))[0]
        self.table_name_entry.delete(0, tk.END)
        self.table_name_entry.insert(0, base_name.lower())
        self.model.data_processing.table.name = base_name.lower()
        self.model.table_name_var.set(base_name.lower())

    def update_for_excel(self):
        if self.model.data_processing is not None:
            self.table_name_entry.delete(0, tk.END)
            self.table_name_entry.insert(0, self.model.data_processing.table.name)
            self.model.table_name_var.set(self.model.data_processing.table.name)

    def generate_sql(self):
        if self.model.data_processing is None:
            messagebox.showwarning("Предупреждение", "Таблица не создана.")
            return
        VALUE_FORMATTER_ERRORS.clear()
        dp = self.model.data_processing
        valid_columns = dp.valid_columns
        valid_values = dp.valid_values
        table_name = dp.table.name
        try:

            sql_code = SQLFormatterFactory().get_sql(table_name, valid_columns, valid_values, sql_formatter=1)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сгенерировать SQL: {e}")
            return
        self.model.sql_script = sql_code
        print("Сгенерирован SQL:")
        print(sql_code)
        self.code_frame.update_code(sql_code)
        # Обновляем текст кнопки ошибок с количеством ошибок
        self.code_frame.code_buttons_frame.update_errors_button()


class HeadersFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel):
        self.parent = parent
        self.builder = builder
        self.model = model

        self.headers_frame = None
        self.create_widgets()

    def create_widgets(self):
        self.headers_frame = self.builder.frame(
            self.parent, pack_options={'padx': 10, 'pady': (5, 0), 'fill': 'x'}
        )
        headers = [
            ("Имя столбца", 20),
            ("Тип (наш)", 15),
            ("Новый тип", 15),
            ("Включить", 10)
        ]
        for i, (text, width) in enumerate(headers):
            lbl = ttk.Label(self.headers_frame, text=text, width=width, anchor="center")
            lbl.grid(row=0, column=i, padx=5)


class ColumnsConfigFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel):
        self.parent = parent
        self.builder = builder
        self.model = model  # self.model.data_processing.table – объект Table
        self.valid_types = ValueFormatterFactory().types
        self.columns_config_frame = None
        self.columns_canvas = None
        self.columns_scrollbar = None
        self.inner_frame = None
        self.create_widgets()

    def create_widgets(self):
        self.columns_config_frame = self.builder.frame(
            self.parent, pack_options={'fill': 'both', 'expand': True}
        )
        self.columns_canvas = self.builder.canvas(
            self.columns_config_frame,
            pack_options={'side': 'left', 'fill': 'both', 'expand': True}
        )
        self.columns_scrollbar = self.builder.scrollbar(
            self.columns_config_frame, command=self.columns_canvas.yview,
            pack_options={'side': 'right', 'fill': 'y'}
        )
        self.columns_canvas.configure(yscrollcommand=self.columns_scrollbar.set)
        self.inner_frame = ttk.Frame(self.columns_canvas)
        self.columns_canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.inner_frame.bind(
            "<Configure>", lambda event: self.columns_canvas.configure(
                scrollregion=self.columns_canvas.bbox("all")
            )
        )
        self.refresh_columns()

    def refresh_columns(self):
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        if self.model.data_processing is not None:
            for i, col_obj in enumerate(self.model.data_processing.table.columns):
                self.create_column_row(i, col_obj)

    def create_column_row(self, row_index, col_obj):
        row_frame = ttk.Frame(self.inner_frame)
        row_frame.grid(row=row_index, column=0, sticky="w", padx=5, pady=2)
        # Поле для изменения имени колонки
        col_name_var = tk.StringVar(value=col_obj.new_name)
        col_entry = self.builder.entry(row_frame, width=20, pack_options={'side': 'left'})
        col_entry.config(textvariable=col_name_var)
        col_entry.bind("<Return>", lambda event, c=col_obj, v=col_name_var: self.update_column_name(c, v.get()))
        # Отображаем дружественное имя текущего типа
        default_display = self.valid_types.get(col_obj.new_type, col_obj.new_type)
        type_label = ttk.Label(row_frame, text=default_display, width=15, anchor="center")
        type_label.pack(side="left", padx=5)
        # Доступные типы (дружественные имена)
        display_options = list(self.valid_types.values())
        new_type_var = tk.StringVar(value=default_display)
        new_type_combo = self.builder.combobox(
            row_frame, textvariable=new_type_var, values=display_options, state="readonly",
            pack_options={'side': 'left', 'padx': 5}
        )
        new_type_combo.bind(
            "<<ComboboxSelected>>",
            lambda event, c=col_obj, v=new_type_var: self.update_column_type(c, v.get())
        )
        # Флажок для включения колонки с trace
        include_var = tk.BooleanVar(value=col_obj.include)
        include_cb = self.builder.checkbutton(
            row_frame, text="", variable=include_var, pack_options={'side': 'left', 'padx': 5}
        )
        include_var.trace("w", lambda *args, c=col_obj, var=include_var: self.update_column_include(c, var.get()))
        # Сохраняем изменения
        col_obj.new_name = col_name_var.get()
        col_obj.new_type = self.get_key_from_display(new_type_var.get())
        col_obj.include = include_var.get()

    def update_column_name(self, col_obj, new_name):
        col_obj.new_name = new_name
        print(f"Колонка '{col_obj.column_name}' переименована в '{new_name}'.")

    def update_column_type(self, col_obj, new_display):
        new_type = self.get_key_from_display(new_display)
        col_obj.new_type = new_type
        print(f"Колонка '{col_obj.column_name}' обновлена до типа '{new_type}'.")

    def update_column_include(self, col_obj, include_value):
        col_obj.include = include_value
        print(f"Колонка '{col_obj.column_name}' включена: {include_value}")

    def get_key_from_display(self, display):
        inverted = {v: k for k, v in self.valid_types.items()}
        return inverted.get(display, display)

    def update_for_csv(self):
        if self.model.data_processing is not None:
            print("Обновление колонок для CSV")
            self.refresh_columns()

    def update_for_excel(self):
        if self.model.data_processing is not None:
            print("Обновление колонок для Excel")
            self.refresh_columns()


class CodeFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel):
        self.parent = parent
        self.builder = builder
        self.model = model

        self.code_space_frame = None
        self.code_text = None
        self.code_buttons_frame = None

        self.create_widgets()

    def create_widgets(self):
        self.code_space_frame = self.builder.frame(
            self.parent, pack_options={'side': 'right', 'fill': 'both', 'expand': True}
        )
        self.code_text = self.builder.text(
            self.code_space_frame,
            pack_options={'padx': 10, 'pady': 5, 'fill': 'both', 'expand': True}
        )
        self.code_text.bind("<Control-c>", self.copy_selection)
        self.code_buttons_frame = CodeButtonsFrame(self.code_space_frame, self.builder, self.model)

    def update_code(self, sql_code):
        self.code_text.delete("1.0", tk.END)
        self.code_text.insert(tk.END, sql_code)

    def copy_selection(self, event):
        try:
            selected_text = self.code_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.code_text.winfo_toplevel().clipboard_clear()
            self.code_text.winfo_toplevel().clipboard_append(selected_text)
        except tk.TclError:
            pass
        return "break"


class CodeButtonsFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel):
        self.parent = parent
        self.builder = builder
        self.model = model

        self.code_buttons_frame = None
        self.copy_all_button = None
        self.errors_button = None

        self.create_widgets()

    def create_widgets(self):
        self.code_buttons_frame = self.builder.frame(
            self.parent, pack_options={'padx': 10, 'pady': 5, 'fill': 'x'}
        )
        self.copy_all_button = self.builder.button(
            self.code_buttons_frame, text="Копировать все", command=self.copy_code,
            pack_options={'side': 'left', 'padx': 5}
        )
        self.errors_button = self.builder.button(
            self.code_buttons_frame, text="Ошибки (0)", command=self.show_errors,
            pack_options={'side': 'right', 'padx': 5}
        )
        self.errors_button.pack_forget()

    def copy_code(self):
        self.parent.clipboard_clear()
        self.parent.clipboard_append(self.model.sql_script)
        messagebox.showinfo("Информация", "SQL-код скопирован в буфер обмена")

    def show_errors(self):
        if len(VALUE_FORMATTER_ERRORS) == 0:
            messagebox.showinfo("Ошибки", "Ошибок нет")
        else:
            # Открываем окно с логом ошибок
            error_win = tk.Toplevel(self.parent)
            error_win.title("Лог ошибок")
            error_text = tk.Text(error_win)
            error_text.pack(fill="both", expand=True)
            errors = "\n".join(VALUE_FORMATTER_ERRORS)
            error_text.insert(tk.END, errors)
            error_text.config(state="disabled")

    def update_errors_button(self):
        count = len(VALUE_FORMATTER_ERRORS)
        if count == 0:
            # Скрываем кнопку, если ошибок нет
            self.errors_button.pack_forget()
        else:
            # Обновляем текст кнопки и показываем её, если она скрыта
            self.errors_button.config(text=f"Ошибки ({count})")
            if not self.errors_button.winfo_ismapped():
                self.errors_button.pack(side="right", padx=5)
