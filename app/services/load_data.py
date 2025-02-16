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
        self._filename = None

    @property
    def filename(self) -> str:
        """
        Возвращает имя для таблицы загруженных данных на основе его пути (без расширения).
        :return: Имя файла без расширения.
        """
        return os.path.basename(self.file_path).split('.')[0]

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
        except pd.errors.EmptyDataError:
            raise CSVIsEmptyError(f"Отсутствуют данные в CSV")


class LoadExcel(LoadData):
    """
    Класс для загрузки данных из Excel-файла.
    """

    def __init__(self, file_path: str):
        super().__init__(file_path)
        self._sheet_name: str | int | None = None

    @property
    def filename(self) -> str:
        """
        Возвращает имя Excel-файла на основе выбранного листа.
        :return: Строка с именем для таблицы.
        """
        return self._sheet_name

    def get_data(self, sheet_name: str | int = 0) -> pd.DataFrame:
        """
        Возвращает содержимое Excel-файла в виде DataFrame.
        :param sheet_name: Имя листа (str) или индекс листа (int).
                           По умолчанию 0 (первый лист).
        :return: Загруженные данные в формате DataFrame.
        """
        self._sheet_name = self._get_sheet_name(sheet_name)
        return pd.read_excel(self.file_path, sheet_name=self._sheet_name)

    def _get_sheet_name(self, sheet_name: str | int) -> str:
        """
        Возвращает имя Excel-файла на основе выбранного листа (по индексу или имени).
        :param sheet_name: Имя листа (str) или индекс листа (int).
        :return: Имя листа (str).
        """
        xlsx = pd.ExcelFile(self.file_path)
        valid_sheets = xlsx.sheet_names
        self._validate_sheet(sheet_name, valid_sheets)
        if isinstance(sheet_name, int):
            return valid_sheets[sheet_name]
        return sheet_name

    @staticmethod
    def _validate_sheet(sheet_name: str | int, valid_sheets: list[str]) -> None:
        """
        Проверка существования листа в Excel-файле.
        :param sheet_name: Имя листа (str) или индекс листа (int)
        :raises ExcelSheetNotFoundError: Если лист с указанным именем или индексом не найден.
        """
        if sheet_name is None:
            raise ExcelSheetNotFoundError("Имя листа не указано")
        if isinstance(sheet_name, int) and not (0 <= sheet_name < len(valid_sheets)):
            raise ExcelSheetNotFoundError(f"Лист с индексом {sheet_name} не найден в Excel-файле")
        if isinstance(sheet_name, str) and sheet_name not in valid_sheets:
            raise ExcelSheetNotFoundError(f"Лист с именем {sheet_name} не найден в Excel-файле")


class DataLoaderFactory:
    """
    Фабрика загрузчиков данных.
    """
    SUPPORTED_TYPES: dict[str, type] = {
        '.csv': LoadCSV,
        '.xlsx': LoadExcel,
        '.xls': LoadExcel
    }

    def __init__(self):
        self._file_path = None

    @property
    def types(self) -> list[str]:
        """
        Возвращает список поддерживаемых расширений для загрузки данных.
        :return: Список поддерживаемых расширений для загрузки данных.
        """
        return list(self.SUPPORTED_TYPES.keys())

    def load_data(self, file_path: str, **kwargs) -> tuple[pd.DataFrame, str]:
        """
        Функция загрузки данных из файла.
        :param file_path: Путь к файлу для чтения.
        :param kwargs: Дополнительные параметры для настройки процесса загрузки.
        :return: DataFrame с загруженными данными (с заполнением пропусков "NULL") и имя таблицы.
        """
        self._file_path = file_path
        loader = self._create_loader()
        df = loader.get_data(**kwargs)
        if df is None:
            raise DataFrameLoadError("Не удалось загрузить данные")
        return df.fillna("NULL"), loader.filename

    def _create_loader(self) -> LoadData:
        """
        Создает экземпляр загрузчика данных в зависимости от расширения файла.
        :return: Экземпляр загрузчика данных.
        """
        self._validate_file_path()
        extension = self._get_extension()
        loader_class = self.SUPPORTED_TYPES[extension]
        return loader_class(self._file_path)

    def _validate_file_path(self) -> None:
        """
        Проверка существования файла по указанному пути.
        """
        if not self._file_path:
            raise PathNotProvidedError("Путь к файлу не указан")
        if not os.path.exists(self._file_path):
            raise FileDoesNotExistError(f"Файл не найден по пути: {self._file_path}")

    def _get_extension(self) -> str:
        """
        Определяет расширение файла по его пути.
        :return: Расширение файла
        """
        extension = os.path.splitext(self._file_path)[1].lower()
        self._validate_extension(extension)
        return extension

    def _validate_extension(self, extension) -> None:
        """
        Проверка поддерживаемого расширения файла.
        :param extension: Проверяемое расширение файла
        :raises UnknownFileExtensionError: Если расширение файла не поддерживается
        """
        if extension not in self.SUPPORTED_TYPES:
            raise UnknownFileExtensionError(f"Неподдерживаемое расширение файла: {extension}")
