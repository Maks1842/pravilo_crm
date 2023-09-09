from sqlalchemy import select, insert, update, desc
from src.legal_work.models import legal_work


async def number_case_legal(data, session):
    legal_section = str(data['legalSection_id']).zfill(2)
    legal_num = data['legalNumber']
    if data['legalNumber'] == None:
        try:
            legal_section_id: int = data['legalSection_id']
            legal_work_query = await session.execute(select(legal_work).where(legal_work.c.legal_section_id == legal_section_id).order_by(desc(legal_work.c.id)))
            legal_work_set = legal_work_query.mappings().fetchone()

            if len(legal_work_set['legal_number']) > 0:
                legal_number_split = legal_work_set['legal_number'][3:]
                legal_number_body = str(int(legal_number_split) + 1).zfill(7)
                legal_num = f'{legal_section}/{legal_number_body}'
        except:
            legal_num = f'{legal_section}/0000001'

    return legal_num


async def save_case_legal(case_id: int, legal_data, session):
    try:
        if case_id:
            post_data = update(legal_work).where(legal_work.c.id == case_id).values(legal_data)
        else:
            post_data = insert(legal_work).values(legal_data)

        await session.execute(post_data)
        await session.commit()
    except Exception as ex:
        return {
            "status": "error",
            "data": None,
            "details": f"Ошибка при добавлении/изменении судебного кейса. {ex}"
        }
    return {
        'status': 'success',
        'data': None,
        'details': 'Судебный кейс успешно сохранен'
    }