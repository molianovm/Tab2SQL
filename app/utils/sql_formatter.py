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
            f"DELETE\n  FROM {self.table_name};\n\n"
            f"INSERT\n  INTO {self.table_name} (\n"
            f"           {columns}\n       )\n"
            f"VALUES {values};"
        )

    def formatter_2(self):
        columns = ", ".join(self.columns)
        values = ",\n       ".join(self.values)
        return (
            f"DELETE FROM {self.table_name};\n\n"
            f"INSERT INTO {self.table_name} ({columns})\n"
            f"VALUES {values};"
        )


class SQLFormatterFactory:
    """

    """
    valid_sql_formatters = [1, 2]

    @classmethod
    def get_sql(cls, table_name: str, columns: list[str], values: list[str], sql_formatter: int = 1):
        """
        Возвращает SQL запрос на основе списка имен колонок и значений
        :param table_name: Название таблицы
        :param columns: Список имен колонок
        :param values: Список значений
        :param sql_formatter: Тип SQL шаблона для форматирования
        :return: SQL запрос
        :raises SQLFormatterNotFoundError: Если тип SQL шаблона для форматирования не найден
        """
        sql_formatters = {
            1: SQLFormatter(table_name, columns, values).formatter_1,
            2: SQLFormatter(table_name, columns, values).formatter_2
        }

        if sql_formatter not in cls.valid_sql_formatters:
            raise SQLFormatterNotFoundError("Тип SQL шаблона для форматирования не найден")
        return sql_formatters[sql_formatter]()
