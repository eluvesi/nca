import sys
import os

def resource_path(relative_path):
    """Возвращает абсолютный путь до ресурса. Работает и при запуске через терминал, и при запуске .exe-файла."""
    if hasattr(sys, '_MEIPASS'):
        # При запуске из .exe-файла
        return os.path.join(sys._MEIPASS, relative_path)
    # При обычном запуске через терминал
    return os.path.join(os.path.abspath("."), relative_path)
