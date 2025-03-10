import os
import sys


def resource_path(relative_path):
    """ Возвращает корректный путь для ресурсов при упаковке с PyInstaller """
    try:
        # PyInstaller создает временную папку и хранит путь в _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("./app/")

    return os.path.join(base_path, relative_path)
