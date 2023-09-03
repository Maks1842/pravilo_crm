'''
Это Основной модуль для формирования документов .docx.

В моделе Print_Form_Variables хранятся переменные-тэги применяемые в шаблоне, индексы Сущностей к которым относятся переменные-тэги,
а также ключи-Полей которым относятся соответствующие переменные-тэги.

В шаблоне .docx индексация осуществляется по тегам. Пример: {{Адрес_должника}}, {{Номер_КД}};
если необходимо склонение, то - {{Должник_дат}}

nomn - именительный -- Кто? Что?
gent - родительный -- Кого? Чего?
datv - дательный -- Кому? Чему?
accs - винительный -- Кого? Что?
ablt - творительный -- Кем? Чем?
loct - предложный -- О ком? О чём?

!!! Склоняются переменные, для которых в Моделе Print_Form_Variables проставленные значения в поле declension_entity_id.
Значения в поле declension_entity_id указывают, какие правили склонения применяются
'''
import re
import os
from datetime import datetime
import random

from sqlalchemy import select

from src.creating_docs.models import docs_generator_variable
from src.registries.models import registry_headers


async def select_from_variables(credits_data, template, session):
    context_dict = {}
    context = {}
    count_debt = 0
    # print(f'{credits_data=}')

    variables_query = await session.execute(select(docs_generator_variable))
    variables_list = variables_query.mappings().all()

    print(f'{variables_list=}')

    count = 1455
    for data in credits_data['data_debtors']:
        print(f'credits_data {data}')
        num_random = random.randint(10, 6500)
        num_random_2 = random.randint(1100, 2600)
        num_random_3 = random.randint(1000, 2500)
        count += 1

        for var in variables_list:
            reg_head_id = int(var['registry_headers_id'])
            headers_key_query = await session.execute(select(registry_headers.c.headers_key).where(registry_headers.c.id == reg_head_id))
            headers_key = headers_key_query.scalar()

            var_dict = dict(var)
            var_dict['headers_key'] = headers_key
            try:
                count_debt += 1
                if var['entity_id'] == 1:
                    pass
                    # declension_regular = Print_Form_Declension.objects.filter(entity_name_id=1).values()
            #
            #         text = {'text': data[var['fields_key']], 'gender': data['pol']}
            #         result_decl = declension(text, declension_regular)
#
#                     context = { f'{var["variables"]}': f'{result_decl[0]}',
#                                 f'{var["variables"]}_им': f'{result_decl[0]}',
#                                 f'{var["variables"]}_род': f'{result_decl[1]}',
#                                 f'{var["variables"]}_дат': f'{result_decl[2]}',
#                                 f'{var["variables"]}_вин': f'{result_decl[3]}',
#                                 f'{var["variables"]}_твор': f'{result_decl[4]}',
#                                 f'{var["variables"]}_пред': f'{result_decl[5]}',
#                                 f'Случайный_номер': f'{num_random}',
#                                 f'Случайный_номер_2': f'{num_random_2}',
#                                 f'Случайный_номер_3': f'{num_random_3}',
#                                 }
#                     context_dict.update(context)
#
#                 elif var['declension_entity_id'] == 2:
#                     declension_regular = Print_Form_Declension.objects.filter(entity_name_id=2).values()
#
#                     text = {'text': data[var['fields_key']], 'gender': None}
#                     result_decl = declension(text, declension_regular)
#
#                     context = { f'{var["variables"]}': f'{result_decl[0]}',
#                                 f'{var["variables"]}_им': f'{result_decl[0]}',
#                                 f'{var["variables"]}_род': f'{result_decl[1]}',
#                                 f'{var["variables"]}_дат': f'{result_decl[2]}',
#                                 f'{var["variables"]}_вин': f'{result_decl[3]}',
#                                 f'{var["variables"]}_твор': f'{result_decl[4]}',
#                                 f'{var["variables"]}_пред': f'{result_decl[5]}',
#                                 f'Случайный_номер': f'{num_random}',
#                                 f'Случайный_номер_2': f'{num_random_2}',
#                                 f'Случайный_номер_3': f'{num_random_3}',
#                                 }
#                     context_dict.update(context)
#
                else:
                    if data[var['fields_key']] is not None and data[var['fields_key']] != '':
                        if re.findall(r'\d{4}-\d{2}-\d{2}$', str(data[var["fields_key"]])):
                            context[f'{var["variables"]}'] = f'{datetime.strptime(str(data[var["fields_key"]]), "%Y-%m-%d").strftime("%d.%m.%Y")}'
                        else:
                            context[f'{var["variables"]}'] = f'{data[var["fields_key"]]}'
                    else:
                        context[f'{var["variables"]}'] = "{{ " + f'{var["variables"]}' + " }}"
#
#                     context_dict.update(context)
            except Exception as ex:
                print(f'{ex=}')

#         doc_pattern(context_dict, count, template)
#
#     return {'message': f'Документы сформированы.'}
#
#
# def doc_pattern(context_dict, count, template):
#     try:
#         doc = DocxTemplate(f'media/{template["template_file"]}')
#         name = context_dict.get('Должник')
#         num_credit = context_dict.get('номер_КД')
#         num = re.sub(r'/', '_', num_credit)
#         path = os.path.join('media/result', template["template_name"])
#
#         if not os.path.exists(path):
#             os.mkdir(path)
#
#         doc.render(context_dict)
#         doc.save(f'{path}/{num}_{name}.docx')
#     except Exception as ex:
#         return Response({'error': f'Отсутствует указанный шаблон. {ex}'})