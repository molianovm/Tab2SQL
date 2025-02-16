# load_data.py
class LoadDataError(Exception):
    """Базовый класс для всех исключений в load_data."""


class PathNotProvidedError(LoadDataError):
    """Путь к файлу не указан."""


class FileDoesNotExistError(LoadDataError):
    """Файл отсутствует или недоступен."""


class UnknownFileExtensionError(LoadDataError):
    """Расширение файла не поддерживается."""


class DataFrameLoadError(LoadDataError):
    """DataFrame пустой."""


class CSVParseError(LoadDataError):
    """Ошибка парсинга CSV."""


class CSVDelimiterNotProvidedError(LoadDataError):
    """Разделитель CSV не указан."""


class CSVIsEmptyError(LoadDataError):
    """CSV пустой."""


class ExcelSheetNotFoundError(LoadDataError):
    """Лист Excel не найден."""


# data_processing.py
class DataProcessingError(Exception):
    """Базовый класс для всех исключений в data_processing."""


class TypeNotFoundError(DataProcessingError):
    """Тип столбца не найден."""


# value_formatter.py
class ValueFormatterError(Exception):
    """Базовый класс для всех исключений в value_formatter."""


class UnknownColumnTypeError(ValueFormatterError):
    """Тип столбца не поддерживается."""


class FailedValueFormattingError(ValueFormatterError):
    """Ошибка форматирования значения."""


# sql_formatter.py
class SQLFormatterError(Exception):
    """Базовый класс для всех исключений в sql_formatter."""


class SQLFormatterNotFoundError(SQLFormatterError):
    """Тип форматирования для SQL не найден."""
