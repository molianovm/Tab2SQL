from utils import validate_keys
from utils.errors import SQLFormatterNotFoundError


class SQLFormatter:
    """
    Класс для форматирования SQL запросов
    :param table_name: Название таблицы
    :param columns: Список имен колонок
    :param values: Список значений
    """

    def __init__(self, table_name: str, columns: list[str], values: list[str]):
        self.table_name = table_name
        self.columns = columns
        self.values = values

    def formatter_1(self):
        columns = "\n         , ".join(self.columns)
        values = "\n     , ".join(self.values)
        return (
            f"TRUNCATE TABLE {self.table_name};\n\n"
            f"INSERT\n  INTO {self.table_name} (\n"
            f"           {columns}\n       )\n"
            f"VALUES {values};"
        )

    def formatter_2(self):
        columns = ", ".join(self.columns)
        values = ",\n       ".join(self.values)
        return (
            f"TRUNCATE TABLE {self.table_name};\n\n"
            f"INSERT INTO {self.table_name} ({columns})\n"
            f"VALUES {values};"
        )

    def formatter_3(self):
        columns = "\n         , ".join(self.columns)
        values = "\n     , ".join(self.values)
        return (
            f"DELETE\n  FROM {self.table_name};\n\n"
            f"INSERT\n  INTO {self.table_name} (\n"
            f"           {columns}\n       )\n"
            f"VALUES {values};"
        )

    def formatter_4(self):
        columns = ", ".join(self.columns)
        values = ",\n       ".join(self.values)
        return (
            f"DELETE FROM {self.table_name};\n\n"
            f"INSERT INTO {self.table_name} ({columns})\n"
            f"VALUES {values};"
        )


class SQLFormatterFactory:
    """Класс для выбора SQL шаблона для форматирования"""
    VALID_SQL_FORMATTERS = [
        "Тип 1",
        "Тип 2",
        "Тип 3",
        "Тип 4"
    ]

    @property
    def types(self) -> list[str]:
        """
        Возвращает список возможных типов SQL шаблонов
        :return: Список возможных типов SQL шаблонов
        """
        return self.VALID_SQL_FORMATTERS

    def get_sql(self, table_name: str, columns: list[str], values: list[str], sql_formatter: str = 'Тип 1'):
        """
        Возвращает SQL запрос на основе списка имен колонок и значений
        :param table_name: Название таблицы
        :param columns: Список имен колонок
        :param values: Список значений
        :param sql_formatter: Тип SQL шаблона для форматирования
        :return: SQL запрос
        :raises KeyMismatchError: Если есть пропущенные или лишние ключи
        :raises SQLFormatterNotFoundError: Если тип SQL шаблона для форматирования не найден
        """
        formatters = {
            'Тип 1': SQLFormatter(table_name, columns, values).formatter_1,
            'Тип 2': SQLFormatter(table_name, columns, values).formatter_2,
            'Тип 3': SQLFormatter(table_name, columns, values).formatter_3,
            'Тип 4': SQLFormatter(table_name, columns, values).formatter_4,
        }
        validate_keys(
            expected=set(self.types),
            expected_name="types",
            actual=set(formatters.keys()),
            actual_name="formatters"
        )
        if sql_formatter not in self.types:
            raise SQLFormatterNotFoundError("Тип SQL шаблона для форматирования не найден")
        return formatters[sql_formatter]()
