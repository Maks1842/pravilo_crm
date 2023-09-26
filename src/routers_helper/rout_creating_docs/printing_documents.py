import os
from src.config import printer_user
import time

# Модуль работает с документами pdf
def printing_docs(path_docs):
    for path in path_docs:
        os.system(f"lpr -P {printer_user} {path}")
        time.sleep(1)
