import tkinter as tk
from tkinter import ttk, Canvas, Text, Toplevel, Tk
from tkinter.ttk import Frame, Button, Label, Entry, Combobox, Checkbutton
from typing import Callable, Any, Literal


class WidgetBuilder:
    """Класс для создания виджетов."""

    @staticmethod
    def frame(
        parent: Tk | Frame,
        pack_options: dict[str, Any] | None = None,
        **widget_options: Any
    ) -> Frame:
        """Создает `ttk.Frame` с заданными настройками.
        :param parent: Родительский виджет
        :param pack_options: Настройки для упаковки
        :param widget_options: Настройки для виджета
        :return: Созданный виджет
        """
        if pack_options is None:
            pack_options = {}
        frame = ttk.Frame(parent, **widget_options)
        frame.pack(**pack_options)
        if widget_options.get('width'):
            frame.pack_propagate(False)
        return frame

    @staticmethod
    def button(
        parent: Frame,
        text: str,
        command: Callable | None = None,
        pack_options: dict[str, Any] | None = None,
        **widget_options: Any
    ) -> Button:
        """Создает `ttk.Button` с заданными настройками.
        :param parent: Родительский виджет
        :param text: Текст кнопки
        :param command: Функция-обработчик
        :param pack_options: Настройки для упаковки
        :param widget_options: Настройки для виджета
        :return: Созданный виджет
        """
        if pack_options is None:
            pack_options = {}
        btn = ttk.Button(parent, text=text, command=command, **widget_options)
        btn.pack(**pack_options)
        return btn

    @staticmethod
    def label(
        parent: Frame | Toplevel,
        text: str,
        pack_options: dict[str, Any] | None = None,
        **widget_options: Any
    ) -> Label:
        """Создает `ttk.Label` с заданными настройками.
        :param parent: Родительский виджет
        :param text: Текст метки
        :param pack_options: Настройки для упаковки
        :param widget_options: Настройки для виджета
        :return: Созданный виджет
        """
        if pack_options is None:
            pack_options = {}
        lbl = ttk.Label(parent, text=text, **widget_options)
        lbl.pack(**pack_options)
        return lbl

    @staticmethod
    def entry(
        parent: Frame,
        width: int,
        pack_options: dict[str, Any] | None = None,
        **widget_options: Any
    ) -> Entry:
        """Создает `ttk.Entry` с заданными настройками.

        :param parent: Родительский виджет
        :param width: Ширина поля ввода
        :param pack_options: Настройки для упаковки
        :param widget_options: Настройки для виджета
        :return: Созданный виджет
        """
        if pack_options is None:
            pack_options = {}
        entry = ttk.Entry(parent, width=width, **widget_options)
        entry.pack(**pack_options)
        return entry

    @staticmethod
    def combobox(
        parent: Frame,
        pack_options: dict[str, Any] | None = None,
        **widget_options: Any
    ) -> Combobox:
        """Создает `ttk.Combobox` с заданными настройками.
        :param parent: Родительский виджет
        :param pack_options: Настройки для упаковки
        :param widget_options: Настройки для виджета
        :return: Созданный виджет
        """
        if pack_options is None:
            pack_options = {}
        cb = ttk.Combobox(parent, **widget_options)
        cb.pack(**pack_options)
        return cb

    @staticmethod
    def checkbutton(
        parent: Frame,
        text: str,
        pack_options: dict[str, Any] | None = None,
        **widget_options: Any
    ) -> Checkbutton:
        """Создает `ttk.Checkbutton` с заданными настройками.
        :param parent: Родительский виджет
        :param text: Текст флажка
        :param pack_options: Настройки для упаковки
        :param widget_options: Настройки для виджета
        :return: Созданный виджет
        """
        if pack_options is None:
            pack_options = {}
        cb = ttk.Checkbutton(parent, text=text, **widget_options)
        cb.pack(**pack_options)
        return cb

    @staticmethod
    def text(
        parent: Frame,
        pack_options: dict[str, Any] | None = None,
        **widget_options: Any
    ) -> Text:
        """Создает `tk.Text` с заданными настройками.
        :param parent: Родительский виджет
        :param pack_options: Настройки для упаковки
        :param widget_options: Настройки для виджета
        :return: Созданный виджет
        """
        if pack_options is None:
            pack_options = {}
        txt = tk.Text(parent, **widget_options)
        txt.pack(**pack_options)
        return txt

    @staticmethod
    def canvas(
        parent: Frame,
        pack_options: dict[str, Any] | None = None,
        **widget_options: Any
    ) -> Canvas:
        """Создает `tk.Canvas` с заданными настройками.
        :param parent: Родительский виджет
        :param pack_options: Настройки для упаковки
        :param widget_options: Настройки для виджета
        :return: Созданный виджет
        """
        if pack_options is None:
            pack_options = {}
        cnv = tk.Canvas(parent, **widget_options)
        cnv.pack(**pack_options)
        return cnv

    @staticmethod
    def scrollbar(
        parent: Frame,
        orient: Literal["vertical", "horizontal"] = "vertical",
        command: Callable | None = None,
        pack_options: dict[str, Any] | None = None,
        **widget_options: Any
    ) -> ttk.Scrollbar:
        """Создает `ttk.Scrollbar` с заданными настройками.
        :param parent: Родительский виджет
        :param orient: Ориентация полосы прокрутки
        :param command: Функция-обработчик
        :param pack_options: Настройки для упаковки
        :param widget_options: Настройки для виджета
        :return: Созданный виджет
        """
        if pack_options is None:
            pack_options = {}
        sb = ttk.Scrollbar(parent, orient=orient, command=command, **widget_options)
        sb.pack(**pack_options)
        return sb

    @staticmethod
    def scrolled_text(
        parent: Frame | Toplevel,
        vertical: bool = True,
        horizontal: bool = True,
        pack_options: dict[str, Any] | None = None,
        **text_options
    ) -> tuple[Text, Frame]:
        return WidgetBuilder._scrolled_widget(tk.Text, parent, vertical, horizontal, pack_options, **text_options)

    @staticmethod
    def scrolled_canvas(
        parent: Frame | Toplevel,
        vertical: bool = True,
        horizontal: bool = True,
        pack_options: dict[str, Any] | None = None,
        **canvas_options
    ) -> tuple[Canvas, Frame]:
        return WidgetBuilder._scrolled_widget(tk.Canvas, parent, vertical, horizontal, pack_options, **canvas_options)

    @staticmethod
    def _scrolled_widget(
        widget_class,
        parent: Frame | Toplevel,
        vertical: bool = True,
        horizontal: bool = True,
        pack_options: dict[str, Any] | None = None,
        **widget_options
    ) -> tuple[Any, Frame]:
        """
        Создает контейнер с виджетом (указанным через widget_class) и опциональными скроллбарами.

        :param widget_class: Класс виджета (например, tk.Text или tk.Canvas).
        :param parent: Родительский виджет.
        :param vertical: Если True, добавляет вертикальный скроллбар.
        :param horizontal: Если True, добавляет горизонтальный скроллбар.
        :param pack_options: Параметры упаковки для контейнера.
        :param widget_options: Дополнительные параметры для создаваемого виджета.
        :return: Кортеж (widget_instance, container)
        """
        if pack_options is None:
            pack_options = {}
        container = tk.Frame(parent)
        container.pack(**pack_options)

        widget_instance = widget_class(container, **widget_options)
        widget_instance.grid(row=0, column=0, sticky="nsew")

        if vertical:
            v_scroll = tk.Scrollbar(container, orient="vertical", command=widget_instance.yview, cursor="hand2")
            v_scroll.grid(row=0, column=1, sticky="ns")
            widget_instance.config(yscrollcommand=v_scroll.set)

        if horizontal:
            h_scroll = tk.Scrollbar(container, orient="horizontal", command=widget_instance.xview, cursor="hand2")
            h_scroll.grid(row=1, column=0, sticky="ew")
            widget_instance.config(xscrollcommand=h_scroll.set)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        return widget_instance, container
