from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.mail.routers.incoming_mail import save_incoming_mail
from src.collection_debt.routers.executive_document_rout import add_ed_debtor


# Добавить входящую корреспонденцию из Reader
router_reader_save_incoming_mail = APIRouter(
    prefix="/v1/ReaderSaveDataToMail",
    tags=["Reader"]
)


@router_reader_save_incoming_mail.post("/")
async def add_reader_incoming_mail(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    data = data_json['data_json']

    list_mail = []
    for item in data:
        if item['credit_id']:
            try:
                tribunal_name = item['tribunalName']
            except:
                tribunal_name = None

            try:
                num_case = item['numCase']
            except:
                num_case = None

            try:
                date_ED = item['dateED']
            except:
                date_ED = None

            try:
                legal_docs_id = item['legal_docs_id']
            except:
                legal_docs_id = None

            try:
                date_session = item['dateSessionTribunal']
            except:
                date_session = None

            try:
                result_statement_id = item['result_statement_id']
            except:
                result_statement_id = None

            list_mail.append({
                'id': None,
                'sequence_num': None,
                "case_number": num_case,
                "credit_id": item['credit_id'],
                "barcode": None,
                'date': None,
                'addresser': tribunal_name,
                'docDate': date_ED,
                "legal_docs_id": legal_docs_id,
                "resolution_id": result_statement_id,
                'user_id': None,
                'comment': '',
            })
        else:
            pass

    result = await save_incoming_mail(list_mail, session)

    return result


# Добавить ИД из Reader
router_reader_save_ed = APIRouter(
    prefix="/v1/ReaderSaveED",
    tags=["Reader"]
)


@router_reader_save_ed.post("/")
async def add_reader_ed(data_json: dict, session: AsyncSession = Depends(get_async_session)):

    data = data_json['data_json']

    list_ed = []
    for item in data:
        if item['credit_id']:

            list_ed.append({
                'id': None,
                "number": item['numCase'],
                "date_decision": item['dateED'],
                "case_number": item['numCase'],
                "date_of_receipt_ed": None,
                "type_ed_id": item['type_ed_id'],
                "status_ed_id": 1,
                "credit_id": item['credit_id'],
                "user_id": None,
                "summa_debt_decision": item['summaDebt'],
                "state_duty": item['stateDuty'],
                "succession": None,
                "date_entry_force": item['date_entry_force'],
                "claimer_ed_id": None,
                "tribunal_id": item['tribunal_id'],
                'comment': '',
            })
        else:
            pass

    result = await add_ed_debtor({"data_json": list_ed}, session)

    return result