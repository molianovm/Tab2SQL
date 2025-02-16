VALUE_FORMATTER_ERRORS = []


def log_error(logger: list[str] | None, message: str) -> None:
    """
    Записывает ошибку в лог нужный логгер.
    :param logger: Список, куда добавляется сообщение.
    :param message: Сообщение об ошибке.
    """
    logger.append(message)
