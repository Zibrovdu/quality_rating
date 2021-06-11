import pandas as pd


def no_data():
    df = pd.DataFrame(columns=['ФИО', 'Код сотрудника', 'Регион сотрудника', 'Проверяющий регион',
                               'Проверяющий сотрудник', 'Описание', 'Описание решения', 'Количество уточнений',
                               'Количество возобновлений (max 4)', 'Время выполнения (max 24 ч.)', 'Есть вложения?'])
    return df


def read_history_data():
    history_data = ''
    with open('assets/history.txt', 'r', encoding="utf8") as history_text_file:
        for line in history_text_file:
            history_data += line
        return history_data


def load_df(df):
    df = df[['Дата/время регистрации', 'Номер', 'Технический статус', 'Описание', 'Ответственный (сотрудник)',
             'Плановое время выполнения', 'Просрочен крайний срок', 'Фактическое время выполнения',
             'Код закрытия', 'Описание решения', 'Кем решен (группа)', 'Кем решен (сотрудник)',
             'Количество уточнений', 'Количество возобновлений', 'Приоритет', 'Статус', 'Причина ожидания',
             'Кем решен']]
    return df


def set_styles(msg):
    if 'Ошибка'.lower() in str(msg).lower():
        style = dict(color='red', fontWeight='bold')
    else:
        style = dict(color='green', fontWeight='bold')
    return style
