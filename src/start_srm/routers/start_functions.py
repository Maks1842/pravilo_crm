from datetime import date, timedelta, datetime

from sqlalchemy import select, desc, update
from src.debts.models import cession, credit
from src.agreement.models import agreement
from src.payments.models import payment

from variables_for_backend import VarStatusCD, VarStatusED, VarTypeDep



async def control_payment_schedule(session):

    current_date = date.today()

    agreement_query = await session.execute(select(agreement))
    agreement_set = agreement_query.mappings().all()

    for agr in agreement_set:

        status_cd_query = await session.execute(select(credit.c.status_cd_id))
        status_cd = status_cd_query.scalar()

        result = None

        if status_cd != VarStatusCD.status_cd_pgsh:

            schedule = agr.payment_schedule

            payment_query = await session.execute(select(payment).where(payment.c.credit_id == int(agr.credit_id)).order_by(desc(payment.c.date)))
            pay_set = payment_query.mappings().first()
            if pay_set:
                date_pay = datetime.strptime(str(pay_set.date), '%Y-%m-%d').strftime("%d.%m.%Y")
                summa_pay = pay_set.summa
            else:
                date_pay = None
                summa_pay = None

            try:
                schedule_list = []
                for item in schedule:
                    if item['datePay']:
                        date_pay_schedule = datetime.strptime(item['datePay'], "%d.%m.%Y").date()

                        if date_pay_schedule <= current_date:
                            schedule_list.append({"datePay": date_pay_schedule, "summaPay": item['summaPay']})

                if len(schedule_list) > 0:
                    #Получил данные из графика, где дата платежа ближайшая к текущей дате
                    data_schedule = max(schedule_list, key=lambda x: x['datePay'])

                    if date_pay:
                        date_pay_f = datetime.strptime(date_pay, "%d.%m.%Y").date()
                        day_delta = data_schedule['datePay'] - date_pay_f

                        if day_delta.days > 6:
                            delay_day = current_date - date_pay_f
                            result = f'Платеж просрочен на {delay_day.days} д.'
                        elif float(summa_pay) < float(data_schedule['summaPay']):
                            pay_delta = round(float(data_schedule['summaPay']) - float(summa_pay), 2)
                            result = f'Платеж меньше на {pay_delta} руб.'
                        else:
                            result = None
                    elif date_pay is None and data_schedule:
                        delay_day = current_date - data_schedule['datePay']

                        if delay_day.days > 6:
                            result = f'Платеж просрочен на {delay_day.days} д.'
                    else:
                        result = None
                else:
                    result = None
            except Exception as ex:
                result = f'Ошибка контроля платежа {ex}'
                if len(result) > 100:
                    result = result[-100:]
        else:
            result = f'Статус Погашено'

        agreement_data = {"control": result}

        try:
            post_data = update(agreement).where(agreement.c.id == int(agr.id)).values(agreement_data)

            await session.execute(post_data)
            await session.commit()
        except Exception as ex:
            print(f'ОШИБКА сохранения в Соглашение. {ex}')