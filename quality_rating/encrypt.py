import base64
import datetime
import io
import os
import random

import numpy as np
import pandas as pd

import quality_rating.log_writer as lw
import quality_rating.processing as processing
import quality_rating.category_lists as cat_list
from quality_rating.load_cfg import table, conn_string

staff_info_df = processing.load_staff(table_name=table, connection_string=conn_string)


def parse_contents_encrypt(contents, filename):

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        content_df = pd.read_excel(io.BytesIO(decoded))
        content_df = processing.load_df(df=content_df)

        return content_df
    except Exception as e:
        lw.log_writer(log_msg=f'При загрузки файла "{filename}" возникла ошибка: {e}')
        content_df = processing.no_data()

        return content_df


def get_quantity_tasks(df, pers_code, limit):
    if len(df[df.person_code == pers_code]['Номер'].unique()) == 0:
        return 0
    elif len(df[df.person_code == pers_code]['Номер'].unique()) > limit:
        return limit
    else:
        return len(df[df.person_code == pers_code]['Номер'].unique())


def count_time(x):
    return int(x[:x.find(':')]) + int(x[x.find(':') + 1:]) / 60


def data_table(data_df, staff_encrypt_df, filename):
    try:
        data_df['Описание'].fillna('Описание отсутствует', inplace=True)
        data_df['Время выполнения'] = pd.to_timedelta(data_df['Фактическое время выполнения'] - data_df['Дата/время '
                                                                                                        'регистрации'])
        data_df['Время выполнения'] = data_df['Время выполнения'].apply(lambda x: round(x.total_seconds() / 3600))
        data_df['Кем решен (сотрудник)'].fillna('Отсутствует', inplace=True)
        data_df['Кем решен (сотрудник)'] = data_df['Кем решен (сотрудник)'].apply(lambda x: x.title())
        data_df['Суммарное время реакции 1 линии.1'] = data_df['Суммарное время реакции 1 линии.1'].fillna('00:00')
        data_df['Суммарное время работы 1 линии.1'] = data_df['Суммарное время работы 1 линии.1'].fillna('00:00')
        data_df['Время решения из СУЭ, ч.'] = data_df[['Суммарное время реакции 1 линии.1',
                                                       'Суммарное время работы 1 линии.1']].apply(
            lambda row: count_time(row['Суммарное время работы 1 линии.1']) + count_time(
                row['Суммарное время работы 1 линии.1']), axis=1)
        data_df['Время решения из СУЭ, ч.'] = data_df['Время решения из СУЭ, ч.'].round(4)

        result_df = data_df.merge(staff_encrypt_df, left_on='Кем решен (сотрудник)', right_on='ФИО', how='left')
        lw.log_writer(log_msg=f'Файл "{filename}" успешно загружен')

        return result_df, 'Файл успешно загружен'
    except Exception as e:
        lw.log_writer(log_msg=f'Ошибка при загрузки файла: "{filename}": {e}')
        lw.log_writer(log_msg=f'Неверный формат файла "{filename}"')
        result_df = processing.no_data()

        return result_df, "Ошибка при загрузки файла"


def staff_table(staff_df):
    df_num = pd.DataFrame([x for x in range(1, len(staff_df) + 1)], columns=['person_code'])
    df_num['sort_code'] = np.random.choice(list(df_num.person_code), len(staff_df))
    df_num.sort_values('sort_code', inplace=True)
    df_num.reset_index(inplace=True)
    df_num.drop(['sort_code', 'index'], axis=1, inplace=True)

    result_df = pd.concat([df_num, staff_df], axis=1)

    return result_df


def write_key_file(staff_encrypt_df):
    current_date = datetime.datetime.now()
    key = str(random.randint(100000, 999999))

    filename_date = '_'.join([current_date.strftime('%d-%m-%Y'), key])
    filepath = 'key_files/'

    dataframe_to_write = staff_encrypt_df

    if os.path.exists(filepath):
        filename_key_file = f"key_{filename_date}"
        writer = pd.ExcelWriter(filepath + filename_key_file + '.xlsx')
        dataframe_to_write.to_excel(writer, index=False, sheet_name=filename_key_file)
        workbook = writer.book
        worksheet = writer.sheets[filename_key_file]
        writer.save()
    else:
        os.mkdir(filepath)
        filename_key_file = f"key_{filename_date}"
        writer = pd.ExcelWriter(filepath + filename_key_file + '.xlsx')
        dataframe_to_write.to_excel(writer, index=False, sheet_name=filename_key_file)
        workbook = writer.book
        worksheet = writer.sheets[filename_key_file]
        writer.save()

    return filename_key_file


