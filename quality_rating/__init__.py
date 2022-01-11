import pandas as pd


def load_staff_table(table_name, connection_string):
    df = pd.read_sql(f"SELECT * from {table_name}", con=connection_string)
    df['state'] = df['state'].apply(lambda x: 'Работает' if x == 'y' else 'Уволен')
    df['works_w_tasks'] = df['works_w_tasks'].apply(lambda x: 'Да' if x == 'y' else 'Нет')
    df['bgu'] = df['bgu'].apply(lambda x: 'Да' if x == 1 else 'Нет')
    df['zkgu'] = df['zkgu'].apply(lambda x: 'Да' if x == 1 else 'Нет')
    df['admin'] = df['admin'].apply(lambda x: 'Да' if x == 1 else 'Нет')
    df['command'] = df['command'].apply(lambda x: 'Да' if x == 1 else 'Нет')

    df.sort_values(['fio'], ascending=True, inplace=True)

    df.columns = [i for i in range(len(df.columns))]

    return df


def set_staff_columns():

    col_name_list = [
        ['ФИО', ''], ['Регион', ''], ['Статус', ''], ['Участие в оценке', ''], ['Подсистемы', 'ПУНФА/ПУИО'],
        ['Подсистемы', 'ПУОТ'], ['Подсистемы', 'Администрирование'], ['Подсистемы', 'Командирование']
    ]
    columns = [{'name': name, 'id': index} for index, name in enumerate(col_name_list)]

    return columns


def get_filter_options(df, filter_name):
    if filter_name == 'state':
        filter_query_options = [{'label': i, 'value': i} for i in df[2].unique()]
    elif filter_name == 'works_w_tasks':
        filter_query_options = [{'label': i, 'value': i} for i in df[3].unique()]
    else:
        filter_query_options = [{'label': i, 'value': i} for i in df[1].unique()]
    filter_query_options.insert(0, dict(label='Все', value='Все'))

    return filter_query_options

