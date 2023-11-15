from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.debts.models import credit, debtor
from src.references.models import ref_tribunal
from src.mail.routers.outgoing_mail import save_outgoing_mail



# Добавить исходящую корреспонденцию из Общего реестра
router_reg_outgoing_mail = APIRouter(
    prefix="/v1/RegistryOutgoingMail",
    tags=["Registries"]
)


@router_reg_outgoing_mail.post("/")
async def get_outgoing_mail(data_dict: dict, session: AsyncSession = Depends(get_async_session)):

    credits_id_array = data_dict['credits_id_array']
    recipient_id = data_dict['recipient_id']
    user_id = data_dict['user_id']
    name_docs = data_dict['name_docs']

    credits_query = await session.execute(select(credit).where(credit.c.id.in_(credits_id_array)))

    for item in credits_query.mappings().all():
        credit_id: int = item.id
        debtor_id: int = item.debtor_id
        addresser = 'НЕ ОПРЕДЕЛЕН'
        recipient_address = 'НЕ ОПРЕДЕЛЕН'
        mass = 10
        category_mail = 'Простое'
        type_mail = {"text": "Письмо", "value": 2}
        type_package = 'C5'

        if recipient_id == 1:
            debtor_query = await session.execute(select(debtor).where(debtor.c.id == debtor_id))
            debtor_item = debtor_query.mappings().one()
            if debtor_item.last_name_2 is not None:
                addresser = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}" \
                             f" ({debtor_item.last_name_2} {debtor_item.first_name_2} {debtor_item.second_name_2 or ''})"
            else:
                addresser = f"{debtor_item.last_name_1} {debtor_item.first_name_1} {debtor_item.second_name_1 or ''}"

            if debtor_item.address_1 is not None:
                recipient_address = f"{debtor_item.index_add_1 or ''}, {debtor_item.address_1}"
        elif recipient_id == 2:
            debtor_query = await session.execute(select(debtor.c.tribunal_id).where(debtor.c.id == debtor_id))
            tribunal = debtor_query.mappings().fetchone()

            if tribunal.tribunal_id:
                tribunal_id: int = tribunal.tribunal_id
                tribunal_query = await session.execute(select(ref_tribunal).where(ref_tribunal.c.id == tribunal_id))
                tribunal_item = tribunal_query.mappings().one()

                addresser = tribunal_item.name
                recipient_address = tribunal_item.address
        elif recipient_id == 3:
            pass
        elif recipient_id == 4:
            pass
        elif recipient_id == 5:
            pass
        else:
            pass

        new_mail = {"new_mail": {
            "id": None,
            "sequenceNum": None,
            "caseNum": None,
            "credit_id": credit_id,
            "mailDate": None,
            "docName": name_docs,
            "mailRecipient": addresser,
            "addressRecipient": recipient_address,
            "mailMass": int(mass),
            "stateDuty": None,
            "trekNum": None,
            "mailCategory": category_mail,
            "mailType": type_mail,
            "packageType": type_package,
            "barcodeNum": None,
            "symbolNum": None,
            "expensesMail": None,
            "user_id": user_id,
            "comment": None,
        }}

        await save_outgoing_mail(new_mail, session)

    return {
        'status': 'success',
        'data': None,
        'details': 'Исходящая почта успешно сохранена'
    }