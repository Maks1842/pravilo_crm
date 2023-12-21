import pathlib
from variables_for_backend import SettingsApp

DB_NAME = SettingsApp.db_name
DB_USER = SettingsApp.db_user
DB_PASS = SettingsApp.db_pass
DB_HOST = SettingsApp.db_host
DB_PORT = SettingsApp.db_port

SECRET_KEY_auth = SettingsApp.secret_key_auth
SECRET_KEY_register = SettingsApp.secret_key_register

path_main = pathlib.Path().resolve()

main_dossier_path = f'{path_main}/Цессии_досье'
logging_path = f'{path_main}/src/media/logs'
generator_docs_path = f'{path_main}/src/media/generator_docs'
generator_txt_path = f'{path_main}/src/media/generator_txt'


printer_user = SettingsApp.printer_user
