from dotenv import load_dotenv
import os

load_dotenv()

DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')

SECRET_KEY_auth = os.environ.get('SECRET_KEY_auth')
SECRET_KEY_register = os.environ.get('SECRET_KEY_register')

main_dossier_path = '/media/maks/Новый том/Python/work/fast_api/pravilo_crm/Цессии_досье'
logging_path = '/media/maks/Новый том/Python/work/fast_api/pravilo_crm/src/media/logs'
generator_docs_path = '/media/maks/Новый том/Python/work/fast_api/pravilo_crm/src/media/generator_docs/'