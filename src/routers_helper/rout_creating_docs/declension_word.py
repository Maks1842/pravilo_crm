'''
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


def declension(text, declension_regular):
    text_im = []
    text_ro = []
    text_da = []
    text_vi = []
    text_tv = []
    text_pr = []

    split_text = text['text'].split()
    gender = text['gender']

    count = 0
    for word in split_text:
        count += 1
        word_imenit = declens_imenit(word, gender, count, declension_regular)
        word_rodit = declens_rodit(word, gender, count, declension_regular)
        word_dat = declens_dat(word, gender, count, declension_regular)
        word_vinit = declens_vinit(word, gender, count, declension_regular)
        word_tvorit = declens_tvorit(word, gender, count, declension_regular)
        word_predl = declens_predl(word, gender, count, declension_regular)

        if word_imenit == '':
            word_imenit = word
        if word_rodit == '':
            word_rodit = word
        if word_dat == '':
            word_dat = word
        if word_vinit == '':
            word_vinit = word
        if word_tvorit == '':
            word_tvorit = word
        if word_predl == '':
            word_predl = word

        text_im.append(word_imenit)
        text_ro.append(word_rodit)
        text_da.append(word_dat)
        text_vi.append(word_vinit)
        text_tv.append(word_tvorit)
        text_pr.append(word_predl)

    text_imenit = ' '.join(text_im)
    text_rodit = ' '.join(text_ro)
    text_dat = ' '.join(text_da)
    text_vinit = ' '.join(text_vi)
    text_tvorit = ' '.join(text_tv)
    text_predl = ' '.join(text_pr)

    return text_imenit, text_rodit, text_dat, text_vinit, text_tvorit, text_predl


def declens_imenit(word, gender, count, declension_regular):
    word_imenit = ''

    sogl = 'б|в|г|д|ж|з|к|л|м|н|п|р|с|т|ф|х|ц|ч|ш|щ'
    gl = 'а|е|ё|и|о|у|э|ю|я|ы'
    # print(f'{item["ending_word"] = }')

    for item in declension_regular:
        if item['number_word'] == count:

            if re.findall(rf'({item["ending_word"]})$', word) and item["gender"] == None:
                if item["imenit"] is not None:               # Именительный
                    if re.findall(r'\+', item["imenit"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["imenit"]).group()
                        word_imenit = word + new_ending
                    elif re.findall(r'-', item["imenit"]):
                        old_ending = re.search(r'\w+(?=\-)', item["imenit"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["imenit"]).group()
                        word_imenit = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

            elif re.findall(rf'({item["ending_word"]})$', word) and re.findall(r'(?i)(муж)|м', item["gender"]) and re.findall(r'(?i)(муж)|м', gender):
                if item["imenit"] != None:               # Именительный
                    if re.findall(r'\+', item["imenit"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["imenit"]).group()
                        word_imenit = word + new_ending
                    elif re.findall(r'-', item["imenit"]):
                        old_ending = re.search(r'\w+(?=\-)', item["imenit"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["imenit"]).group()
                        word_imenit = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

            elif re.findall(rf'({item["ending_word"]})$', word) and re.findall(r'(?i)(жен)|ж', item["gender"]) and re.findall(r'(?i)(жен)|ж', gender):
                if item["imenit"] != None:               # Именительный
                    if re.findall(r'\+', item["imenit"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["imenit"]).group()
                        word_imenit = word + new_ending
                    elif re.findall(r'-', item["imenit"]):
                        old_ending = re.search(r'\w+(?=\-)|.(?=\-)', item["imenit"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["imenit"]).group()
                        word_imenit = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

            elif f'{item["ending_word"]}' == 'sogl' and re.findall(rf'({sogl})$', word) and re.findall(r'(?i)(муж)|м', item["gender"]) and re.findall(r'(?i)(муж)|м', gender):
                if item["imenit"] != None:               # Именительный
                    if re.findall(r'\+', item["imenit"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["imenit"]).group()
                        word_imenit = word + new_ending
                    elif re.findall(r'-', item["imenit"]):
                        old_ending = re.search(r'\w+(?=\-)', item["imenit"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["imenit"]).group()
                        word_imenit = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

    return word_imenit


def declens_rodit(word, gender, count, declension_regular):
    word_rodit = ''

    sogl = 'б|в|г|д|ж|з|к|л|м|н|п|р|с|т|ф|х|ц|ч|ш|щ'
    gl = 'а|е|ё|и|о|у|э|ю|я|ы'
    # print(f'{item["ending_word"] = }')

    for item in declension_regular:
        if item['number_word'] == count:
            if re.findall(rf'({item["ending_word"]})$', word) and item["gender"] == None:
                if item["rodit"] != None:               # Родительный
                    if re.findall(r'\+', item["rodit"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["rodit"]).group()
                        word_rodit = word + new_ending
                    elif re.findall(r'-', item["rodit"]):
                        old_ending = re.search(r'\w+(?=\-)', item["rodit"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["rodit"]).group()
                        word_rodit = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

            elif re.findall(rf'({item["ending_word"]})$', word) and re.findall(r'(?i)(муж)|м', item["gender"]) and re.findall(r'(?i)(муж)|м', gender):
                if item["rodit"] != None:               # Именительный
                    if re.findall(r'\+', item["rodit"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["rodit"]).group()
                        word_rodit = word + new_ending
                    elif re.findall(r'-', item["rodit"]):
                        old_ending = re.search(r'\w+(?=\-)', item["rodit"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["rodit"]).group()
                        word_rodit = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

            elif re.findall(rf'({item["ending_word"]})$', word) and re.findall(r'(?i)(жен)|ж', item["gender"]) and re.findall(r'(?i)(жен)|ж', gender):
                if item["rodit"] != None:               # Именительный
                    if re.findall(r'\+', item["rodit"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["rodit"]).group()
                        word_rodit = word + new_ending
                    elif re.findall(r'-', item["rodit"]):
                        old_ending = re.search(r'\w+(?=\-)|.(?=\-)', item["rodit"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["rodit"]).group()
                        word_rodit = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

            elif f'{item["ending_word"]}' == 'sogl' and re.findall(rf'({sogl})$', word) and re.findall(r'(?i)(муж)|м', item["gender"]) and re.findall(r'(?i)(муж)|м', gender):
                if item["rodit"] != None:               # Именительный
                    if re.findall(r'\+', item["rodit"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["rodit"]).group()
                        word_rodit = word + new_ending
                    elif re.findall(r'-', item["rodit"]):
                        old_ending = re.search(r'\w+(?=\-)', item["rodit"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["rodit"]).group()
                        word_rodit = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

    return word_rodit


def declens_dat(word, gender, count, declension_regular):
    word_dat = ''

    sogl = 'б|в|г|д|ж|з|к|л|м|н|п|р|с|т|ф|х|ц|ч|ш|щ'
    gl = 'а|е|ё|и|о|у|э|ю|я|ы'
    # print(f'{item["ending_word"] = }')

    for item in declension_regular:
        if item['number_word'] == count:
            if re.findall(rf'({item["ending_word"]})$', word) and item["gender"] == None:
                if item["datel"] != None:               # Родительный
                    if re.findall(r'\+', item["datel"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["datel"]).group()
                        word_dat = word + new_ending
                    elif re.findall(r'-', item["datel"]):
                        old_ending = re.search(r'\w+(?=\-)', item["datel"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["datel"]).group()
                        word_dat = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

            elif re.findall(rf'({item["ending_word"]})$', word) and re.findall(r'(?i)(муж)|м', item["gender"]) and re.findall(r'(?i)(муж)|м', gender):
                if item["datel"] != None:               # Именительный
                    if re.findall(r'\+', item["datel"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["datel"]).group()
                        word_dat = word + new_ending
                    elif re.findall(r'-', item["datel"]):
                        old_ending = re.search(r'\w+(?=\-)', item["datel"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["datel"]).group()
                        word_dat = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

            elif re.findall(rf'({item["ending_word"]})$', word) and re.findall(r'(?i)(жен)|ж', item["gender"]) and re.findall(r'(?i)(жен)|ж', gender):
                if item["datel"] != None:               # Именительный
                    if re.findall(r'\+', item["datel"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["datel"]).group()
                        word_dat = word + new_ending
                    elif re.findall(r'-', item["datel"]):
                        old_ending = re.search(r'\w+(?=\-)|.(?=\-)', item["datel"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["datel"]).group()
                        word_dat = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

            elif f'{item["ending_word"]}' == 'sogl' and re.findall(rf'({sogl})$', word) and re.findall(r'(?i)(муж)|м', item["gender"]) and re.findall(r'(?i)(муж)|м', gender):
                if item["datel"] != None:               # Именительный
                    if re.findall(r'\+', item["datel"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["datel"]).group()
                        word_dat = word + new_ending
                    elif re.findall(r'-', item["datel"]):
                        old_ending = re.search(r'\w+(?=\-)', item["datel"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["datel"]).group()
                        word_dat = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

    return word_dat


def declens_vinit(word, gender, count, declension_regular):
    word_vinit = ''

    sogl = 'б|в|г|д|ж|з|к|л|м|н|п|р|с|т|ф|х|ц|ч|ш|щ'
    gl = 'а|е|ё|и|о|у|э|ю|я|ы'
    # print(f'{item["ending_word"] = }')

    for item in declension_regular:
        if item['number_word'] == count:
            if re.findall(rf'({item["ending_word"]})$', word) and item["gender"] == None:
                if item["vinit"] != None:               # Родительный
                    if re.findall(r'\+', item["vinit"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["vinit"]).group()
                        word_vinit = word + new_ending
                    elif re.findall(r'-', item["vinit"]):
                        old_ending = re.search(r'\w+(?=\-)', item["vinit"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["vinit"]).group()
                        word_vinit = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

            elif re.findall(rf'({item["ending_word"]})$', word) and re.findall(r'(?i)(муж)|м', item["gender"]) and re.findall(r'(?i)(муж)|м', gender):
                if item["vinit"] != None:               # Именительный
                    if re.findall(r'\+', item["vinit"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["vinit"]).group()
                        word_vinit = word + new_ending
                    elif re.findall(r'-', item["vinit"]):
                        old_ending = re.search(r'\w+(?=\-)', item["vinit"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["vinit"]).group()
                        word_vinit = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

            elif re.findall(rf'({item["ending_word"]})$', word) and re.findall(r'(?i)(жен)|ж', item["gender"]) and re.findall(r'(?i)(жен)|ж', gender):
                if item["vinit"] != None:               # Именительный
                    if re.findall(r'\+', item["vinit"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["vinit"]).group()
                        word_vinit = word + new_ending
                    elif re.findall(r'-', item["vinit"]):
                        old_ending = re.search(r'\w+(?=\-)|.(?=\-)', item["vinit"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["vinit"]).group()
                        word_vinit = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

            elif f'{item["ending_word"]}' == 'sogl' and re.findall(rf'({sogl})$', word) and re.findall(r'(?i)(муж)|м', item["gender"]) and re.findall(r'(?i)(муж)|м', gender):
                if item["vinit"] != None:               # Именительный
                    if re.findall(r'\+', item["vinit"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["vinit"]).group()
                        word_vinit = word + new_ending
                    elif re.findall(r'-', item["vinit"]):
                        old_ending = re.search(r'\w+(?=\-)', item["vinit"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["vinit"]).group()
                        word_vinit = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

    return word_vinit


def declens_tvorit(word, gender, count, declension_regular):
    word_tvorit = ''

    sogl = 'б|в|г|д|ж|з|к|л|м|н|п|р|с|т|ф|х|ц|ч|ш|щ'
    gl = 'а|е|ё|и|о|у|э|ю|я|ы'
    # print(f'{item["ending_word"] = }')

    for item in declension_regular:
        if item['number_word'] == count:
            if re.findall(rf'({item["ending_word"]})$', word) and item["gender"] == None:
                if item["tvorit"] != None:               # Родительный
                    if re.findall(r'\+', item["tvorit"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["tvorit"]).group()
                        word_tvorit = word + new_ending
                    elif re.findall(r'-', item["tvorit"]):
                        old_ending = re.search(r'\w+(?=\-)', item["tvorit"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["tvorit"]).group()
                        word_tvorit = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

            elif re.findall(rf'({item["ending_word"]})$', word) and re.findall(r'(?i)(муж)|м', item["gender"]) and re.findall(r'(?i)(муж)|м', gender):
                if item["tvorit"] != None:               # Именительный
                    if re.findall(r'\+', item["tvorit"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["tvorit"]).group()
                        word_tvorit = word + new_ending
                    elif re.findall(r'-', item["tvorit"]):
                        old_ending = re.search(r'\w+(?=\-)', item["tvorit"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["tvorit"]).group()
                        word_tvorit = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

            elif re.findall(rf'({item["ending_word"]})$', word) and re.findall(r'(?i)(жен)|ж', item["gender"]) and re.findall(r'(?i)(жен)|ж', gender):
                if item["tvorit"] != None:               # Именительный
                    if re.findall(r'\+', item["tvorit"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["tvorit"]).group()
                        word_tvorit = word + new_ending
                    elif re.findall(r'-', item["tvorit"]):
                        old_ending = re.search(r'\w+(?=\-)|.(?=\-)', item["tvorit"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["tvorit"]).group()
                        word_tvorit = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

            elif f'{item["ending_word"]}' == 'sogl' and re.findall(rf'({sogl})$', word) and re.findall(r'(?i)(муж)|м', item["gender"]) and re.findall(r'(?i)(муж)|м', gender):
                if item["tvorit"] != None:               # Именительный
                    if re.findall(r'\+', item["tvorit"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["tvorit"]).group()
                        word_tvorit = word + new_ending
                    elif re.findall(r'-', item["tvorit"]):
                        old_ending = re.search(r'\w+(?=\-)', item["tvorit"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["tvorit"]).group()
                        word_tvorit = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

    return word_tvorit


def declens_predl(word, gender, count, declension_regular):
    word_predl = ''

    sogl = 'б|в|г|д|ж|з|к|л|м|н|п|р|с|т|ф|х|ц|ч|ш|щ'
    gl = 'а|е|ё|и|о|у|э|ю|я|ы'
    # print(f'{item["ending_word"] = }')

    for item in declension_regular:
        if item['number_word'] == count:
            if re.findall(rf'({item["ending_word"]})$', word) and item["gender"] == None:
                if item["predl"] != None:               # Родительный
                    if re.findall(r'\+', item["predl"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["predl"]).group()
                        word_predl = word + new_ending
                    elif re.findall(r'-', item["predl"]):
                        old_ending = re.search(r'\w+(?=\-)', item["predl"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["predl"]).group()
                        word_predl = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

            elif re.findall(rf'({item["ending_word"]})$', word) and re.findall(r'(?i)(муж)|м', item["gender"]) and re.findall(r'(?i)(муж)|м', gender):
                if item["predl"] != None:               # Именительный
                    if re.findall(r'\+', item["predl"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["predl"]).group()
                        word_predl = word + new_ending
                    elif re.findall(r'-', item["predl"]):
                        old_ending = re.search(r'\w+(?=\-)', item["predl"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["predl"]).group()
                        word_predl = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

            elif re.findall(rf'({item["ending_word"]})$', word) and re.findall(r'(?i)(жен)|ж', item["gender"]) and re.findall(r'(?i)(жен)|ж', gender):
                if item["predl"] != None:               # Именительный
                    if re.findall(r'\+', item["predl"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["predl"]).group()
                        word_predl = word + new_ending
                    elif re.findall(r'-', item["predl"]):
                        old_ending = re.search(r'\w+(?=\-)|.(?=\-)', item["predl"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["predl"]).group()
                        word_predl = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

            elif f'{item["ending_word"]}' == 'sogl' and re.findall(rf'({sogl})$', word) and re.findall(r'(?i)(муж)|м', item["gender"]) and re.findall(r'(?i)(муж)|м', gender):
                if item["predl"] != None:               # Именительный
                    if re.findall(r'\+', item["predl"]):
                        new_ending = re.search(r'(?<=\+)\w+', item["predl"]).group()
                        word_predl = word + new_ending
                    elif re.findall(r'-', item["predl"]):
                        old_ending = re.search(r'\w+(?=\-)', item["predl"]).group()
                        new_ending = re.search(r'(?<=\-)\w+', item["predl"]).group()
                        word_predl = re.sub(rf'({old_ending})$', rf'{new_ending}', word)

    return word_predl


# declension(text, declension_regular)