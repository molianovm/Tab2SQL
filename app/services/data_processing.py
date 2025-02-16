import pandas as pd

from models.column import Column
from models.table import Table
from utils import ValueFormatterFactory
from utils.errors import TypeNotFoundError


class DataProcessing:
    """
    Класс для обработки полученных данных и получения валидных колонок и значений.
    :param dataframe: DataFrame с данными.
    :param table_name: Название таблицы (для SQL запроса).
    """

    def __init__(self, dataframe: pd.DataFrame, table_name: str) -> None:
        self.table = self._get_table(dataframe=dataframe, table_name=table_name)

    @property
    def table_name(self) -> str:
        """
        Возвращает название таблицы.
        :return: Название таблицы.
        """
        return self.table.name

    @property
    def valid_columns(self) -> list[str]:
        """
        Возвращает список имен колонок, которые должны быть включены в результирующую таблицу.
        :return: Список имен колонок.
        """
        return [column.new_name for column in self.table.columns if column.include]

    @property
    def valid_values(self) -> list[str]:
        """
        Возвращает список строк, содержащих форматированные значения для каждого столбца,
        который включен в `valid_columns`. Каждая строка имеет вид "(val_1, val_2, ...)".
        :return: Список строк.
        """
        return [self._format_row(row) for _, row in self.table.data.iterrows()]

    def _format_row(self, row: pd.Series) -> str:
        """
        Форматирует `pd.Series` в строку, содержащую форматированные значения для каждого столбца,
        который включен в `valid_columns`.
        :param row: Строка `pd.Series` для форматирования.
        :return: Строка вида "(val_1, val_2, ...)".
        """
        row_values = [
            ValueFormatterFactory().get_value(
                column_type=column.new_type,
                input_value=row[column.column_name]
            )
            for column in self.table.columns if column.include
        ]
        return f"({', '.join(row_values)})"

    def _get_table(self, dataframe: pd.DataFrame, table_name: str) -> Table:
        """
        Возвращает экземпляр Table, содержащий информацию о столбцах
        и данных DataFrame.
        :param dataframe: DataFrame с данными.
        :param table_name: Название таблицы (для SQL запроса).
        :return: Экземпляр Table.
        """
        columns = []
        for column in dataframe.columns:
            column_type = self._pd_type_determinator(str(dataframe[column].dtype))
            columns.append(Column(column_name=column, column_type=column_type))
        return Table(name=table_name, columns=columns, data=dataframe)

    @staticmethod
    def _pd_type_determinator(input_type: str) -> str:
        """
        Определяет SQL-тип по типу pandas
        :param input_type: Тип pandas
        :return: Тип в который будет форматироваться для SQL
        :raises TypeNotFoundError: Если тип pandas не определен
        """
        type_matching = {
            "object": "str",
            "bool": "bool",
            "int64": "int",
            "float64": "float_r",
            "datetime64[ns]": "timestamp",
        }
        if input_type.lower() in type_matching.keys():
            return type_matching[input_type.lower()]
        raise TypeNotFoundError(f"Тип {input_type} не определeн")
