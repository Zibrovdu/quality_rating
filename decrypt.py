import base64
import io

import pandas as pd

import log_writer as lw
import processing


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
        df_key = pd.read_excel(f'key_files/{df.columns[0]}.xlsx')
        print(df.columns[0])
        total_decrypt_df = df.merge(df_key[['person_code', 'ФИО']], how='left', left_on='Код сотрудника',
                                    right_on='person_code')
        total_decrypt_df.drop([df.columns[0], 'person_code'], axis=1, inplace=True)
        total_decrypt_df = total_decrypt_df[['ФИО', 'Код сотрудника', 'Регион сотрудника', 'Проверяющий регион',
                                             'Проверяющий сотрудник', 'Описание', 'Описание решения',
                                             'Количество уточнений', 'Количество возобновлений', 'Время выполнения',
                                             'Есть вложения?']]
        lw.log_writer(log_msg=f'Файл "{filename}" успешно расшифрован')
        return total_decrypt_df, "Файл успешно расшифрован"
    except Exception as e:
        lw.log_writer(log_msg=f'Ошибка при расшифровки файла: "{filename}": {e}')
        lw.log_writer(log_msg=f'Не найден ключевой файл для расшифровки файла "{filename}" или неверный формат файла '
                              f'"{filename}"')
        decrypt_df = processing.no_data()

        return decrypt_df, "Ошибка при обработке файла: не найден ключевой файл для расшифровки или неверный формат " \
                           "файла "
