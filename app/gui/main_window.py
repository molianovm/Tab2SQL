import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Frame

from gui import WidgetBuilder


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tab2SQL")
        self.geometry("1200x600")
        self.minsize(1200, 600)
        self.builder = WidgetBuilder()
        self.create_widgets()

    def create_widgets(self):
        # Основной контейнер
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True)
        # Слева – панель настроек
        self.build_config_frame(main_frame)
        # Справа – панель с SQL-кодом
        self.build_code_frame(main_frame)

    def build_config_frame(self, parent: Frame) -> None:
        # Создаем панель настроек (слева)
        config_frame = self.builder.frame(
            parent, width=500, pack_options={'side': 'left', 'fill': 'y', 'expand': False}
        )
        # Файловые настройки
        self.build_file_settings(config_frame)
        # Опции для Excel/CSV
        self.build_options_frame(config_frame)
        # Настройки таблицы
        self.build_table_frame(config_frame)
        # Заголовки для колонок
        self.build_headers_frame(config_frame)
        # Область для столбцов с прокруткой
        self.build_columns_canvas(config_frame)

    def build_file_settings(self, parent: Frame) -> None:
        file_frame = self.builder.frame(
            parent, pack_options={'padx': 10, 'pady': 5, 'fill': 'x'}
        )
        self.builder.button(
            file_frame,
            text="Выбрать файл",
            command=self.on_select_file,
            pack_options={'side': 'left'}
        )
        self.builder.label(
            file_frame, text="Файл не выбран", pack_options={'side': 'left', 'padx': 10}
        )
        self.builder.button(
            file_frame, text="Типы", command=self.on_show_types, pack_options={'side': 'right', 'padx': 5}
        )

    def build_options_frame(self, parent: Frame) -> None:
        options_frame = self.builder.frame(
            parent, pack_options={'padx': 10, 'pady': 5, 'fill': 'x'}
        )
        self.build_excel_frame(options_frame)
        self.build_csv_frame(options_frame)

    def build_excel_frame(self, parent: Frame) -> None:
        excel_frame = self.builder.frame(
            parent, pack_options={'padx': 5, 'pady': 5, 'fill': 'x'}
        )
        self.builder.label(
            excel_frame, text="Выберите лист:", pack_options={'side': 'left'}
        )
        self.builder.combobox(
            excel_frame, pack_options={'side': 'left', 'padx': 5}, state="readonly"
        )

    def build_csv_frame(self, parent: Frame) -> None:
        csv_frame = self.builder.frame(
            parent, pack_options={'padx': 5, 'pady': 5, 'fill': 'x'}
        )
        self.builder.label(
            csv_frame,
            text="Разделитель:", pack_options={'side': 'left'}
        )
        self.builder.entry(
            csv_frame, width=5, pack_options={'side': 'left', 'padx': 5}
        )
        self.builder.checkbutton(
            csv_frame, text="Заголовок", pack_options={'side': 'left', 'padx': 5}
        )

    def build_table_frame(self, parent: Frame) -> None:
        table_frame = self.builder.frame(
            parent, pack_options={'padx': 10, 'pady': 5, 'fill': 'x'}
        )
        self.builder.label(
            table_frame, text="Имя таблицы:", pack_options={'side': 'left'}
        )
        self.builder.entry(
            table_frame, width=30, pack_options={'side': 'left', 'padx': 5}
        )
        self.builder.button(
            table_frame, text="Генерация кода", command=self.on_generate_sql, pack_options={'side': 'right', 'padx': 5}
        )

    def build_headers_frame(self, parent: Frame) -> None:
        headers_frame = self.builder.frame(
            parent, pack_options={'padx': 10, 'pady': (5, 0), 'fill': 'x'}
        )
        # Используем grid для размещения заголовков столбцов
        headers = [
            ("Имя столбца", 20),
            ("Тип (наш)", 15),
            ("Новый тип", 15),
            ("Включить", 10)
        ]
        for i, (text, width) in enumerate(headers):
            lbl = ttk.Label(headers_frame, text=text, width=width, anchor="center")
            lbl.grid(row=0, column=i, padx=5)

    def build_columns_canvas(self, parent: Frame) -> None:
        # Область для столбцов с прокруткой
        canvas = self.builder.canvas(
            parent, pack_options={'side': 'left', 'fill': 'both', 'expand': True}
        )
        scrollbar = self.builder.scrollbar(
            parent, command=canvas.yview, pack_options={'side': 'right', 'fill': 'y'}
        )
        canvas.configure(yscrollcommand=scrollbar.set)

    def build_code_frame(self, parent: Frame) -> None:
        code_frame = self.builder.frame(
            parent, pack_options={'side': 'right', 'fill': 'both', 'expand': True}
        )
        self.builder.text(
            code_frame, pack_options={'padx': 10, 'pady': 5, 'fill': 'both', 'expand': True}
        )
        self.build_code_buttons_frame(code_frame)

    def build_code_buttons_frame(self, parent: Frame) -> None:
        btn_frame = self.builder.frame(
            parent, pack_options={'padx': 10, 'pady': 5, 'fill': 'x'}
        )
        self.builder.button(
            btn_frame, text="Копировать все", command=self.on_copy_all, pack_options={'side': 'left', 'padx': 5}
        )
        self.builder.button(
            btn_frame, text="Ошибки", command=self.on_show_errors, pack_options={'side': 'right', 'padx': 5}
        )

    # Обработчики событий (пример)
    def on_select_file(self):
        print("Выбран файл")

    def on_show_types(self):
        print("Показаны типы файлов")

    def on_generate_sql(self):
        print("Генерация SQL")

    def on_copy_all(self):
        print("Копировать весь код")

    def on_show_errors(self):
        print("Показ ошибок")