def create_result_table(data_df, limit):
    df = pd.DataFrame(columns=['person_code', 'region', 'quantity_tasks', 'tasks_numbers'])

    for index, code in enumerate(data_df[data_df.person_code.notna()].person_code.unique()):
        region = data_df[data_df.person_code == code]['Регион'].unique()[0]
        quantity_tasks = get_quantity_tasks(df=data_df, pers_code=code, limit=limit)
        num_tasks = random.sample(list(data_df[data_df.person_code == code]['Номер'].unique()), k=quantity_tasks)
        df.loc[index] = code, region, quantity_tasks, num_tasks
    return df


def transform_result_table(filename_key_file, result_table, staff_df):
    df = pd.DataFrame(columns=[filename_key_file, 'person_code', 'region', 'tasks_numbers'])

    count = 0
    for j in range(len(result_table)):
        for i in range(len(result_table.tasks_numbers.loc[j])):
            df.loc[count] = 'x', result_table.person_code.loc[j], result_table.region.loc[j], \
                            result_table.tasks_numbers.loc[j][i]
            count += 1

    regions_dict = dict()
    for i in list(staff_df['Регион'].unique()):
        regions_dict[i] = [x for x in staff_df['Регион'].unique() if x != i]
    df['Проверяющий регион'] = df.region.apply(lambda x: random.choice(regions_dict[x]))

    df['Проверяющий сотрудник'] = ''

    return df


def create_total_table(result_table, data_df):
    def may_has_files(x):
        has_files_texts = ['скриншот', 'файл во вложении', '[img]', 'вложен', 'скрин', 'прикладываю', 'прилага', '.doc',
                           '.jpg', '.png', 'текст письма: описание отсутствует (пустое тело письма).', 'приложен',
                           'тема письма: тема отсутствует. текст письма: описание отсутствует (пустое тело письма).']
        for phrase in has_files_texts:
            if phrase in x.lower():
                return 'Да'
        return 'Нет'

    result_table = result_table.merge(data_df[['Номер', 'Описание', 'Сложность', 'Подсистема', 'Категория',
                                               'Описание решения', 'Количество уточнений', 'Количество возобновлений',
                                               'Время выполнения', 'Время решения из СУЭ, ч.']],
                                      how='left',
                                      left_on='tasks_numbers',
                                      right_on='Номер')

    result_table['Есть вложения?'] = result_table['Описание'].apply(lambda x: may_has_files(x))

    result_table.rename(columns=dict(person_code='Код сотрудника',
                                     region='Регион сотрудника',
                                     tasks_numbers='Номер задачи'),
                        inplace=True)
    result_table.rename(columns={'Количество возобновлений': 'Количество возобновлений (max 4)',
                                 'Время выполнения': 'Время выполнения, ч (max 24 ч.)',
                                 },
                        inplace=True)
    result_table.drop('Номер задачи', axis=1, inplace=True)
    result_table.sort_values(['Проверяющий регион', 'Проверяющий сотрудник'], ascending=True, inplace=True)
    result_table[['Оценка', 'Комментарий к оценке']] = ''

    return result_table


def get_difficult_level(df):
    df['Аналитические признаки'] = df['Аналитические признаки'].fillna('')
    df['Сложность'] = df['Аналитические признаки'].apply(lambda x: x.split(','))
    df['Сложность'] = df['Сложность'].apply(lambda row: [item for item in row if item.strip().isdigit()])
    df['Сложность'] = df['Сложность'].apply(lambda x: x[len(x) - 1] if len(x) > 0 else 'Не указано')

    return df


def get_category_level(df):
    df['Аналитические признаки'] = df['Аналитические признаки'].fillna('')
    df['Категория'] = df['Аналитические признаки'].apply(lambda x: x.split(','))
    df['Категория'] = df['Категория'].apply(lambda row: [item for item in row if not item.strip().isdigit()])
    df['Категория'] = df['Категория'].apply(lambda x: [x[i].strip() for i in range(len(x))])
    df['Категория'] = df['Категория'].apply(lambda x: x[0] if len(x) > 0 else x)
    df['Категория'] = df['Категория'].apply(lambda x: '' if x == [] else x)
    df['Категория'] = df['Категория'].apply(lambda x: 'Не указано' if x == '' else x)

    return df


def main_categories(df):
    df['Подсистема'] = ''
    df.loc[df[df['Категория'].isin(cat_list.zkgu_list)].index, 'Подсистема'] = 'ЗКГУ'
    df.loc[df[df['Категория'].isin(cat_list.bgu_list)].index, 'Подсистема'] = 'БГУ'
    df.loc[df[df['Категория'].isin(cat_list.com_list)].index, 'Подсистема'] = 'Командирование'
    df.loc[df[df['Категория'].isin(cat_list.admin_list)].index, 'Подсистема'] = 'Администрирование'

    return df
