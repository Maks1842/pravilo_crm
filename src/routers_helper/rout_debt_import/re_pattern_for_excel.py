'''
Шаблоны RE
'''
class RePattern:
    # Split ФИО
    fio_1 = r'\D+\w(?=\s*\()'
    fio_2 = r'(?<=\()\D+\w(?=\s*\))'

    # Split Паспорт
    passport_series = r'\d{2}\s*\d{2}'
    passport_num = r'\d{6}'
    passport_date = r'\d{2}\.\d{2}\.\d{4}'
    passport_department = r'выдан.+'

    # Split Адрес
    index_re = r'\d{6}'
    address_re = r'(?<=\s)[\w\W]+'

    # Split данные по ИП
    execut_production = r'(?i)[\d\/]+-ИП'
    consolidat_ep = r'(?i)[\d\/]+-СД'
    date_ep = r'\d{2}\.\d{2}\.\d{4}'