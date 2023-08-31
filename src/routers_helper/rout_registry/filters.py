from datetime import date, timedelta

# import logging
# logger_cons = logging.getLogger('console_views_api')

'''
Боевые:
Функции контроля и фильтров Реестра должников
'''


def control_section8():
    pass

    # queryset = Executive_Documents.objects.filter(status_ed=2).values()
    #
    # current_date = date.today()
    #
    # credit_id_list = []
    # for item in queryset:
    #
    #     collection_set = Collection_Debt.objects.values('date_start').filter(executive_document=item['id']).order_by('-date_start')
    #     date_start = collection_set[0]['date_start']
    #
    #     # Период предъявления ИД
    #     period = current_date - date_start
    #
    #     if period.days > 39:
    #         date_pay_40 = current_date - timedelta(days=40)
    #         payments_set = Payments.objects.values().filter(credit=item['credit_id'], date__range=[date_pay_40, current_date.strftime("%Y-%m-%d")]).order_by('-date')
    #         summa_all = payments_set.aggregate(Sum('summa'))
    #
    #         try:
    #             # Сумма платежей в период предъявления менее 500
    #             if summa_all['summa__sum'] < 500:
    #                 credit_id_list.append(item['credit_id'])
    #         except:
    #             credit_id_list.append(item['credit_id'])
    #
    #     elif period.days > 54:
    #         date_pay_55 = current_date - timedelta(days=55)
    #         payments_set = Payments.objects.values().filter(credit=item['credit_id'], date__range=[date_pay_55, current_date.strftime("%Y-%m-%d")]).order_by('-date')
    #         summa_all = payments_set.aggregate(Sum('summa'))
    #
    #         try:
    #             # Сумма платежей в период предъявления менее 500
    #             if summa_all['summa__sum'] >= 500 and len(payments_set) == 1:
    #                 credit_id_list.append(item['credit_id'])
    #         except:
    #             credit_id_list.append(item['credit_id'])
    #
    # return credit_id_list


def control_return_section8():
    pass

    # queryset = Executive_Documents.objects.filter(status_ed=2).values()
    #
    # current_date = date.today()
    #
    # credit_id_list = []
    # for item in queryset:
    #
    #     date_return_set = Collection_Debt.objects.values().filter(executive_document=item['id']).order_by('-date_return')
    #
    #     for d in date_return_set:
    #
    #         if d['date_return'] is not None:
    #             date_return = d['date_return']
    #
    #             # Период нахождения в пути в даты отзыва ИД
    #             period = current_date - date_return
    #
    #             if period.days > 15:
    #                 credit_id_list.append(d['credit_id'])
    #
    # return credit_id_list


def control_not_excitement_ep():
    pass

    # queryset = Collection_Debt.objects.filter(type_department=1).values()
    #
    # current_date = date.today()
    #
    # credit_id_list = []
    # for item in queryset:
    #
    #     date_start = item['date_start']
    #     date_return = item['date_return']
    #
    #     # Период предъявления ИД
    #     period = current_date - date_start
    #
    #     if period.days > 39 and (date_return == None or date_return == ''):
    #         credit_id = item['credit_id']
    #
    #         ep_set = Executive_Productions.objects.filter(credit=credit_id).values()
    #
    #         if len(ep_set) == 0:
    #             credit_id_list.append(item['credit_id'])
    #         else:
    #             for ep in ep_set:
    #                 date_end = ep['date_end']
    #                 if date_end:
    #                     period_end = current_date - date_end
    #                     if period_end.days > 39:
    #                         credit_id_list.append(item['credit_id'])
    #
    # return credit_id_list


def control_not_return_ed():
    pass

    # date_end_set = Executive_Productions.objects.filter(date_end__isnull=False).values()
    #
    # current_date = date.today()
    #
    # credit_id_list = []
    # for item in date_end_set:
    #
    #     date_end = item['date_end']
    #     period = current_date - date_end
    #
    #     if period.days > 14:
    #
    #         queryset = Collection_Debt.objects.filter(type_department=1, credit_id=item['credit_id']).values().order_by('-date_start')
    #
    #         if len(queryset) == 0:
    #             credit_id_list.append(item['credit_id'])
    #         else:
    #             date_end_cd = queryset[0]['date_end']
    #             if date_end_cd == None or date_end_cd == '':
    #                 credit_id_list.append(item['credit_id'])
    #
    # return credit_id_list