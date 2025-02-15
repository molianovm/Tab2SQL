import logging


def get_logger(name: str = "default") -> logging.Logger:
    """
    Создает и возвращает логгер с заданным именем.

    :param name: Имя логгера. По умолчанию "default".
    :return: Объект логгера.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt='%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
