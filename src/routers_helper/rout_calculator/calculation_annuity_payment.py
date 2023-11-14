from datetime import datetime, timedelta


def get_calculation_annuity(data_json):

    date_start_cd = data_json['date_start_cd']
    summa_cd = data_json['summa_cd']
    interest_rate = float(data_json['interest_rate'])
    date_start_pay = datetime.strptime(data_json['date_start_pay'], '%Y-%m-%d')
    date_end_pay = datetime.strptime(data_json['date_end_pay'], '%Y-%m-%d')
    period = int(data_json['period'])
    summa_payments = float(data_json['summa_payments'])
    summa_pay_start = float(data_json['summa_pay_start'])
    summa_percent_start = float(data_json['summa_percent_start'])
    overdue_od = float(data_json['overdue_od'])
    timeline = data_json['timeline']

    summa_payments_decrease = summa_payments
    current_date = datetime.now()
    date_delta = current_date - timedelta(days=(365 * 3))

    summ_percent_total = 0

    annuity_list = []
    if timeline == 1:

        summ_pay_total = 0

        count = 0
        remains_debt = summa_cd

        num_period_year = 365/7
        number_periods_credit = period/7

        rate_week = interest_rate/num_period_year/100

        if summa_pay_start == 0 or summa_pay_start > 0:

            count += 1

            number_periods_credit = period/7 - 1
            summa_payments_decrease = summa_payments_decrease - summa_percent_start
            remains_debt = remains_debt - summa_pay_start

            summ_pay_total += summa_percent_start + summa_pay_start
            summ_percent_total += summa_percent_start

            annuity_list.append({
                'count': count,
                'date_pay': date_start_pay,
                'annuity_pay': summa_percent_start,
                'pay_od': summa_pay_start,
                'pay_percent': round(summa_percent_start, 2),
                'remains_debt': round(remains_debt, 2),     # Остаток долга после платежа
                'summ_pay_total': round(summ_pay_total, 2),
                'summ_percent_total': round(summ_percent_total, 2)
            })

            date_start_pay = date_start_pay + timedelta(days=7)

        k_annuity = (rate_week * (1 + rate_week) ** number_periods_credit) / ((1 + rate_week) ** number_periods_credit - 1)

        annuity_pay = round(remains_debt * k_annuity, 2)

        if date_start_cd > date_delta.date():
            while annuity_pay < summa_payments_decrease:

                pay_percent = remains_debt * rate_week
                pay_od = annuity_pay - pay_percent
                remains_debt = remains_debt - pay_od

                summa_payments_decrease -= annuity_pay
                count += 1

                if annuity_pay > summa_payments_decrease:
                    if remains_debt > overdue_od:

                        remains_debt_back = annuity_list[count - 2]['remains_debt']
                        pay_od = remains_debt_back - overdue_od
                        remains_debt = overdue_od
                        pay_percent = summa_payments - summ_pay_total - pay_od

                p = pay_od + pay_percent
                summ_pay_total += p
                summ_percent_total += pay_percent

                annuity_list.append({
                    'count': count,
                    'date_pay': date_start_pay,
                    'annuity_pay': annuity_pay,
                    'pay_od': round(pay_od, 2),
                    'pay_percent': round(pay_percent, 2),
                    'remains_debt': round(remains_debt, 2),     # Остаток долга после платежа
                    'summ_pay_total': round(summ_pay_total, 2),
                    'summ_percent_total': round(summ_percent_total, 2)
                })

                date_start_pay = date_start_pay + timedelta(days=7)
        else:
            while annuity_pay < summa_payments_decrease:

                pay_percent = remains_debt * rate_week
                pay_od = annuity_pay - pay_percent
                remains_debt = remains_debt - pay_od

                summa_payments_decrease -= annuity_pay

                count += 1

                if date_start_pay > date_end_pay:

                    remains_debt_back = annuity_list[count - 2]['remains_debt']
                    pay_od = remains_debt_back - overdue_od
                    remains_debt = overdue_od
                    pay_percent = summa_payments - summ_pay_total - pay_od
                    summ_percent_total += pay_percent

                    annuity_list.append({
                        'count': count,
                        'date_pay': date_end_pay,
                        'annuity_pay': annuity_pay,
                        'pay_od': round(pay_od, 2),
                        'pay_percent': round(pay_percent, 2),
                        'remains_debt': round(remains_debt, 2),     # Остаток долга после платежа
                        'summ_pay_total': round(summ_pay_total, 2),
                        'summ_percent_total': round(summ_percent_total, 2)
                    })

                    return annuity_list

                else:
                    if annuity_pay > summa_payments_decrease:
                        date_start_pay = date_end_pay
                        if remains_debt > overdue_od:

                            remains_debt_back = annuity_list[count - 2]['remains_debt']

                            pay_od = remains_debt_back - overdue_od
                            remains_debt = overdue_od
                            pay_percent = summa_payments_decrease

                    summ_pay_total += (pay_od + pay_percent)
                    summ_percent_total += pay_percent

                    annuity_list.append({
                        'count': count,
                        'date_pay': date_start_pay,
                        'annuity_pay': annuity_pay,
                        'pay_od': round(pay_od, 2),
                        'pay_percent': round(pay_percent, 2),
                        'remains_debt': round(remains_debt, 2),     # Остаток долга после платежа
                        'summ_pay_total': round(summ_pay_total, 2),
                        'summ_percent_total': round(summ_percent_total, 2)
                    })

                    date_start_pay = date_start_pay + timedelta(days=7)

    return {'annuity_list': annuity_list, 'summ_percent_total': round(summ_percent_total, 2)}

