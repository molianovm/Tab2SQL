import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.ttk import Frame

from gui import WidgetBuilder
from models.app import AppModel

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tab2SQL")
        self.geometry("1200x600")
        self.minsize(1200, 600)
        self.builder = WidgetBuilder()
        self.model = AppModel()

        self.main_frame = None
        self.settings_frame = None
        self.code_frame = None
        self.create_widgets()

    def create_widgets(self):
        # Основной контейнер
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill='both', expand=True)
        # Левая сторона – панель настроек
        self.settings_frame = SettingsFrame(self.main_frame, self.builder, self.model)
        # Правая сторона – панель с SQL-кодом
        self.code_frame = CodeFrame(self.main_frame, self.builder, self.model)


class SettingsFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel):
        self.parent = parent
        self.builder = builder
        self.model = model

        # Создаем основной контейнер для настроек
        self.settings_frame = None
        self.file_settings_and_types_frame = None
        self.file_parse_options_frame = None
        self.table_name_and_code_generate_frame = None
        self.headers_frame = None
        self.columns_config_frame = None

        self.create_widgets()

    def create_widgets(self):
        self.settings_frame = self.builder.frame(
            self.parent, pack_options={'side': 'left', 'fill': 'y', 'expand': False}, width=500
        )
        # Файловые настройки
        self.file_settings_and_types_frame = FileSettingsAndTypesFrame(self.settings_frame, self.builder, self.model)
        # Опции для Excel/CSV
        self.file_parse_options_frame = FileParseOptionsFrame(self.settings_frame, self.builder, self.model)
        # Настройки таблицы
        self.table_name_and_code_generate_frame = TableNameAndCodeGenerateFrame(
            self.settings_frame,
            self.builder,
            self.model
        )
        # Заголовки для колонок
        self.headers_frame = HeadersFrame(self.settings_frame, self.builder, self.model)
        # Область для колонок с прокруткой
        self.columns_config_frame = ColumnsConfigFrame(self.settings_frame, self.builder, self.model)


class FileSettingsAndTypesFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel):
        self.parent = parent
        self.builder = builder
        self.model = model

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
            command=self.get_file,
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

    def get_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл",
            filetypes=[("Excel and CSV files", "*.xlsx *.xls *.csv")]
        )
        if file_path:
            self.model.file_name = file_path
            self.file_name_label.config(text=file_path)

    def show_types(self):
        print("Показаны типы файлов")


class FileParseOptionsFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel):
        self.parent = parent
        self.builder = builder
        self.model = model

        self.file_parse_options_frame = None
        self.csv_options_frame = None
        self.excel_options_frame = None

        self.create_widgets()

    def create_widgets(self):
        # Опции для Excel
        self.file_parse_options_frame = self.builder.frame(
            self.parent, pack_options={'padx': 10, 'pady': 5, 'fill': 'x'}
        )
        self.csv_options_frame = CSVOptionsFrame(self.file_parse_options_frame, self.builder, self.model)
        self.excel_options_frame = ExcelOptionsFrame(self.file_parse_options_frame, self.builder, self.model)


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
        # Опции для CSV
        self.csv_options_frame = self.builder.frame(
            self.parent, pack_options={'padx': 5, 'pady': 5, 'fill': 'x'}
        )
        self.delimiter_label = self.builder.label(
            self.csv_options_frame,
            text="Разделитель:",
            pack_options={'side': 'left'}
        )
        self.delimiter_entry = self.builder.entry(
            self.csv_options_frame, width=5,
            pack_options={'side': 'left', 'padx': 5}
        )
        self.header_checkbutton = self.builder.checkbutton(
            self.csv_options_frame,
            text="Заголовок",
            pack_options={'side': 'left', 'padx': 5}
        )


class ExcelOptionsFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel):
        self.parent = parent
        self.builder = builder
        self.model = model

        self.excel_options_frame = None
        self.sheet_label = None
        self.sheet_combobox = None

        self.create_widgets()

    def create_widgets(self):
        self.excel_options_frame = self.builder.frame(
            self.parent, pack_options={'padx': 5, 'pady': 5, 'fill': 'x'}
        )
        self.builder.label(
            self.excel_options_frame,
            text="Выберите лист:",
            pack_options={'side': 'left'}
        )
        self.builder.combobox(
            self.excel_options_frame,
            pack_options={'side': 'left', 'padx': 5},
            state="readonly"
        )


class TableNameAndCodeGenerateFrame:
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel):
        self.parent = parent
        self.builder = builder
        self.model = model

        self.table_name_and_code_generate_frame = None
        self.table_name_label = None
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
        self.builder.entry(
            self.table_name_and_code_generate_frame, width=30,
            pack_options={'side': 'left', 'padx': 5}
        )
        self.builder.button(
            self.table_name_and_code_generate_frame,
            text="Генерация кода",
            command=self.generate_sql,
            pack_options={'side': 'right', 'padx': 5}
        )

    def generate_sql(self):
        print("Генерация SQL")


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
    def __init__(self, parent, builder: WidgetBuilder, model: AppModel, ):
        self.parent = parent
        self.builder = builder
        self.model = model
        self.columns_config_frame = None
        self.columns_canvas = None
        self.columns_scrollbar = None
        self.create_widgets()

    def create_widgets(self):
        self.columns_config_frame = self.builder.frame(
            self.parent, pack_options={'fill': 'both', 'expand': True}
        )
        # Область для столбцов с прокруткой
        self.columns_canvas = self.builder.canvas(
            self.columns_config_frame, pack_options={'side': 'left', 'fill': 'both', 'expand': True}
        )
        self.columns_scrollbar = self.builder.scrollbar(
            self.columns_config_frame, command=self.columns_canvas.yview,
            pack_options={'side': 'right', 'fill': 'y'}
        )
        self.columns_canvas.configure(yscrollcommand=self.columns_scrollbar.set)


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
            self.code_space_frame, pack_options={'padx': 10, 'pady': 5, 'fill': 'both', 'expand': True}
        )
        self.code_buttons_frame = CodeButtonsFrame(self.code_space_frame, self.builder, self.model)

    def copy_all(self):
        print("Копировать весь код")
        # Реализуйте копирование содержимого text_widget в буфер обмена

    def show_errors(self):
        print("Показ ошибок")
        # Реализуйте отображение окна с ошибками


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
            self.code_buttons_frame, text="Ошибки", command=self.show_errors,
            pack_options={'side': 'right', 'padx': 5}
        )

    def copy_code(self):
        print("Код скоприован")

    def show_errors(self):
        print("Показ ошибок")
