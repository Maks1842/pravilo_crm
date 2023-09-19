from dotenv import load_dotenv
import os
import pathlib

load_dotenv()

DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')

SECRET_KEY_auth = os.environ.get('SECRET_KEY_auth')
SECRET_KEY_register = os.environ.get('SECRET_KEY_register')

path_main = pathlib.Path().resolve()

main_dossier_path = f'{path_main}/Цессии_досье'
logging_path = f'{path_main}/src/media/logs'
generator_docs_path = f'{path_main}/src/media/generator_docs'
