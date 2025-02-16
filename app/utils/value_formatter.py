import re
from datetime import datetime

from utils.errors import UnknownColumnTypeError, FailedValueFormattingError
from utils.keys_validator import validate_keys


class ValueFormatter:
    """
    Класс для форматирования значений.
    :param value: Входное значение для форматирования
    """

    def __init__(self, value: any) -> None:
        self.value = value

    def str_formatter(self) -> str:
        """
        Форматирует значение как строку с одинарными кавычками
        :return: Форматированное строковое значение
        """
        return f"'{str(self.value).strip()}'"

    def str_r_formatter(self) -> str:
        """
        Форматирует значение как строку, преобразуя числовые типы по необходимости
        :return: Форматированное строковое значение с округлением числовых значений
        """
        try:
            self.value = float(self.value)
            self.value = self._get_round_value()
        finally:
            return f"'{str(self.value).strip()}'"

    def int_formatter(self) -> str:
        """
        Преобразует значение в целое число
        :return: Форматированное целое число
        """
        return str(int(float(self.value)))

    def float_formatter(self) -> str:
        """
        Преобразует значение в число с плавающей точкой
        :return: Форматированное число с плавающей точкой без округления
        """
        return str(float(self.value))

    def float_r_formatter(self) -> str:
        """
        Преобразует значение в число с плавающей точкой, округляя, если оканчивается на .0
        :return: Форматированное число с плавающей точкой с округлением
        """
        self.value = float(self.value)
        self.value = self._get_round_value()
        return str(self.value)

    def date_formatter(self) -> str | None:
        """
        Преобразует значение в дату в формате 'YYYY-MM-DD'::DATE
        :return: Форматированная дата или None
        """
        return self._date_formatter_template(output_date_format="%Y-%m-%d", output_type="DATE")

    def timestamp_formatter(self) -> str | None:
        """
        Преобразует значение в TIMESTAMP в формате 'YYYY-MM-DD HH:MM:SS'::TIMESTAMP
        :return: Форматированная дата или None
        """
        return self._date_formatter_template(output_date_format="%Y-%m-%d %H:%M:%S", output_type="TIMESTAMP")

    def func_formatter(self) -> str | None:
        """
        Если строка имеет формат функции, то возвращается строка без кавычек
        :return: Строка с форматом функции без кавычек
        """
        value = str(self.value).strip()
        pattern = r'.*\(.*\)\s*$'
        if re.match(pattern, value):
            return f"{value}"

    def bool_formatter(self) -> str | None:
        """
        Преобразует булево значение в SQL-формат, если это возможно
        :return: 'TRUE' или 'FALSE'
        """
        value = str(self.value).strip().lower()
        true_values = {'true', 'yes', 'y', 'да', '1', '1.0'}
        false_values = {'false', 'no', 'n', 'нет', '0', '0.0'}
        if value in true_values:
            return "TRUE"
        elif value in false_values:
            return "FALSE"

    def _get_round_value(self) -> int | float:
        """
        Возвращает округленное значение, если значение оканчивается на .0
        :return: Округленное значение
        """
        return int(self.value) if self.value == int(self.value) else self.value

    def _date_formatter_template(self, output_date_format: str, output_type: str) -> str | None:
        """
        Шаблон для преобразования даты
        :param output_date_format: Формат даты для SQL
        :param output_type: Тип даты для форматирования SQL
        :return: Форматированная дата или None
        """
        date_formats = [
            '%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d',
            '%d.%m.%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%Y/%m/%d %H:%M:%S'
        ]
        for date_format in date_formats:
            try:
                date_sting = datetime.strptime(str(self.value).strip(), date_format)
                return f"'{date_sting.strftime(output_date_format)}'::{output_type}"
            except ValueError:
                continue


class ValueFormatterFactory:
    """
    Фабрика для получения функции форматирования по типу колонки.
    """
    VALID_FORMATTER_TYPES: dict[str, str] = {
        "str": "STRING",
        "str_r": "STRING (R)",
        "int": "INTEGER",
        "float": "FLOAT",
        "float_r": "FLOAT (R)",
        "date": "DATE",
        "timestamp": "TIMESTAMP",
        "func": "FUNCTION",
        "bool": "BOOLEAN",
    }

    @property
    def types(self) -> dict[str, str]:
        """
        Возвращает список возможных типов колонок
        :return: Список возможных типов колонок
        """
        return self.VALID_FORMATTER_TYPES

    def get_value(self, column_type: str, input_value: any) -> str:
        """
        Возвращает функцию форматирования значения по типу колонки
        :param column_type: Тип в котором нужно произвести форматирование
        :param input_value: Входное значение для форматирования
        :return: Отформатированное значение в виде строки
        :raises KeyMismatchError: Если колонка не соответствует списку возможных типов
        :raises UnknownColumnTypeError: Если передан неизвестный тип колонки
        :raises FailedValueFormattingError: Если не удалось преобразовать значение
        """
        formatters = {
            "str": ValueFormatter(input_value).str_formatter,
            "str_r": ValueFormatter(input_value).str_r_formatter,
            "int": ValueFormatter(input_value).int_formatter,
            "float": ValueFormatter(input_value).float_formatter,
            "float_r": ValueFormatter(input_value).float_r_formatter,
            "date": ValueFormatter(input_value).date_formatter,
            "timestamp": ValueFormatter(input_value).timestamp_formatter,
            "func": ValueFormatter(input_value).func_formatter,
            "bool": ValueFormatter(input_value).bool_formatter,
        }
        validate_keys(
            expected=set(self.types.keys()),
            expected_name="types",
            actual=set(formatters.keys()),
            actual_name="formatters"
        )
        type_ = column_type.lower()
        if type_ not in formatters:
            raise UnknownColumnTypeError(f"Неизвестный тип колонки: {column_type}")
        try:
            returned_value = formatters[type_]()
            if returned_value is None:
                raise FailedValueFormattingError(
                    f"Не удалось преобразовать значение {input_value} в тип {self.types[type_]}"
                )
            return formatters[type_]()
        except ValueError:
            return "NULL"
        except FailedValueFormattingError:
            return "NULL"
