import base64
import io

import pandas as pd

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
        total_decrypt_df = df.merge(df_key[['person_code', 'ФИО']], how='left', left_on='Код сотрудника',
                                    right_on='person_code')
        total_decrypt_df.drop([df.columns[0], 'person_code'], axis=1, inplace=True)
        if 'Решение ' and 'Время решения' and 'Кол-во возвратов' in df.columns:
            total_decrypt_df = total_decrypt_df[['ФИО', 'Код сотрудника', 'Регион сотрудника', 'Проверяющий регион',
                                                 'Проверяющий сотрудник', 'Описание', 'Описание решения',
                                                 'Количество уточнений', 'Количество возобновлений (max 4)',
                                                 'Время выполнения (max 24 ч.)', 'Есть вложения?', 'Решение',
                                                 'Время решения', 'Кол-во возвратов']]
        # total_decrypt_df['Итоговая оценка'] = \
        #     total_decrypt_df['Решение'] + total_decrypt_df['Время решения'] + total_decrypt_df['Кол-во возвратов']
        #
        # total_decrypt_df_pivot = total_decrypt_df.pivot_table(index=['ФИО'],
        #                                                       values=['Решение', 'Время решения', 'Кол-во возвратов',
        #                                                               'Итоговая оценка'],
        #                                                       aggfunc='sum')
        # total_decrypt_df_pivot = total_decrypt_df_pivot[['Решение', 'Время решения', 'Кол-во возвратов',
        #                                                  'Итоговая оценка']]
        total_decrypt_df_pivot = total_decrypt_df.pivot_table(index=['ФИО'],
                                                              values=['Решение', 'Время решения', 'Кол-во возвратов'],
                                                              aggfunc='mean')

        total_decrypt_df_pivot = total_decrypt_df_pivot[['Решение', 'Время решения', 'Кол-во возвратов']]

        for column_name in total_decrypt_df_pivot.columns:
            total_decrypt_df_pivot[column_name] = total_decrypt_df_pivot[column_name].apply(lambda x: round(x, 2))

        total_decrypt_df_pivot['Итоговая оценка'] = total_decrypt_df_pivot[['Решение', 'Время решения',
                                                                            'Кол-во возвратов']].sum(axis=1)
        total_decrypt_df_pivot['Итоговая оценка'] = total_decrypt_df_pivot['Итоговая оценка'].\
            apply(lambda x: round(x, 2))

        total_decrypt_df_pivot = total_decrypt_df_pivot.reset_index()

        # total_decrypt_df.sort_values(['Проверяющий регион', 'Проверяющий сотрудник'], ascending=True, inplace=True)
        lw.log_writer(log_msg=f'Файл "{filename}" успешно расшифрован')
        return total_decrypt_df_pivot, "Файл успешно расшифрован"
    except Exception as e:
        lw.log_writer(log_msg=f'Ошибка при расшифровки файла: "{filename}": {e}')
        lw.log_writer(log_msg=f'Не найден ключевой файл для расшифровки файла "{filename}" или неверный формат файла '
                              f'"{filename}"')
        decrypt_df = processing.no_data()

        return decrypt_df, "Ошибка при обработке файла: не найден ключевой файл для расшифровки или неверный формат " \
                           "файла "
