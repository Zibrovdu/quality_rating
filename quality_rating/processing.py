import pandas as pd
import numpy as np


def load_staff(table_name, connection_string):
    df = pd.read_sql(f"SELECT fio, region from {table_name}", con=connection_string)
    df.sort_values(['region', 'fio'], ascending=True, inplace=True)
    df.columns = ['ФИО', 'Регион']
    return df


def no_data():
    df = pd.DataFrame(columns=['ФИО', 'Код сотрудника', 'Регион сотрудника', 'Проверяющий регион',
                               'Проверяющий сотрудник', 'Описание', 'Сложность', 'Категория', 'Описание решения',
                               'Количество уточнений', 'Количество возобновлений (max 4)',
                               'Время выполнения (max 24 ч.)', 'Есть вложения?'])
    return df


def read_history_data():
    history_data = ''
    with open('assets/history.txt', 'r', encoding="utf8") as history_text_file:
        for line in history_text_file:
            history_data += line
        return history_data


def load_df(df):
    df.columns = ['Дата/время регистрации', 'Тип', 'Номер', 'Технический статус', 'Услуга', 'Компонент', 'Вид запроса',
                  'Описание', 'Конфигурационные единицы', 'Ответственный (группа)', 'Ответственный (сотрудник)',
                  'Плановое время выполнения', 'Просрочен крайний срок', 'Фактическое время выполнения', 'Код закрытия',
                  'Описание решения', 'Кем решен (группа)', 'Кем решен (сотрудник)', 'Количество уточнений',
                  'Количество возобновлений', 'Приоритет', 'Критичность', 'Приоритет.1', 'Способ обращения',
                  'Качество проведения работ по Запросу', 'Расположение в котором необходимо произвести работы',
                  'Получатель услуг', 'Головное подразделение Пользователя на момент создания запроса',
                  'Головной запрос', 'Суммарное время уточнений', 'Техническое описание', 'Список связанных запросов',
                  'Статус исполнения дочерних запросов', 'Суммарное время реакции 1 линии',
                  'Суммарное время реакции 2 линии', 'Суммарное время реакции 3 линии',
                  'Суммарное время реакции 4 линии', 'Суммарное время работы 1 линии',
                  'Суммарное время работы 2 линии', 'Суммарное время работы 3 линии', 'Суммарное время работы 4 линии',
                  'Дата изменения', 'Аналитические признаки', 'Статус', 'Суммарное время уточнений.1',
                  'Внешний идентификатор', 'Версия ППО', 'Причина ожидания', 'Правило входящей почты',
                  'Количество возобновлений после автоматического решения', 'Номер ВП', 'Активность', 'Контур',
                  'Область', 'Среда', 'Суммарное время уточнений.2', 'Вариант решения', 'Номер в Jira', 'Номер в СУВВ',
                  'Головное подразделение Пользователя', 'Суммарное время уточнений.3',
                  'Суммарное время реакции 1 линии.1', 'Суммарное время реакции 2 линии.1',
                  'Суммарное время реакции 3 линии.1', 'Суммарное время реакции 4 линии.1',
                  'Суммарное время работы 1 линии.1', 'Суммарное время работы 2 линии.1',
                  'Суммарное время работы 3 линии.1', 'Суммарное время работы 4 линии.1',
                  'Количество возвратов оператору', 'VIP организация', 'ИНН', 'Кем решен', 'Головной компонент',
                  'Инициатор', 'Автор', 'Тип организации получателя', 'Дата и время возврата в работу',
                  'Дата и время возникновения аварии', 'Дата и время устранения аварии',
                  'Проблемы в рамках которых ведутся работы', 'Измененные статьи БЗ']
    df = df[['Дата/время регистрации', 'Тип', 'Номер', 'Технический статус', 'Описание', 'Ответственный (сотрудник)',
             'Плановое время выполнения', 'Просрочен крайний срок', 'Фактическое время выполнения', 'Код закрытия',
             'Описание решения', 'Кем решен (группа)', 'Кем решен (сотрудник)', 'Количество уточнений',
             'Количество возобновлений', 'Приоритет', 'Аналитические признаки', 'Статус', 'Причина ожидания',
             'Кем решен']]
    df = df[(df['Тип'] != 'Проблема') & (df['Тип'] != 'Массовый инцидент')]
    df = df[(df['Код закрытия'] != 'Дублирование') &
            (df['Код закрытия'] != 'Неверное назначение') &
            (df['Код закрытия'] != 'Отозвано Пользователем')]
    df = df[df['Технический статус'] == 'Закрыт']
    df['Описание решения'] = df['Описание решения'].fillna('')
    df['del_col'] = df['Описание решения'].apply(lambda s: 1 if ('уточнение не предоставлено' in s.lower()) or
                                                                ('неверная группа назначения' in s.lower()) or
                                                                ('прошу назначить на группу' in s.lower()) or
                                                                ('дубль обращения' in s.lower()) else 0)
    df.drop(df[df['del_col'] == 1].index, inplace=True)
    df.drop('del_col', axis=1, inplace=True)
    return df


def set_styles(msg):
    if 'Ошибка'.lower() in str(msg).lower():
        style = dict(color='red', fontWeight='bold')
    else:
        style = dict(color='green', fontWeight='bold')
    return style


def filter_region_person(filter_df, staff_df, person, region):
    total_df = staff_df.merge(filter_df[['ФИО', 'Номер', 'Описание', 'Описание решения', 'Оценка',
                                         'Комментарий к оценке']],
                              how='right',
                              on='ФИО')

    if (person == 'Все пользователи' and region == 'Все регионы') or (not person and not region):
        person_options = [{'label': item, 'value': item} for item in np.sort(total_df['ФИО'].unique())]
        person_options.insert(0, dict(label='Все пользователи', value='Все пользователи'))

        regions_options = [{'label': item, 'value': item} for item in np.sort(total_df['Регион'].unique())]
        regions_options.insert(0, dict(label='Все регионы', value='Все регионы'))

        return total_df, person_options, regions_options

    elif (person == 'Все пользователи' or not person) and (region != 'Все регионы' and region):

        total_df = total_df[total_df['Регион'] == region]

        person_options = [{'label': item, 'value': item} for item in np.sort(total_df['ФИО'].unique())]
        person_options.insert(0, dict(label='Все пользователи', value='Все пользователи'))

        regions_options = [{'label': item, 'value': item} for item in np.sort(total_df['Регион'].unique())]
        regions_options.insert(0, dict(label='Все регионы', value='Все регионы'))

        return total_df, person_options, regions_options

    elif (region == 'Все регионы' or not region) and (person != 'Все регионы' and person):
        total_df = total_df[total_df['ФИО'] == person]

        person_options = [{'label': item, 'value': item} for item in np.sort(total_df['ФИО'].unique())]
        person_options.insert(0, dict(label='Все пользователи', value='Все пользователи'))

        regions_options = [{'label': item, 'value': item} for item in np.sort(total_df['Регион'].unique())]
        regions_options.insert(0, dict(label='Все регионы', value='Все регионы'))

        return total_df, person_options, regions_options
    else:
        total_df = total_df[(total_df['ФИО'] == person) & (total_df['Регион'] == region)]

        person_options = [{'label': item, 'value': item} for item in np.sort(total_df['ФИО'].unique())]
        person_options.insert(0, dict(label='Все пользователи', value='Все пользователи'))

        regions_options = [{'label': item, 'value': item} for item in np.sort(total_df['Регион'].unique())]
        regions_options.insert(0, dict(label='Все регионы', value='Все регионы'))

        return total_df, person_options, regions_options
