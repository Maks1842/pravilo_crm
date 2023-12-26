'''
Шаблоны RE
'''
class RePattern:
    #### Для Выписок платежей ##########
    # Формат суммы
    payment = r'\d+\.\d{2}|\d+|\d+\,\d{2}'
    # ФИО из столбца "Назначение платежа"
    pay_fio = r'(?i)[а-яА-Я]+\s+[а-яА-Я]+\s+[а-яА-Я]{4,}'
    # ФИО из столбца "Назначение"
    pay_fio_ufk = r'(?i)((?<= с )|(?<=должник )|(?<=:)|(?<=: ))\D\w+ \w+ \w+|\D\w+ \w+ \w+ оглы(?= исполнительный| судебный|\(|\,|\.| \d{6}\,| ИП| Россия| biz| по)'
    pay_fio_osfr = r'(?i)(?<=\d )\D\w+ \w+ \w+'
    executive_document = r'(?i)(((?<=судебный приказ )|(?<=с/п ))[\d-]+\/[\d-]+)|(((?<=\№)|(?<=N))[\d\w-]+\/[\d-]+)|(((?<=\№ )|(?<=N ))[\d\w-]+\/[\d-]+)'
    ispol_list = '(?i)((?<=фс )\d{9})|((?<=фс №)\d{9})|((?<=фс № )\d{9})|((?<=фс№)\d{9})'
    number_case = r'(?i)\S+-ИП'
    department_ufk = r'(?i)(?<=\().+(?=\))'
    department_bank = r'(?i)(?<=\d )\D.+(?= /)'

    #### Для Мемориальных ордеров ##########
    # Сумма
    payment_memori = r'(^\d+\-\d+$)|(^\d+$)'
    # ФИО
    pay_fio_memori = r'(?i)^[\w\s]+(?=\_продан)'