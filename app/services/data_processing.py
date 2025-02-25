import pandas as pd

from models.column import Column
from models.table import Table
from utils import ValueFormatterFactory
from utils.errors import TypeNotFoundError, FailedValueFormattingError
from utils.logger import log_error, VALUE_FORMATTER_ERRORS


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
        return [
            self._format_row(row, index)
            for index, (_, row) in enumerate(self.table.data.iterrows(), start=1)
        ]

    def _format_row(self, row: pd.Series, row_number: int) -> str:
        """
        Форматирует `pd.Series` в строку, содержащую форматированные значения для каждого столбца,
        который включен в `valid_columns`.
        :param row: Строка `pd.Series` для форматирования.
        :param row_number: Номер строки.
        :return: Строка вида "(val_1, val_2, ...)".
        """
        row_values = []
        for column in self.table.columns:
            if column.include:
                value = row[column.column_name]
                formatted_value = self._get_formatted_value(
                    column_type=column.new_type,
                    input_value=value,
                    row_number=row_number,
                    column_name=column.new_name
                )
                row_values.append(formatted_value)
        return f"({', '.join(row_values)})"

    @staticmethod
    def _get_formatted_value(column_type: str, input_value: any, row_number: int, column_name: str) -> str:
        """
        Форматирует значение input_value в строку, используя column_type
        :param column_type: Тип для форматирования
        :param input_value: Значение для форматирования
        :param row_number: Номер строки (для error message)
        :param column_name: Имя столбца (для error message)
        :return: Форматированное значение
        """
        try:
            return ValueFormatterFactory().get_value(column_type, input_value)
        except (ValueError, TypeError, FailedValueFormattingError):
            readable_type = ValueFormatterFactory().types[column_type]
            message = (
                f"Ошибка преобразования [{row_number}, {column_name}]: "
                f"входное значение «{input_value}» в тип «{readable_type}»")
            log_error(logger=VALUE_FORMATTER_ERRORS, message=message)
            return str("NULL")

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
