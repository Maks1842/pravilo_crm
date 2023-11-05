'''
Модуль формирования документов .txt
'''
import os
from datetime import datetime

from src.config import generator_txt_path


async def paymant_order_txt(credits_list, date, number_seq, session):

    if date:
        date_text = datetime.strptime(str(date), "%Y-%m-%d").strftime("%d.%m.%Y")
    else:
        current_date = datetime.now()
        date_text = current_date.strftime("%d.%m.%Y")

    number = int(number_seq)

    for item in credits_list:

        path_file = os.path.join(generator_txt_path, f'ПП_{number}_{date_text}.txt')

        with open(path_file, 'w+') as file:

            file.write('1CClientBankExchange\n')
            file.write('СекцияДокумент=Платежное поручение\n')
            file.write(f'Номер={str(number)}\n')
            file.write(f'Дата={date_text}\n')
            file.write('Сумма=16301.00\n')
            file.write('ПлательщикСчет=40702810000000000000\n')
            file.write('Плательщик=ИНН 0579400000 Тест АЛБО № 16437\n')
            file.write('ПлательщикИНН=0579400000\n')
            file.write('ПлательщикКПП=037012360\n')
            file.write('Плательщик1=Тест АЛБО № 16437\n')
            file.write('ПлательщикБанк1=ФИЛИАЛ "ЕКАТЕРИНБУРГСКИЙ" АО "АЛЬФА-БАНК"\n')
            file.write('ПлательщикБанк2=г. Екатеринбург\n')
            file.write('ПлательщикБИК=046500000\n')
            file.write('ПлательщикКорсчет=30101810000000000000\n')
            file.write('ПолучательСчет=40817810000000000000\n')
            file.write('Получатель=Иванов Иван Иванович\n')
            file.write('ПолучательИНН=000000000000\n')
            file.write('ПолучательКПП=0\n')
            file.write('Получатель1=Иванов Иван Иванович\n')
            file.write('ПолучательРасчСчет=40817810000000000000\n')
            file.write('ПолучательБанк1=АО "АЛЬФА-БАНК"\n')
            file.write('ПолучательБанк2=Г МОСКВА\n')
            file.write('ПолучательБИК=044500000\n')
            file.write('ВидОплаты=01\n')
            file.write('Очередность=5\n')
            file.write('НазначениеПлатежа=//ВЗС//5000-00// Test16.03 НДС не облагается\n')
            file.write('НазначениеПлатежа1=//ВЗС//5000-00// Test16.03 НДС не облагается\n')
            file.write('Код=0\n')
            file.write('КодНазПлатежа=\n')
            file.write('КонецДокумента\n')
            file.write('КонецФайла')

        number += 1

    return {
        'status': 'success',
        'data': None,
        'details': 'Данные для ПП сформированы'
    }