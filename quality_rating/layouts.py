import dash_core_components as dcc
import dash_html_components as html
import dash_table

import quality_rating.processing as processing
from quality_rating.load_cfg import table, conn_string, config


def serve_layout():
    staff_oit_stsb_df = processing.load_staff(
        table_name=table,
        connection_string=conn_string
    )

    filter_query_options = [{'label': i, 'value': i} for i in staff_oit_stsb_df['Регион'].unique()]
    filter_query_options.insert(0, dict(label='Все регионы',
                                        value='Все регионы'))

    tab_selected_style = dict(backgroundColor='#dfe49b',
                              fontWeight='bold')

    max_tasks_limit = config['main']['max_tasks_limit']

    layout = html.Div([
        html.Div([
            html.H2(
                'Оценка качества обращений, отработанных второй линией технической поддержки'
            ),
            html.Img(
                src="assets/logo.png"
            )
        ],
            className="banner"),
        html.Br(),
        html.Br(),
        html.A(
            'О программе',
            href='#modal-1',
            className='js-modal-open link'
        ),
        html.Br(),
        html.Br(),
        dcc.Tabs(children=[
            dcc.Tab(
                label='Подготовка файла',
                value='encrypt',
                children=[
                    html.Label(
                        '''Загрузите файл с выполненными заявками. С порядком работы с программой, а также 
                            требованиями к формату файлов можно ознакомиться, зайдя в меню "О программе"''',
                        className='labels_encrypt'
                    ),
                    html.Label(
                        '''ВАЖНО!!! Пожалуйста не меняйте структуру сформированного файла (не удаляйте, не 
                            переименовывайте столбцы и не меняйте их порядок).''',
                        className='labels_encrypt'
                    ),
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Label(
                                    'Текущее количество задач, отбираемое для оценки сотрудника (от 1 до 10)',
                                    id='curr_tasks',
                                    className='lbl_limit'
                                ),
                                html.Label(
                                    '5',
                                    id='curr_lim',
                                    className='lbl_curr_lim'
                                ),
                            ]),
                            html.Div([
                                dcc.Input(
                                    id='curr_tasks_input',
                                    type='number',
                                    inputMode='numeric',
                                    min=1,
                                    max=10,
                                    step=1,
                                    value=max_tasks_limit,
                                    className='curr_tasks_input'
                                ),
                                html.Button(
                                    id='submit_btn',
                                    n_clicks=0,
                                    children='Установить',
                                    className='submit_btn'
                                ),
                            ]),
                        ]),
                    ]),
                    html.Br(),
                    html.Br(),
                    dcc.Upload(
                        html.Button(
                            'Загрузить файл с данными',
                            className='btn_loaders'
                        ),
                        id='upload-data',
                        className='btn_load'
                    ),
                    html.Br(),
                    html.Span(
                        id='error_msg_encrypt',
                        className='labels_encrypt'
                    ),
                    html.Br(),
                    html.Br(),
                    html.Div([
                        dcc.Loading(
                            id="loading-3",
                            type="cube",
                            fullscreen=True,
                            color='#9db33e',
                            children=dcc.Store(
                                id='memory_storage'
                            )
                        ),
                        html.Div([
                            html.Div([
                                html.Label(
                                    'Фильтр по столбцу "Проверяющий регион"',
                                    style=dict(fontSize='16px')
                                )
                            ],
                                className='bblock'),
                            html.Div([
                                dcc.Dropdown(
                                    id='filter_query',
                                    options=filter_query_options,
                                    value=filter_query_options[0]['value'],
                                    clearable=False,
                                    style=dict(width='250px',
                                               padding='0 20px',
                                               fontSize='16px')
                                )
                            ],
                                className='bblock')
                        ],
                            className='labels_encrypt'
                        ),
                    ]),
                    html.Div([
                        dcc.Loading(
                            id="loading-1",
                            type="cube",
                            fullscreen=True,
                            color='#9db33e',
                            children=html.Div([
                                dash_table.DataTable(
                                    id='table_encrypt',
                                    export_format='xlsx',
                                    css=[
                                        {'selector': 'table', 'rule': 'table-layout: fixed'}
                                    ],
                                    style_cell=dict(textAlign='center',
                                                    whiteSpace='normal',
                                                    height='auto'),
                                    style_cell_conditional=[
                                        {'if': {'column_id': 'Описание'}, 'width': '20%'},
                                        {'if': {'column_id': 'Описание решения'}, 'width': '20%'}
                                    ],
                                ),
                            ],
                                id="loading-output-1",
                                className='table_all'
                            )
                        ),
                    ],
                        id='output-data-upload'
                    ),
                ],
                selected_style=tab_selected_style),
            dcc.Tab(
                label='Расшифровка файла',
                value='decrypt',
                children=[
                    html.Label(
                        '''Загрузите файл сформированный ранее в котором проставлены оценки. Оценка (целое 
                        число от 0 до 5) должна быть проставлена в каждой ячейке столбца "Оценка". Ввод других значений,
                         а также пропуски не допускаются.
                         С порядком работы с программой, а также требованиями к формату файлов можно ознакомиться, зайдя
                          в меню "О программе"''',
                        className='labels_encrypt'
                    ),
                    html.Label(
                        '''ВАЖНО!!! Пожалуйста не меняйте структуру сформированного файла (не удаляйте, не 
                            переименовывайте столбцы и не меняйте их порядок)''',
                        className='labels_encrypt'
                    ),
                    html.Br(),
                    html.Br(),
                    dcc.Upload(
                        html.Button(
                            'Загрузить файл с данными',
                            className='btn_loaders'
                        ),
                        id='upload-data_decrypt',
                        className='btn_load'
                    ),
                    html.Br(),
                    html.Span(
                        id='error_msg',
                        className='labels_encrypt'
                    ),
                    html.Br(),
                    html.Br(),
                    html.A(
                        'Детализация',
                        href='#modal-2',
                        className='js-modal-open link'
                    ),
                    html.Br(),
                    html.Br(),
                    html.Div([
                        dcc.Loading(
                            id="loading-2",
                            type="cube",
                            color='#9db33e',
                            fullscreen=True,
                            children=html.Div([
                                dash_table.DataTable(
                                    id='table_decrypt',
                                    export_format='xlsx',
                                    style_cell=dict(textAlign='center',
                                                    whiteSpace='normal',
                                                    height='auto'),
                                ),
                            ],
                                id="loading-output-2",
                                className='table_all'
                            )
                        ),
                    ],
                        id='output-data-upload_decrypt'
                    ),
                ],
                selected_style=tab_selected_style
            ),
            dcc.Tab(
                label='Сотрудники ОИТ СЦБ',
                value='about',
                children=[
                    html.Br(),
                    html.Br(),
                    html.Div([
                        dash_table.DataTable(
                            id='table_staff',
                            data=staff_oit_stsb_df.to_dict('records'),
                            columns=[
                                {'name': i, 'id': i} for i in staff_oit_stsb_df.columns
                            ],
                            export_format='xlsx',
                            style_cell=dict(textAlign='center',
                                            whiteSpace='normal',
                                            height='auto'),
                        ),
                    ],
                        id='output-data-upload_info',
                        className='table_staff'
                    ),
                ],
                selected_style=tab_selected_style
            ),
            dcc.Tab(
                label='Хранение данных',
                value='db',
                children=[
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Label(
                                    'Выберите базу:',
                                    className='lbl_db'
                                )
                            ],
                                className='div_lbl_db'
                            ),
                            html.Div([
                                dcc.Dropdown(
                                    id='choose_db',
                                    clearable=False,
                                    searchable=True
                                )
                            ],
                                className='div_dropdown_db'
                            )
                        ]),
                        html.Div([
                            dash_table.DataTable(
                                id='db_table',
                                editable=True,
                                export_format='xlsx',
                                style_cell=dict(textAlign='center',
                                                whiteSpace='normal',
                                                height='auto'),
                            )
                        ],
                            className='table_all_1'
                        )
                    ])
                ],
                selected_style=tab_selected_style
            )
        ],
            colors=dict(border='#55761a',
                        primary='#55761a',
                        background='#9db33e')
        ),
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        'О программе'
                    ],
                        className='modal__dialog-header-content'
                    ),
                    html.Div([
                        html.Button([
                            html.Span('x')
                        ],
                            className='js-modal-close modal__dialog-header-close-btn'
                        )
                    ],
                        className='modal__dialog-header-close'
                    )
                ],
                    className='modal__dialog-header'
                ),
                html.Div([
                    html.Br(),
                    html.Div([
                        dcc.Textarea(
                            value=processing.read_history_data(),
                            readOnly=True,
                            className='frame-history'
                        )
                    ]),
                    html.Br(),
                ],
                    className='modal__dialog-body'
                ),
                html.Div([
                    html.Button(
                        'Закрыть',
                        className='js-modal-close modal__dialog-footer-close-btn'
                    )
                ],
                    className='modal__dialog-footer'
                )
            ],
                className='modal__dialog'
            )
        ],
            id='modal-1',
            className='modal_about modal--l'
        ),
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        'Детализация'
                    ],
                        className='modal__dialog-header-content'
                    ),
                    html.Div([
                        html.Button([
                            html.Span('x')
                        ],
                            className='js-modal-close modal__dialog-header-close-btn'
                        )
                    ],
                        className='modal__dialog-header-close'
                    )
                ],
                    className='modal__dialog-header'
                ),
                html.Div([
                    html.Br(),
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Label(
                                        'Выберите сотрудника',
                                        className='person_label'
                                    )
                                ]),
                                html.Div([
                                    dcc.Dropdown(
                                        id='person',
                                        clearable=False,
                                        searchable=False,
                                        placeholder='Выберите сотрудника'
                                    )
                                ],
                                    className='person_dropdown_div'
                                ),
                            ],
                                style=dict(display='inline-block')
                            ),
                            html.Div([
                                html.Div([
                                    html.Label(
                                        'Выберите регион',
                                        className='person_label'
                                    )
                                ]),
                                html.Div([
                                    dcc.Dropdown(
                                        id='regions',
                                        clearable=False,
                                        searchable=False,
                                        placeholder='Выберите регион'
                                    )
                                ],
                                    className='person_dropdown_div'
                                ),
                            ],
                                style=dict(display='inline-block')
                            ),
                        ]),
                        html.Br(),
                        html.Br(),
                        html.Div([
                            html.Div([
                                dcc.Loading(
                                    id='person_table_loading',
                                    fullscreen=False,
                                    children=[
                                        html.Div([
                                            dash_table.DataTable(
                                                id='person_table',
                                                export_format='xlsx',
                                                style_cell={
                                                    'whiteSpace': 'normal',
                                                    'height': 'auto',
                                                    'textAlign': 'center',
                                                    'backgroundColor': '#f0f8ff'
                                                },
                                            )
                                        ],
                                            className='dash_tables'
                                        ),
                                    ])
                            ]),
                        ],
                            className='div_table_person'
                        ),
                    ]),
                    html.Br(),
                ],
                    className='modal__dialog-body'
                ),
                html.Div([
                    html.Div([
                        html.Button(
                            'Закрыть',
                            className='js-modal-close modal__dialog-footer-close-btn'
                        )
                    ],
                        style=dict(display='inline-block')
                    ),
                    html.Div([
                        dcc.Store(
                            id='total_table_store'
                        ),
                        html.Div([
                            html.Button(
                                'Записать таблицу в базу',
                                id='load_data_to_db',
                                className='btn_loaders'
                            ),
                        ],
                            style=dict(display='inline-block')
                        ),
                        html.Div([
                            html.Label(
                                id='load_data_label'
                            )
                        ],
                            className='div_load_table_to_db_label'
                        )
                    ],
                        className='div_btn_load_to_db'
                    ),
                ],
                    className='modal__dialog-footer'
                )
            ],
                className='modal__dialog'
            )
        ],
            id='modal-2',
            className='modal_about modal--xl'
        ),
        html.Script(
            src='assets/js/main.js'
        ),
    ])
    return layout
