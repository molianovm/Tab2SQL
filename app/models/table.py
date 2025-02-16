import pandas as pd

from .column import Column


class Table:
    """
    Класс, представляющий таблицу в базе данных.

    :param name: Название таблицы
    :param columns: Список столбцов таблицы
    :param data: Данные таблицы
    """

    def __init__(self, name: str, columns: list[Column] = None, data: pd.DataFrame = None):
        self.name = name
        self.columns = columns if columns else []
        self.data = data

    def __repr__(self):
        return f"Table(name={self.name!r}, columns={self.columns!r}, data={self.data!r})"
