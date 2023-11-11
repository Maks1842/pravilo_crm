from datetime import date, datetime, timedelta


def get_calculation_annuity(data_json):

    summa_cd = data_json['summa_cd']
    interest_rate = int(data_json['interest_rate'])
    date_start_pay = datetime.strptime(data_json['date_start_pay'], '%Y-%m-%d')
    date_end_pay = data_json['date_end_pay']
    period = int(data_json['period'])
    summa_payments = float(data_json['summa_payments'])
    overdue_od = data_json['overdue_od']
    timeline = data_json['timeline']

    annuity_list = []
    if timeline == 1:

        num_perion_year = 365/7
        number_periods_credit = round(period/7, 1)
        rate_week = round(interest_rate/num_perion_year/100, 2)

        k_annuity = (rate_week * (1 + rate_week) ** number_periods_credit) / ((1 + rate_week) ** number_periods_credit - 1)

        annuity_pay = round(summa_cd * k_annuity, 2)

        summ_pay_total = 0
        count = 0
        remains_debt = summa_cd

        while annuity_pay < summa_payments:

            pay_percent = remains_debt * rate_week
            pay_od = annuity_pay - pay_percent
            remains_debt = remains_debt - pay_od

            date_formar = date_start_pay.date().strftime("%d.%m.%Y")

            summa_payments -= annuity_pay
            count += 1

            if annuity_pay > summa_payments:
                pay_percent = pay_percent + summa_payments
                date_formar = datetime.strptime(str(date_end_pay), '%Y-%m-%d').strftime("%d.%m.%Y")

            summ_pay_total += (pay_od + pay_percent)

            date_start_pay = date_start_pay + timedelta(days=7)

            annuity_list.append({
                'count': count,
                'date_pay': date_formar,
                'annuity_pay': annuity_pay,
                'pay_od': round(pay_od, 2),
                'pay_percent': round(pay_percent, 2),
                'remains_debt': round(remains_debt, 2),     # Остаток долга после платежа
                'summ_pay_total': round(summ_pay_total, 2)
            })

            # print(annuity_list)

    return annuity_list




# data_json = {
#     'summa_cd': 15000.00,
#     'interest_rate': 365,
#     'date_start_pay': '2021-10-01',
#     'date_end_pay': '2021-12-01',
#     'period': 175,
#     'summ_pay': 11622.96,
#     'overdue_od': 12159.31,
#     'timeline': 1
# }
# get_calculation_annuity(data_json)

