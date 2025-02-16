class Column:
    """
    Класс для хранения информации о колонке таблицы

    :param column_name: Имя колонки
    :param column_type: Тип колонки
    :param new_name: Новое имя колонки (если None, то будет использоваться column_name)
    :param new_type: Новый тип колонки (если None, то будет использоваться column_type)
    :param include: Флаг, указывающий, должна ли колонка быть включена в результирующую таблицу
    """

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
