import os
from abc import ABC, abstractmethod

import pandas as pd

from utils.errors import (
    FileDoesNotExistError,
    UnknownFileExtensionError,
    PathNotProvidedError,
    DataFrameLoadError,
    CSVParseError,
    CSVDelimiterNotProvidedError,
    CSVIsEmptyError,
    ExcelSheetNotFoundError
)


class LoadData(ABC):
    """
    Базовый абстрактный класс для загрузки данных из файла.
    :param file_path: Путь к файлу для чтения.
    """

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    @abstractmethod
    def get_data(self, **kwargs) -> pd.DataFrame:
        """
        Абстрактный метод для получения данных в формате DataFrame.
        :param kwargs: Дополнительные параметры для настройки процесса загрузки.
        :return: DataFrame с загруженными данными.
        :raises NotImplementedError: Если метод не переопределён в подклассе.
        """
        pass


class LoadCSV(LoadData):
    """
    Класс для загрузки данных из CSV-файла.
    """

    def get_data(self, header: bool = True, delimiter: str = ',') -> pd.DataFrame:
        """
        Возвращает содержимое CSV-файла в виде DataFrame.
        :param header: Указывает, есть ли в файле строка заголовка.
                       Если False, заголовки будут созданы автоматически.
        :param delimiter: Разделитель CSV-файла (по умолчанию ",").
        :return: Загруженные данные в формате DataFrame.
        :raises CSVDelimiterNotProvidedError: Если не указан разделитель (delimiter).
        :raises CSVParseError: Если произошла ошибка при парсинге CSV (например, некорректные данные).
        :raises CSVIsEmptyError: Если CSV-файл пустой.
        """
        if not delimiter:
            raise CSVDelimiterNotProvidedError("Разделитель CSV не указан")
        try:
            csv_header = 0 if header else None
            df = pd.read_csv(self.file_path, header=csv_header, delimiter=delimiter)
            if not header:
                df.columns = [f"column{i + 1}" for i in range(df.shape[1])]
            return df
        except pd.errors.ParserError as e:
            raise CSVParseError(f"Ошибка при попытке парсинга CSV: {e}")
        except pd.errors.EmptyDataError as e:
            raise CSVIsEmptyError(f"Отсутствуют данные в CSV")


class LoadExcel(LoadData):
    """
    Класс для загрузки данных из Excel-файла.
    """

    def _validate_sheet(self, sheet_name: str | int) -> None:
        """
        Проверка существования листа в Excel-файле.
        :param sheet_name: Имя листа (str) или индекс листа (int)
        :raises ExcelSheetNotFoundError: Если лист с указанным именем или индексом не найден.
        """
        xlsx = pd.ExcelFile(self.file_path)
        valid_sheets = xlsx.sheet_names
        if sheet_name is None:
            raise ExcelSheetNotFoundError("Имя листа не указано")
        if isinstance(sheet_name, int) and not (0 <= sheet_name < len(valid_sheets)):
            raise ExcelSheetNotFoundError(f"Лист с индексом {sheet_name} не найден в Excel-файле")
        if isinstance(sheet_name, str) and sheet_name not in valid_sheets:
            raise ExcelSheetNotFoundError(f"Лист с именем {sheet_name} не найден в Excel-файле")

    def get_data(self, sheet_name: str | int = 0) -> pd.DataFrame:
        """
        Возвращает содержимое Excel-файла в виде DataFrame.
        :param sheet_name: Имя листа (str) или индекс листа (int).
                           По умолчанию 0 (первый лист).
        :return: Загруженные данные в формате DataFrame.
        """
        self._validate_sheet(sheet_name)
        df = pd.read_excel(self.file_path, sheet_name=sheet_name)
        return df


def _validate_file_path(file_path: str) -> None:
    """
    Проверка существования файла по указанному пути.
    :param file_path: Путь к файлу для загрузки.
    """
    if not file_path:
        raise PathNotProvidedError("Путь к файлу не указан")
    if not os.path.exists(file_path):
        raise FileDoesNotExistError(f"Файл не найден по пути: {file_path}")


def _get_extension(file_path: str, supported_extensions: dict[str, type]) -> str:
    """
    Определяет расширение файла по его пути.
    :param file_path: Путь к файлу для загрузки.
    :param supported_extensions: Поддерживаемые расширения файлов.
    :return: Расширение файла на основе его пути.
    """
    _validate_file_path(file_path)
    extension = os.path.splitext(file_path)[1].lower()
    if extension not in supported_extensions:
        raise UnknownFileExtensionError(f"Неподдерживаемое расширение файла: {extension}")
    return extension


def load_data(file_path, **kwargs):
    """
    Загружает данные из файла в формате DataFrame.
    :param file_path: Путь к файлу для загрузки.
    :param kwargs: Дополнительные параметры, передаваемые в метод `get_data()`
                   (например, `delimiter` для CSV или `sheet_name` для Excel).
    :return: Загруженные данные в формате DataFrame, с заполнением NaN значением "NULL".
    :raises DataFrameLoadError: Если не удалось загрузить данные (loader вернул None).
    """
    supported_types = {
        '.csv': LoadCSV,
        '.xlsx': LoadExcel,
        '.xls': LoadExcel
    }
    extension = _get_extension(file_path, supported_types)

    loader_class = supported_types[extension]
    loader = loader_class(file_path)

    df = loader.get_data(**kwargs)
    if df is None:
        raise DataFrameLoadError("Не удалось загрузить данные")
    return df.fillna("NULL")
