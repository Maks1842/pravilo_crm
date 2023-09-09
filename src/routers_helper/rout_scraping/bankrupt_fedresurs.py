import requests
import json
import fake_useragent
import openpyxl
import re
from src.routers_helper.data_to_excel.bancrupt_to_excel import bankrupt_to_excel

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 'accept': '*/*'}      #User_Agent генерируется, чтобы сайт понимал, что к ниму обращается человек, а не бот
HOST = 'https://bankrot.fedresurs.ru/'
user = fake_useragent.UserAgent().random            #Можно рандомной генерации User_Agent

header = {
    'user-agent': user
}

def parse():

    path_file = '/media/maks/Новый том/Python/work/fast_api/pravilo_crm/src/media/data/test_bankrupt.xlsx'

    list_inn = extract_inn_xlsx(path_file)

    url_main = f'https://bankrot.fedresurs.ru/bankrupts'

    html_main = get_html(url_main)
    cookies = html_main.cookies

    result = []
    for inn in list_inn:
        url = f'https://bankrot.fedresurs.ru/backend/prsnbankrupts?searchString={inn}&limit=15&offset=0'
        my_referer = f'https://bankrot.fedresurs.ru/bankrupts?searchString={inn}'

        r = requests.get(url, cookies=cookies, headers={'referer': my_referer})
        dict_data = json.loads(r.text)

        if len(dict_data['pageData']) > 0:
            data = dict_data['pageData'][0]

            guid = f'https://fedresurs.ru/backend/persons/{data["guid"]}'
            guid_referer = f'https://fedresurs.ru/person/{data["guid"]}'
            gdx = requests.get(guid, headers={'referer': guid_referer})
            guid_data = json.loads(gdx.text)

            try:
                name_histories = guid_data['info']['nameHistories'][0]
            except:
                name_histories = ''

            try:
                snils = guid_data['info']['snils']
            except:
                snils = ''

            result.append({
                'full_name': guid_data['info']['fullName'],
                'name_histories': name_histories,
                'birthdate_bankrupt': guid_data['info']['birthdateBankruptcy'],
                'birth_place_bankrupt': guid_data['info']['birthplaceBankruptcy'],
                'address': guid_data['info']['address'],
                'inn': inn,
                'snils': snils,
                'number_legal_cases': guid_data['legalCases'][0]['number'],
                'tribunal': guid_data['legalCases'][0]['courtName']})

    bankrupt_to_excel(result)

'''
Функция проверяет отвечает ли сайт на наш запрос.
Применяется если нет необходимости проходить авторизацию на сайте
'''
def get_html(url, params=None):
    d = requests.get(url, headers=HEADERS, params=params)
    return d


def extract_inn_xlsx(path_file):
    result = []

    book = openpyxl.load_workbook(path_file)
    sheet = book.active

    inn_cel = 0
    for row in range(1, (sheet.max_row + 1)):
        for cell in range(1, sheet.max_column):
            if re.findall(r'inn', str(sheet[row][cell].value)):
                inn_cel = cell
        inn = sheet[row][inn_cel].value
        try:
            inn = re.sub(r'^[\s-]+|\s+$|\n+|^\s+', '', inn)
        except:
            inn = inn
        result.append(str(inn))

    return result

# parse()