'''
Это Основной модуль для формирования документов .docx.

В моделе docs_generator_variable хранятся переменные-тэги применяемые в шаблоне, индексы Сущностей к которым относятся переменные-тэги,
а также ссылки на registry_headers.  В registry_headers хранятся headers_key к которым относятся соответствующие переменные-тэги.

В шаблоне .docx индексация осуществляется по тегам. Пример: {{Адрес_должника}}, {{Номер_КД}};
если необходимо склонение, то - {{Должник_дат}}

nomn - именительный -- Кто? Что?
gent - родительный -- Кого? Чего?
datv - дательный -- Кому? Чему?
accs - винительный -- Кого? Что?
ablt - творительный -- Кем? Чем?
loct - предложный -- О ком? О чём?

!!! Склоняются переменные, для которых в Моделе docs_generator_variable проставленные значения в поле entity_id.
Значения в поле entity_id указывают, какие правили склонения применяются
'''
import re
import os
from datetime import datetime
import random

from docxtpl import DocxTemplate
from src.config import generator_docs_path

from sqlalchemy import select

from src.creating_docs.models import docs_generator_variable, docs_generator_declension
from src.registries.models import registry_headers
from src.routers_helper.rout_creating_docs.declension_word import declension


async def select_from_variables(credits_data, template_json, session):
    context_dict = {}
    context = {}
    count_debt = 0
    # print(f'{credits_data=}')

    variables_query = await session.execute(select(docs_generator_variable))
    variables_list = variables_query.mappings().all()

    count = 1455
    for data in credits_data['data_debtors']:
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
                if var_dict['entity_id'] == 1:
                    declension_reg_query = await session.execute(select(docs_generator_declension).where(docs_generator_declension.c.entity_id == 1))
                    declension_regular = declension_reg_query.mappings().all()

                    text = {'text': data[var_dict['headers_key']], 'gender': data['pol']}
                    result_decl = declension(text, declension_regular)

                    context = { f'{var_dict["variables"]}': f'{result_decl[0]}',
                                f'{var_dict["variables"]}_им': f'{result_decl[0]}',
                                f'{var_dict["variables"]}_род': f'{result_decl[1]}',
                                f'{var_dict["variables"]}_дат': f'{result_decl[2]}',
                                f'{var_dict["variables"]}_вин': f'{result_decl[3]}',
                                f'{var_dict["variables"]}_твор': f'{result_decl[4]}',
                                f'{var_dict["variables"]}_пред': f'{result_decl[5]}',
                                f'Случайный_номер': f'{num_random}',
                                f'Случайный_номер_2': f'{num_random_2}',
                                f'Случайный_номер_3': f'{num_random_3}',
                                }
                    context_dict.update(context)

                elif var_dict['entity_id'] == 2:
                    declension_reg_query = await session.execute(select(docs_generator_declension).where(docs_generator_declension.c.entity_id == 2))
                    declension_regular = declension_reg_query.mappings().all()

                    text = {'text': data[var_dict['headers_key']], 'gender': None}
                    result_decl = declension(text, declension_regular)

                    context = { f'{var_dict["variables"]}': f'{result_decl[0]}',
                                f'{var_dict["variables"]}_им': f'{result_decl[0]}',
                                f'{var_dict["variables"]}_род': f'{result_decl[1]}',
                                f'{var_dict["variables"]}_дат': f'{result_decl[2]}',
                                f'{var_dict["variables"]}_вин': f'{result_decl[3]}',
                                f'{var_dict["variables"]}_твор': f'{result_decl[4]}',
                                f'{var_dict["variables"]}_пред': f'{result_decl[5]}',
                                f'Случайный_номер': f'{num_random}',
                                f'Случайный_номер_2': f'{num_random_2}',
                                f'Случайный_номер_3': f'{num_random_3}',
                                }
                    context_dict.update(context)

                else:
                    if data[var_dict['headers_key']] is not None and data[var_dict['headers_key']] != '':
                        if re.findall(r'\d{4}-\d{2}-\d{2}$', str(data[var_dict["headers_key"]])):
                            context[f'{var_dict["variables"]}'] = f'{datetime.strptime(str(data[var_dict["headers_key"]]), "%Y-%m-%d").strftime("%d.%m.%Y")}'
                            x = context[f'{var_dict["variables"]}']
                        else:
                            context[f'{var_dict["variables"]}'] = f'{data[var_dict["headers_key"]]}'
                    else:
                        context[f'{var_dict["variables"]}'] = "{{ " + f'{var_dict["variables"]}' + " }}"

                    context_dict.update(context)
            except Exception as ex:
                print(f'{ex=}')

        doc_pattern(context_dict, count, template_json)

    return {
        'status': 'success',
        'data': None,
        'details': 'Документы сформированы'
    }


def doc_pattern(context_dict, count, template_json):
    try:
        doc_path = os.path.join(generator_docs_path, template_json["value"]["path_template_file"])
        doc = DocxTemplate(doc_path)
        name = context_dict['Должник']
        num_credit = context_dict['Номер_КД']
        num = re.sub(r'/', '_', num_credit)
        result_path = os.path.join(generator_docs_path, f'result/{template_json["template_name"]}')

        if not os.path.exists(result_path):
            os.mkdir(result_path)

        doc.render(context_dict)
        doc.save(f'{result_path}/{num}_{name}.docx')
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f'Отсутствует указанный шаблон. {ex}'
        }