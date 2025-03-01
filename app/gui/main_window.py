import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Text, Canvas
from tkinter.ttk import Button, Frame, Entry, Label, Checkbutton, Combobox

import pandas as pd

from models.app import AppModel
from services import DataLoaderFactory, DataProcessing
from utils import messages
from utils.errors import CSVParseError, CSVIsEmptyError
from utils.logger import VALUE_FORMATTER_ERRORS
from utils.sql_formatter import SQLFormatterFactory
from utils.value_formatter import ValueFormatterFactory
from utils.widget_builder import WidgetBuilder


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tab2SQL")
        self.geometry("1200x500")
        self.minsize(1200, 500)
        self.builder = WidgetBuilder()
        self.model = AppModel()

        self._create_widgets()

    def _create_widgets(self) -> None:
        main_frame = self._get_main_frame()
        code_frame = CodeFrame(main_frame, self.builder, self.model)
        SettingsFrame(main_frame, self.builder, self.model, code_frame=code_frame)

    def _get_main_frame(self) -> Frame:
        return self.builder.frame(self, pack_options={'fill': 'both', 'expand': True})


class SettingsFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel, code_frame):
        self.parent = parent
        self.builder = builder
        self.model = model
        self.code_frame = code_frame

        self.file_parse_options_frame = None
        self.table_name_frame = None
        self.columns_config_frame = None

        self._create_widgets()

    def _create_widgets(self) -> None:
        settings_frame = self._get_settings_frame()
        FileSettingsFrame(settings_frame, self.builder, self.model, update_callback=self._on_file_selected)
        self.file_parse_options_frame = FileParseOptionsFrame(
            settings_frame, self.builder, self.model, update_callback=self._on_sheet_changed
        )
        self.table_name_frame = TableNameFrame(
            settings_frame, self.builder, self.model, code_frame=self.code_frame
        )
        GenerateSQLFrame(settings_frame, self.builder, self.model, code_frame=self.code_frame)
        HeadersFrame(settings_frame, self.builder, self.model)
        self.columns_config_frame = ColumnsConfigFrame(settings_frame, self.builder, self.model)

    def _get_settings_frame(self) -> Frame:
        return self.builder.frame(self.parent, pack_options={'side': 'left', 'fill': 'y', 'expand': False}, width=450)

    def _on_file_selected(self) -> None:
        self.file_parse_options_frame.update()
        self.table_name_frame.update()
        self.columns_config_frame.update()

    def _on_sheet_changed(self) -> None:
        self.table_name_frame.update()
        self.columns_config_frame.update()


class FileSettingsFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel, update_callback):
        self.parent = parent
        self.builder = builder
        self.model = model
        self.update_callback = update_callback

        self.file_settings_frame = None
        self.file_name_entry = None

        self._create_widgets()

    def _create_widgets(self) -> None:
        self.file_settings_frame = self._get_file_settings_frame()
        self._get_select_file_button()
        self.file_name_entry = self._get_file_name_entry()

    def _get_file_settings_frame(self) -> Frame:
        return self.builder.frame(self.parent, pack_options={'padx': 10, 'pady': 5, 'fill': 'x'})

    def _get_select_file_button(self) -> Button:
        return self.builder.button(
            self.file_settings_frame,
            text="Выбрать файл",
            command=self._select_file,
            pack_options={'side': 'left'}
        )

    def _get_file_name_entry(self) -> Entry:
        return self.builder.entry(
            self.file_settings_frame,
            state="readonly",
            width=55,
            pack_options={'side': 'left', 'padx': 5}
        )

    def _select_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Выберите файл",
            filetypes=[("Excel and CSV files", "*.xlsx *.xls *.csv")]
        )
        if file_path:
            self.model.file_path = file_path
            self.model.data_processing = None
            self._set_file_name_entry()
            self.model.get_extension()
            try:
                df, table_name = self._load_data()
                if df is None:
                    return
                if df.empty:
                    raise CSVIsEmptyError
                self.model.data_processing = DataProcessing(df, table_name.lower())
            except CSVParseError:
                messagebox.showerror("Ошибка парсинга CSV", messages.CSV_PARSE_ERROR)
            except CSVIsEmptyError:
                messagebox.showerror("Данные отсутствуют", messages.DATA_NOT_EXISTS)
            finally:
                self.update_callback()

    def _set_file_name_entry(self) -> None:
        self.file_name_entry.config(state="normal")
        self.file_name_entry.delete(0, tk.END)
        self.file_name_entry.insert(0, self.model.file_path)
        self.file_name_entry.xview_moveto(1.0)
        self.file_name_entry.config(state="readonly")

    def _load_data(self) -> tuple[pd.DataFrame, str]:
        df = None
        table_name = None
        if self.model.file_extension == ".csv":
            try:
                df, table_name = DataLoaderFactory().load_data(
                    file_path=self.model.file_path,
                    delimiter=self.model.delimiter_var.get(),
                    header=self.model.header_var.get()
                )
            except CSVParseError:
                messagebox.showerror("Ошибка парсинга CSV", messages.CSV_PARSE_ERROR)
                table_name = self.model.get_csv_table_name()
        elif self.model.file_extension in (".xlsx", ".xls"):
            self.model.get_sheet_names()
            df, table_name = DataLoaderFactory().load_data(
                file_path=self.model.file_path,
                sheet_name=self.model.selected_sheet_var.get()
            )
        return df, table_name


class FileParseOptionsFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel, update_callback):
        self.parent = parent
        self.builder = builder
        self.model = model
        self.update_callback = update_callback

        self.file_parse_options_frame = None
        self.csv_options_frame = None
        self.excel_options_frame = None

        self._create_widgets()

    def update(self) -> None:
        if self.model.file_extension == ".csv":
            self.csv_options_frame.update_options()
            self.excel_options_frame.hide()
        elif self.model.file_extension in (".xlsx", ".xls"):
            self.excel_options_frame.update_options()
            self.csv_options_frame.hide()

    def _create_widgets(self) -> None:
        self.file_parse_options_frame = self._get_file_parse_options_frame()
        self.csv_options_frame = CSVOptionsFrame(
            self.file_parse_options_frame,
            self.builder,
            self.model,
            update_callback=self.update_callback
        )
        self.excel_options_frame = ExcelOptionsFrame(
            self.file_parse_options_frame,
            self.builder,
            self.model,
            update_callback=self.update_callback
        )
        self._hide_options_frames()

    def _get_file_parse_options_frame(self) -> Frame:
        return self.builder.frame(self.parent, pack_options={'padx': 10, 'pady': 5, 'fill': 'x'})

    def _hide_options_frames(self) -> None:
        self.csv_options_frame.hide()
        self.excel_options_frame.hide()


class CSVOptionsFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel, update_callback):
        self.parent = parent
        self.builder = builder
        self.model = model
        self.update_callback = update_callback

        self.csv_options_frame = None
        self.delimiter_entry = None

        self._create_widgets()

    def update_options(self):
        self.csv_options_frame.pack(fill="x")

    def hide(self):
        self.csv_options_frame.pack_forget()

    def _create_widgets(self) -> None:
        self.csv_options_frame = self._get_csv_options_frame()
        self._get_delimiter_label()
        self.delimiter_entry = self._get_delimiter_entry()
        self._get_header_checkbutton()

    def _get_csv_options_frame(self) -> Frame:
        return self.builder.frame(self.parent, pack_options={'padx': 10, 'pady': 5, 'fill': 'x'})

    def _get_delimiter_label(self) -> Label:
        return self.builder.label(self.csv_options_frame, text="Разделитель:", pack_options={'side': 'left'})

    def _get_delimiter_entry(self) -> Entry:
        delimiter_entry = self.builder.entry(
            self.csv_options_frame,
            width=5,
            textvariable=self.model.delimiter_var,
            pack_options={'side': 'left', 'padx': 5}
        )
        delimiter_entry.bind("<Return>", self._on_csv_options_change)
        return delimiter_entry

    def _get_header_checkbutton(self) -> Checkbutton:
        return self.builder.checkbutton(
            self.csv_options_frame,
            text="Заголовок",
            variable=self.model.header_var,
            command=self._on_csv_options_change,
            pack_options={'side': 'left', 'padx': 5}
        )

    def _on_csv_options_change(self, event):
        if self.model.file_path and self.model.file_extension == ".csv":
            delimiter = self.model.delimiter_var.get()
            header = self.model.header_var.get()
            try:
                df, table_name = DataLoaderFactory().load_data(
                    file_path=self.model.file_path,
                    delimiter=delimiter,
                    header=header
                )
                self.model.data_processing = DataProcessing(df, table_name.lower())
                messagebox.showinfo("Смена разделителя", messages.DELIMITER_CHANGED.format(delimiter=delimiter))
            except CSVParseError:
                messagebox.showerror("Ошибка парсинга CSV", messages.CSV_PARSE_ERROR)
                self.model.data_processing = None
            finally:
                self.update_callback()


class ExcelOptionsFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel, update_callback):
        self.parent = parent
        self.builder = builder
        self.model = model
        self.update_callback = update_callback

        self.excel_options_frame = None
        self.sheet_combobox = None

        self._create_widgets()

    def update_options(self):
        self.sheet_combobox["values"] = self.model.sheet_names
        current = self.model.selected_sheet_var.get()
        if current and current in self.model.sheet_names:
            self.sheet_combobox.set(current)
        else:
            self.sheet_combobox.set(self.model.sheet_names[0])
            self.model.selected_sheet_var.set(self.model.sheet_names[0])
        self.excel_options_frame.pack(fill="x")

    def hide(self):
        self.excel_options_frame.pack_forget()

    def _create_widgets(self):
        self.excel_options_frame = self._get_excel_options_frame()
        self._get_sheet_label()
        self.sheet_combobox = self._get_sheet_combobox()

    def _get_excel_options_frame(self) -> Frame:
        return self.builder.frame(self.parent, pack_options={'padx': 10, 'pady': 5, 'fill': 'x'})

    def _get_sheet_label(self) -> Label:
        return self.builder.label(self.excel_options_frame, text="Выберите лист:", pack_options={'side': 'left'})

    def _get_sheet_combobox(self) -> Combobox:
        sheet_combobox = self.builder.combobox(
            self.excel_options_frame,
            state="readonly",
            pack_options={'side': 'left', 'padx': 5}
        )
        sheet_combobox.bind("<<ComboboxSelected>>", lambda event: self._load_excel())
        return sheet_combobox

    def _load_excel(self):
        sheet_name = self.sheet_combobox.get()
        self.model.selected_sheet_var.set(sheet_name)
        if self.model.file_path and self.model.file_extension in (".xlsx", ".xls"):
            df, table_name = DataLoaderFactory().load_data(
                file_path=self.model.file_path,
                sheet_name=sheet_name
            )
            if df.empty:
                messagebox.showerror("Ошибка", messages.DATA_NOT_EXISTS)
            self.model.data_processing = DataProcessing(df, table_name.lower())
            self.update_callback()


class TableNameFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel, code_frame):
        self.parent = parent
        self.builder = builder
        self.model = model
        self.code_frame = code_frame

        self.table_name_frame = None
        self.table_name_entry = None

        self._create_widgets()

    def update(self):
        self.table_name_entry.configure(state="normal")
        self.table_name_entry.delete(0, tk.END)
        if self.model.data_processing is not None:
            table_name = self.model.data_processing.table.name
        else:
            if self.model.file_extension == ".csv":
                table_name = self.model.get_csv_table_name()
            elif self.model.file_extension in (".xlsx", ".xls"):
                table_name = self.model.selected_sheet_var.get()
            else:
                table_name = ""
        self.table_name_entry.insert(0, table_name)

    def _create_widgets(self):
        self.table_name_frame = self._get_table_name_frame()
        self._get_table_name_label()
        self.table_name_entry = self._get_table_name_entry()
        self._get_show_types_button()

    def _get_table_name_frame(self) -> Frame:
        return self.builder.frame(self.parent, pack_options={'padx': 10, 'pady': 5, 'fill': 'x'})

    def _get_table_name_label(self) -> Label:
        return self.builder.label(self.table_name_frame, text="Имя таблицы:", pack_options={'side': 'left'})

    def _get_table_name_entry(self) -> Entry:
        table_name_entry = self.builder.entry(
            self.table_name_frame,
            textvariable=tk.StringVar(value=""),
            width=30,
            state="readonly",
            pack_options={'side': 'left', 'padx': 5}
        )
        table_name_entry.bind("<Return>", lambda event: self._set_table_name())
        return table_name_entry

    def _get_show_types_button(self):
        return self.builder.button(
            self.table_name_frame,
            text="?",
            command=self._show_types,
            width=5,
            pack_options={'side': 'right', 'padx': 5}
        )

    def _set_table_name(self):
        if self.model.data_processing is None:
            messagebox.showwarning("Предупреждение", messages.TABLE_NOT_EXIST)
            return
        table_name = self.table_name_entry.get()
        self.model.data_processing.table.name = table_name
        messagebox.showinfo("Изменение названия таблицы", messages.TABLE_NAME_CHANGED.format(table_name=table_name))

    def _show_types(self):
        types_window = tk.Toplevel()
        types_window.title("Описание типов")
        types_window.geometry("645x315")
        self.builder.label(
            types_window,
            text=messages.TYPES_INFO,
            justify="left",
            anchor="nw",
            pack_options={'padx': 10, 'pady': 10, 'fill': 'both', 'expand': False}
        )


class GenerateSQLFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel, code_frame):
        self.parent = parent
        self.builder = builder
        self.model = model
        self.code_frame = code_frame

        self.generate_sql_frame = None
        self.sql_template_combobox = None

        self._create_widgets()

    def _create_widgets(self):
        self.generate_sql_frame = self._get_generate_sql_frame()
        self._get_sql_template_label()
        self.sql_template_combobox = self._get_sql_template_combobox()
        self._get_generate_sql_button()

    def _get_generate_sql_frame(self) -> Frame:
        return self.builder.frame(self.parent, pack_options={'padx': 10, 'pady': 5, 'fill': 'x'})

    def _get_sql_template_label(self) -> Label:
        return self.builder.label(self.generate_sql_frame, text="Шаблон SQL:", pack_options={'side': 'left'})

    def _get_sql_template_combobox(self) -> Combobox:
        sql_template_combobox = self.builder.combobox(
            self.generate_sql_frame,
            textvariable=self.model.sql_template_type_var,
            values=SQLFormatterFactory().types,
            state="readonly",
            pack_options={'side': 'left', 'padx': 5}
        )
        sql_template_combobox.bind("<<ComboboxSelected>>", lambda event: self._set_sql_template)
        return sql_template_combobox

    def _get_generate_sql_button(self):
        return self.builder.button(
            self.generate_sql_frame,
            text="Генерация SQL",
            command=self._generate_sql,
            pack_options={'side': 'right', 'padx': 5}
        )

    def _set_sql_template(self, event):
        self.model.sql_template_type_var.set(self.sql_template_combobox.get())

    def _generate_sql(self):
        if self.model.data_processing is None:
            messagebox.showwarning("Предупреждение", messages.TABLE_NOT_EXIST)
            return
        VALUE_FORMATTER_ERRORS.clear()
        dp = self.model.data_processing
        try:
            sql_code = SQLFormatterFactory().get_sql(
                table_name=dp.table.name,
                columns=dp.valid_columns,
                values=dp.valid_values,
                sql_formatter=self.model.sql_template_type_var.get()
            )
        except Exception:
            messagebox.showerror("Ошибка генерации", messages.SQL_GENERATION_ERROR)
            return
        self.model.sql_script = sql_code
        self.code_frame.update_code(sql_code)
        self.code_frame.code_buttons_frame.update_errors_button()


class HeadersFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel):
        self.parent = parent
        self.builder = builder
        self.model = model

        self._create_widgets()

    def _create_widgets(self):
        self._get_headers_frame()

    def _get_headers_frame(self) -> Frame:
        headers_frame = self.builder.frame(self.parent, pack_options={'padx': 10, 'pady': (5, 0), 'fill': 'x'})
        headers = [("Имя столбца", 30), ("Тип", 7), ("Новый тип", 15), ("Включить", 10)]
        for i, (text, width) in enumerate(headers):
            lbl = ttk.Label(headers_frame, text=text, width=width, anchor="center")
            lbl.grid(row=0, column=i, padx=5)
        return headers_frame


class ColumnsConfigFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel):
        self.parent = parent
        self.builder = builder
        self.model = model
        self.valid_types = ValueFormatterFactory().types

        self.columns_config_frame = None
        self.columns_canvas = None
        self.inner_frame = None

        self._create_widgets()
        self._refresh_columns()

    def update(self):
        self._refresh_columns()

    def _create_widgets(self):
        self.columns_config_frame = self._get_columns_config_frame()
        self.columns_canvas = self._get_scrolled_canvas()
        self.inner_frame = self._get_inner_frame()

    def _get_columns_config_frame(self) -> tk.Frame:
        return self.builder.frame(self.parent, pack_options={'fill': 'both', 'expand': True})

    def _get_scrolled_canvas(self) -> Canvas:
        canvas, _ = self.builder.scrolled_canvas(
            parent=self.columns_config_frame,
            vertical=True,
            horizontal=False,
            pack_options={'fill': 'both', 'expand': True}
        )
        return canvas

    def _get_inner_frame(self):
        inner_frame = ttk.Frame(self.columns_canvas)
        self.columns_canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        inner_frame.bind(
            "<Configure>",
            lambda event: self.columns_canvas.configure(scrollregion=self.columns_canvas.bbox("all"))
        )
        return inner_frame

    def _refresh_columns(self):
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        if self.model.data_processing is not None:
            for i, col_obj in enumerate(self.model.data_processing.table.columns):
                self._create_column_row(i, col_obj)

    def _create_column_row(self, row_index, col_obj):
        row_frame = self._get_row_frame(row_index)
        # Поле для ввода имени колонки
        column_name_var = self._get_column_name(row_frame, col_obj)
        column_type = self._get_column_type(row_frame, col_obj)
        column_new_type_var = self._get_column_new_type(row_frame, col_obj, column_type)
        column_include_var = self._get_column_include(row_frame, col_obj)

        col_obj.new_name = column_name_var.get()
        col_obj.new_type = self._get_key_from_display(column_new_type_var.get())
        col_obj.include = column_include_var.get()

    def _get_row_frame(self, row_index):
        row_frame = ttk.Frame(self.inner_frame)
        row_frame.grid(row=row_index, column=0, sticky="w", padx=5, pady=2)
        return row_frame

    def _get_column_name(self, row_frame, col_obj):
        column_name = tk.StringVar(row_frame, value=col_obj.new_name)
        col_entry = self.builder.entry(row_frame, width=30, pack_options={'side': 'left'})
        col_entry.config(textvariable=column_name)
        col_entry.bind("<Return>", lambda event, c=col_obj, v=column_name: self._on_column_name_change(c, v.get()))
        return column_name

    def _get_column_type(self, row_frame, col_obj):
        column_type = self.valid_types.get(col_obj.new_type)
        self.builder.label(
            row_frame,
            text=column_type,
            width=10,
            anchor="center",
            pack_options={'side': 'left', 'padx': 5}
        )
        return column_type

    def _get_column_new_type(self, row_frame, col_obj, column_type):
        new_types = list(self.valid_types.values())
        new_type_var = tk.StringVar(value=column_type)
        new_type_combo = self.builder.combobox(
            row_frame,
            textvariable=new_type_var,
            values=new_types,
            state="readonly",
            width=11,
            pack_options={'side': 'left', 'padx': 5}
        )
        new_type_combo.bind(
            "<<ComboboxSelected>>",
            lambda event, c=col_obj, v=new_type_var: self._on_column_type_change(c, v.get())
        )
        return new_type_var

    def _get_column_include(self, row_frame, col_obj):
        include_var = tk.BooleanVar(value=col_obj.include)
        self.builder.checkbutton(
            row_frame,
            text="",
            variable=include_var,
            pack_options={'side': 'left', 'padx': 25}
        )
        include_var.trace("w", lambda *args, c=col_obj, var=include_var: self._on_column_include_change(c, var.get()))
        return include_var

    @staticmethod
    def _on_column_name_change(col_obj, new_name):
        col_obj.new_name = new_name

    def _on_column_type_change(self, col_obj, new_display):
        col_obj.new_type = self._get_key_from_display(new_display)

    @staticmethod
    def _on_column_include_change(col_obj, include_value):
        col_obj.include = include_value

    def _get_key_from_display(self, display):
        inverted = {v: k for k, v in self.valid_types.items()}
        return inverted.get(display, display)


class CodeFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel):
        self.parent = parent
        self.builder = builder
        self.model = model

        self.code_space_frame = None
        self.code_text = None
        self.code_buttons_frame = None

        self._create_widgets()

    def update_code(self, sql_code) -> None:
        self.code_text.delete("1.0", tk.END)
        self.code_text.insert(tk.END, sql_code)

    def _create_widgets(self) -> None:
        self.code_space_frame = self._get_code_space_frame()
        self.code_text = self._get_code_text()
        self.code_buttons_frame = CodeButtonsFrame(self.code_space_frame, self.builder, self.model)

    def _get_code_space_frame(self) -> Frame:
        return self.builder.frame(self.parent, pack_options={'side': 'right', 'fill': 'both', 'expand': True})

    def _get_code_text(self) -> Text:
        code_text, _ = self.builder.scrolled_text(
            parent=self.code_space_frame,
            wrap="none",
            pack_options={'padx': 10, 'pady': 5, 'fill': 'both', 'expand': True}
        )
        code_text.bind("<Control-c>", self._copy_selection)
        return code_text

    def _copy_selection(self, event) -> None:
        try:
            selected_text = self.code_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.code_text.winfo_toplevel().clipboard_clear()
            self.code_text.winfo_toplevel().clipboard_append(selected_text)
        except tk.TclError:
            pass


class CodeButtonsFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel):
        self.parent = parent
        self.builder = builder
        self.model = model

        self.code_buttons_frame = None
        self.errors_button = None

        self._create_widgets()

    def update_errors_button(self) -> None:
        count = len(VALUE_FORMATTER_ERRORS)
        if count == 0:
            self.errors_button.pack_forget()
        else:
            self.errors_button.config(text=f"Ошибки ({count})")
            if not self.errors_button.winfo_ismapped():
                self.errors_button.pack(side="right", padx=5)

    def _create_widgets(self) -> None:
        self.code_buttons_frame = self._get_code_button_frame()
        self._get_copy_all_button()
        self.errors_button = self._get_errors_button()

    def _get_code_button_frame(self) -> Frame:
        return self.builder.frame(self.parent, pack_options={'padx': 10, 'pady': 5, 'fill': 'x'})

    def _get_copy_all_button(self) -> Button:
        return self.builder.button(
            self.code_buttons_frame,
            text="Копировать все",
            command=self._copy_code,
            pack_options={'side': 'left', 'padx': 5}
        )

    def _get_errors_button(self) -> Button:
        errors_button = self.builder.button(
            self.code_buttons_frame, text="Ошибки (0)", command=self._show_errors,
            pack_options={'side': 'right', 'padx': 5}
        )
        errors_button.pack_forget()
        return errors_button

    def _copy_code(self) -> None:
        self.parent.clipboard_clear()
        self.parent.clipboard_append(self.model.sql_script)
        messagebox.showinfo("Информация", messages.SQL_COPIED_TO_CLIPBOARD)

    def _show_errors(self) -> None:
        if len(VALUE_FORMATTER_ERRORS) > 0:
            error_win = tk.Toplevel(self.parent)
            error_win.geometry("800x400")
            error_win.title("Ошибки при форматировании")
            error_text = self._get_error_text(error_win)
            error_text.insert(tk.END, "\n".join(VALUE_FORMATTER_ERRORS))
            error_text.config(state="disabled")

    def _get_error_text(self, error_window) -> Text:
        error_text, _ = self.builder.scrolled_text(
            parent=error_window,
            wrap="none",
            cursor="hand2",
            pack_options={'padx': 10, 'pady': 5, 'fill': 'both', 'expand': True}
        )
        return error_text
