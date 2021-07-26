import base64
import io

import pandas as pd
from statistics import mean

import quality_rating.log_writer as lw
import quality_rating.processing as processing


def parse_contents_decrypt(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        content_df = pd.read_excel(io.BytesIO(decoded))
        lw.log_writer(log_msg=f'Файл "{filename}" загружен')

        return content_df
    except Exception as e:
        lw.log_writer(log_msg=f'При загрузки файла "{filename}" возникла ошибка: {e}')
        content_df = processing.no_data()

        return content_df


def load_data(df, filename):
    try:
        df_key = pd.read_excel(f'key_files\\{df.columns[0]}.xlsx')
        decrypt_df = df.merge(df_key[['person_code', 'ФИО']],
                              how='left',
                              left_on='Код сотрудника',
                              right_on='person_code')

        decrypt_df.drop([df.columns[0], 'person_code'],
                        axis=1,
                        inplace=True)
        if 'Решение' and 'Время решения' and 'Кол-во возвратов' in df.columns:
            decrypt_df = decrypt_df[['ФИО', 'Код сотрудника', 'Регион сотрудника', 'Проверяющий регион',
                                     'Проверяющий сотрудник', 'Описание', 'Сложность', 'Описание решения',
                                     'Количество уточнений', 'Количество возобновлений (max 4)',
                                     'Время выполнения (max 24 ч.)', 'Есть вложения?', 'Решение', 'Время решения',
                                     'Кол-во возвратов']]

        lw.log_writer(log_msg=f'Файл "{filename}" успешно расшифрован')
        return decrypt_df, "Файл успешно расшифрован"
    except Exception as e:
        lw.log_writer(log_msg=f'Ошибка при расшифровки файла: "{filename}": {e}')
        lw.log_writer(log_msg=f'Не найден ключевой файл для расшифровки файла "{filename}" или неверный формат файла '
                              f'"{filename}"')
        decrypt_df = processing.no_data()

        return decrypt_df, "Ошибка при обработке файла: не найден ключевой файл для расшифровки или неверный формат " \
                           "файла "


def count_mean_difficult_level(df):
    difficult_level_dict = dict()
    for person in df['ФИО'].unique():
        difficult_list = [dif for dif in df[df['ФИО'] == person]['Сложность'].tolist() if dif.isdigit()]
        if difficult_list:
            difficult_level_dict[person] = round(mean(list(map(int, difficult_list))), 2)
        else:
            difficult_level_dict[person] = 'Не указан'
    return pd.DataFrame(difficult_level_dict, index=['Средний уровень сложности'])


def make_decrypted_table(mean_diff_level_df, decrypt_df):
    decrypt_df_pivot = decrypt_df.pivot_table(index=['ФИО'],
                                              values=['Решение', 'Время решения', 'Кол-во возвратов'],
                                              aggfunc='mean')

    decrypt_df_pivot = decrypt_df_pivot[['Решение', 'Время решения', 'Кол-во возвратов']]

    for column_name in decrypt_df_pivot.columns:
        decrypt_df_pivot[column_name] = decrypt_df_pivot[column_name].apply(lambda x: round(x, 2))

    decrypt_df_pivot['Итоговая оценка'] = decrypt_df_pivot[['Решение', 'Время решения', 'Кол-во возвратов']].sum(axis=1)

    decrypt_df_pivot['Итоговая оценка'] = decrypt_df_pivot['Итоговая оценка'].apply(lambda x: round(x, 2))

    decrypt_df_pivot = decrypt_df_pivot.reset_index()

    # decrypt_df.sort_values(['Проверяющий регион', 'Проверяющий сотрудник'], ascending=True, inplace=True)

    mean_diff_level_df = mean_diff_level_df.T.reset_index().rename(columns={'index': 'ФИО'})
    decrypt_df_pivot = decrypt_df_pivot.merge(mean_diff_level_df, on='ФИО', how='left')

    return decrypt_df_pivot
