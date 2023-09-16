import json
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from selenium.webdriver.common.keys import Keys



'''
Изхвлечение с сайта ГАС Правосудие судов в которые можно подать заявление через https://ej.sudrf.ru/
'''
def sudrf_auth():
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")

    # options = webdriver.FirefoxOptions()
    # options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0")

    # Бот работает в фоновом режиме
    # options.add_argument('--headless')

    s = Service(executable_path="/media/maks/Новый том/Python/work/fast_api/pravilo_crm/webdriver/chromedriver/chromedriver")
    driver = webdriver.Chrome(
        service=s,
        options=options
    )

    # Драйвер для Firefox
    # driver = webdriver.Firefox(
    #     executable_path="./data/gosuslugi/webdriver/firefoxdriver/geckodriver-v0.32.0-linux64/geckodriver",
    #     options=options
    # )

    # try:
    driver.implicitly_wait(60)

    driver.set_window_size(1800, 1000)

    driver.get("https://ej.sudrf.ru/appeal")

    time.sleep(40)

    tribunal_json = {}
    tribunal_json['tribunal'] = []
    for i in range(1, 96):

        if i < 10:
            i = '0' + str(i)

        url_page = f"https://ej.sudrf.ru/api/appeal/getCourtsInRegion?regionCode={i}"

        driver.get(url_page)

        answer_list = json.loads(driver.find_element(By.TAG_NAME, 'body').text)
        if len(answer_list['data']) > 0 and answer_list['data'] is not None:
            for item in answer_list['data']:
                tribunal_json['tribunal'].append({
                    'class_code': item['VNKOD'],
                    'name': item['ZNACHATR'],
                    'address': item['ADRESS'],
                    'gaspravosudie': True})

        time.sleep(1)

    path_file = '/home/maks/Загрузки/data.json'
    with open(path_file, 'w') as file:
        json.dump(tribunal_json, file, ensure_ascii=False)

    print('Готово')
    return

# sudrf_auth()