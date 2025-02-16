class KeyMismatchError(Exception):
    """Исключение, возникающее при несоответствии ожидаемых и фактических ключей."""


def validate_keys(
    expected: set[any],
    expected_name: str,
    actual: set[any],
    actual_name: str,
    error_cls: type[Exception] = KeyMismatchError
) -> None:
    """
    Универсальная функция для проверки, что множество `actual` полностью
    соответствует множеству `expected`. Если есть расхождения, бросается ошибка.
    :param expected: Множество ожидаемых ключей
    :param expected_name: Название множества ожидаемых ключей
    :param actual: Множество фактических ключей
    :param actual_name: Название множества фактических ключей
    :param error_cls: Класс исключения, которое нужно бросать (по умолчанию KeyMismatchError)
    :raises KeyMismatchError (или переданный error_cls): Если есть пропущенные или лишние ключи
    """
    missing = expected - actual
    extra = actual - expected

    if not missing and not extra:
        return

    messages = []
    if missing:
        messages.append(f"Отсутствуют ключи в {expected_name}: {', '.join(missing)}")
    if extra:
        messages.append(f"Лишние ключи в {actual_name}: {', '.join(extra)}")

    raise error_cls(" | ".join(messages))
