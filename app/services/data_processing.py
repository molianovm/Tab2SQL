import pandas as pd

from services.load_data import load_data
from utils.errors import TypeNotFoundError


class DataProcessing:
    """
    Класс для обработки данных.
    """

    @staticmethod
    def convert_value(value):
        """
        Преобразование значения с конвертацией даты/времени.
        Если pd.to_datetime не справляется (например, дата вне диапазона), то пробуем вручную через datetime.strptime.
        :param value: Значение для преобразования.
        :return: Преобразованное значение.
        """
        return value


class Table:
    def __init__(self, name, columns, data):
        self.name = name
        self.columns = columns if columns else []
        self.data = data

    def __repr__(self):
        return f"Table(name={self.name}, columns={self.columns}, data={self.data})"


class Column:
    def __init__(
        self,
        column_name: str,
        column_type: str,
        new_name: str | None = None,
        new_type: str | None = None,
        include: bool = True
    ):
        self.column_name = column_name
        self.column_type = column_type
        self.new_name = new_name if new_name else column_name.lower()
        self.new_type = new_type if new_type else column_type.lower()
        self.include = include

    def __repr__(self):
        return (f"Column(name={self.column_name}, type={self.column_type}, new_name={self.new_name}, new_type="
                f"{self.new_type}, include={self.include})")


def _type_determinator(input_type: str) -> str:
    type_matching = {
        "object": "str",
        "bool": "bool",
        "int64": "int",
        "float64": "float_r",
        "datetime64[ns]": "datetime"
    }
    if input_type in type_matching.keys():
        return type_matching[input_type]
    raise TypeNotFoundError(f"Тип {input_type} не определен")

def _get_table(dataframe: pd.DataFrame, table_name: str = "table") -> Table:
    columns = []
    for column in dataframe.columns:
        column_type = str(dataframe[column].dtype)
        columns.append(Column(column_name=column, column_type=_type_determinator(column_type)))
    return Table(table_name, columns, dataframe)

def value_converter(column_type: str, value: any) -> str:
    if value == 'NULL':
        return 'NULL'
    if column_type == "str":
        return f"'{value}'"
    if column_type == "int":
        return str(int(value))
    if column_type == "float_r":
        return str(float(value))
    if column_type == "datetime":
        return f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'::TIMESTAMP"
    return value

def _get_actual_columns(table: Table) -> list[str]:
    return [column.new_name for column in table.columns if column.include]

def _get_actual_values(table: Table) -> list[str]:
    values = []
    for _, row in table.data.iterrows():
        row_values = []
        for col in table.columns:
            if col.include:
                row_values.append(value_converter(col.new_type, row[col.column_name]))
        values.append(f"({', '.join(row_values)})")
    return values

def get_sql(table_name: str, columns: list[str], values: list[str]) -> str:
    return f"INSERT INTO {table_name} ({columns}) VALUES\n" + ",\n".join(values) + ";"

if __name__ == "__main__":
    # df = load_data("../test_data/data.csv", delimiter=";")
    df = load_data("../test_data/data.xlsx")
    table_data = _get_table(df)
    table_data.columns[0].new_name = "id"
    table_data.columns[1].new_type = "datetime"
    columns_sql = _get_actual_columns(table_data)
    values_sql = _get_actual_values(table_data)
    print(columns_sql)
    print(values_sql)

    sql_statement = get_sql(table_data.name, columns_sql, values_sql)

    # print(sql_statement)
