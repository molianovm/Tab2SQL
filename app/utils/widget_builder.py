import tkinter as tk
from tkinter import ttk, Canvas, Text
from tkinter.ttk import Frame, Button, Label, Entry, Combobox, Checkbutton
from typing import Callable, Any, Literal


class WidgetBuilder:
    """Класс для создания виджетов."""

    @staticmethod
    def frame(
        parent: Frame,
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
        parent: Frame,
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
