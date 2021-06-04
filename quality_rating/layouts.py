import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd

import quality_rating.processing as processing


def serve_layout():
    staff_oit_stsb_df = pd.read_excel(r'assets/Список сотрудников ЦОКР.xlsx')

    tab_selected_style = dict(backgroundColor='#ebecf1',
                              fontWeight='bold')
    layout = html.Div([
        html.Div([
            html.H2('Оценка качества отработанных второй линией технической поддержки обращений'),
            html.Img(src="assets/logo.png")],
            className="banner"),
        html.Br(),
        html.Br(),
        html.A('О программе',
               href='#modal-1',
               className='js-modal-open link'),
        html.Br(),
        html.Br(),
        dcc.Tabs(children=[
            dcc.Tab(label='Подготовка файла',
                    value='encrypt',
                    children=[
                        html.Label('''Загрузите файл с выполненными заявками. С порядком работы с программой, а также 
                        требованиями к формату файлов можно ознакомиться, зайдя в меню "О программе"''',
                                   className='labels_encrypt'),
                        html.Label(
                            '''ВАЖНО!!! Пожалуйста не удаляйте столбец № 1 из подготовленного программой файла.''',
                            className='labels_encrypt'),
                        html.Br(),
                        html.Br(),
                        dcc.Upload(
                            html.Button('Загрузить файл с данными'),
                            id='upload-data',
                            className='btn_load'),
                        html.Br(),
                        html.Span(id='error_msg_encrypt',
                                  className='labels_encrypt'),
                        html.Br(),
                        html.Br(),
                        html.Div([
                            dcc.Loading(
                                id="loading-1",
                                type="cube",
                                fullscreen=True,
                                children=html.Div([
                                    dash_table.DataTable(id='table_encrypt',
                                                         export_format='xlsx',
                                                         style_cell=dict(textAlign='center',
                                                                         whiteSpace='normal',
                                                                         height='auto'),
                                                         ),
                                ], id="loading-output-1", className='table_all')
                            ),
                        ], id='output-data-upload'),
                    ],
                    selected_style=tab_selected_style),
            dcc.Tab(label='Расшифровка файла',
                    value='decrypt',
                    children=[
                        html.Label('''Загрузите файл с выполненными заявками. С порядком работы с программой, а также 
                        требованиями к формату файлов можно ознакомиться, зайдя в меню "О программе"''',
                                   className='labels_encrypt'),
                        html.Label(
                            '''ВАЖНО!!! Пожалуйста не удаляйте столбец № 1 из подготовленного программой файла.''',
                            className='labels_encrypt'),
                        html.Br(),
                        html.Br(),
                        dcc.Upload(
                            html.Button('Загрузить файл с данными'),
                            id='upload-data_decrypt',
                            className='btn_load'),
                        html.Br(),
                        html.Span(id='error_msg',
                                  className='labels_encrypt'),
                        html.Br(),
                        html.Br(),
                        html.Div([
                            dcc.Loading(
                                id="loading-2",
                                type="cube",
                                fullscreen=True,
                                children=html.Div([
                                    dash_table.DataTable(id='table_decrypt',
                                                         export_format='xlsx',
                                                         style_cell=dict(textAlign='center',
                                                                         whiteSpace='normal',
                                                                         height='auto'),
                                                         ),
                                ],
                                    id="loading-output-2",
                                    className='table_all')
                            ),
                        ], id='output-data-upload_decrypt'),

                    ],
                    selected_style=tab_selected_style),
            dcc.Tab(label='Сотрудники ОИТ СЦБ',
                    value='about',
                    children=[
                        html.Br(),
                        html.Br(),
                        html.Div([
                            dash_table.DataTable(id='table_staff',
                                                 data=staff_oit_stsb_df.to_dict('records'),
                                                 columns=[{'name': i, 'id': i} for i in staff_oit_stsb_df.columns],
                                                 export_format='xlsx',
                                                 style_cell=dict(textAlign='center',
                                                                 whiteSpace='normal',
                                                                 height='auto'),

                                                 ),
                        ], id='output-data-upload_info',
                            className='table_staff'),

                    ],
                    selected_style=tab_selected_style)
        ], colors=dict(border='#ebecf1',
                       primary='#222780',
                       background='#33ccff')),
        html.Div([
            html.Div([
                html.Div([
                    html.Div(['О программе'
                              ], className='modal__dialog-header-content'),
                    html.Div([
                        html.Button([
                            html.Span('x')
                        ], className='js-modal-close modal__dialog-header-close-btn')
                    ], className='modal__dialog-header-close')
                ], className='modal__dialog-header'),
                html.Div([
                    html.Br(),
                    html.Div([
                        dcc.Textarea(value=processing.read_history_data(),
                                     readOnly=True,
                                     className='frame-history')
                    ]),
                    html.Br(),
                ], className='modal__dialog-body'),
                html.Div([
                    html.Button('Закрыть', className='js-modal-close modal__dialog-footer-close-btn')
                ], className='modal__dialog-footer')
            ], className='modal__dialog')
        ],
            id='modal-1',
            className='modal_about modal--l'),
        html.Script(src='assets/js/main.js'),

    ])

    return layout
