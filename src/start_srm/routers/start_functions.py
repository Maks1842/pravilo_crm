# from datetime import date, timedelta, datetime
#
# from debtors.app_models import *
# from django.db.models import Sum
#
# from variables_for_backend import VarStatusCD, VarStatusED, VarTypeDep
#
# import logging
# debug_log = logging.getLogger('debug_log')
#
#
#
# def control_payment_schedule():
#
#     current_date = date.today()
#
#     agreement_set = Agreement.objects.values()
#
#     for agr in agreement_set:
#
#         status_cd = Credits.objects.values('status_cd_id').get(id=agr['credit_id'])['status_cd_id']
#
#         if status_cd != VarStatusCD.status_cd_pgsh:
#
#             result = None
#
#             schedule = agr['payment_schedule']
#
#             pay_set = Payments.objects.values().filter(credit=agr['credit_id']).order_by('date').last()
#             if pay_set:
#                 date_pay = datetime.strptime(str(pay_set['date']), '%Y-%m-%d').strftime("%d.%m.%Y")
#                 summa_pay = pay_set['summa']
#             else:
#                 date_pay = None
#                 summa_pay = None
#
#             try:
#                 schedule_list = []
#                 for item in schedule:
#                     if item['datePay']:
#                         date_pay_schedule = datetime.strptime(item['datePay'], "%d.%m.%Y").date()
#
#                         if date_pay_schedule <= current_date:
#                             schedule_list.append({"datePay": date_pay_schedule, "summaPay": item['summaPay']})
#
#                 if len(schedule_list) > 0:
#                     #Получил данные из графика, где дата платежа ближайшая к текущей дате
#                     data_schedule = max(schedule_list, key=lambda x: x['datePay'])
#
#                     if date_pay:
#                         date_pay_f = datetime.strptime(date_pay, "%d.%m.%Y").date()
#                         day_delta = data_schedule['datePay'] - date_pay_f
#
#                         if day_delta.days > 6:
#                             delay_day = current_date - date_pay_f
#                             result = f'Платеж просрочен на {delay_day.days} д.'
#                         elif float(summa_pay) < float(data_schedule['summaPay']):
#                             pay_delta = round(float(data_schedule['summaPay']) - float(summa_pay), 2)
#                             result = f'Платеж меньше на {pay_delta} руб.'
#                         else:
#                             result = None
#                     elif date_pay is None and data_schedule:
#                         delay_day = current_date - data_schedule['datePay']
#
#                         if delay_day.days > 6:
#                             result = f'Платеж просрочен на {delay_day.days} д.'
#                     else:
#                         result = None
#                 else:
#                     result = None
#             except Exception as ex:
#                 result = f'Ошибка контроля платежа {ex}'
#                 if len(result) > 100:
#                     result = result[-100:]
#
#             try:
#
#                 Agreement.objects.update_or_create(
#                     pk=agr['id'],
#                     defaults={"control": result},
#                 )
#             except Exception as ex:
#                 debug_log.debug(f'ОШИБКА сохранения в Соглашение. {ex}')
#
#         else:
#             try:
#                 Agreement.objects.update_or_create(
#                     pk=agr['id'],
#                     defaults={"control": 'Статус Погашено'},
#                 )
#             except Exception as ex:
#                 debug_log.debug(f'ОШИБКА сохранения в Соглашение. {ex}')