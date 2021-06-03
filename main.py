import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from dash.dependencies import Input, Output

import decrypt
import encrypt
import processing

staff_tsokr_df = pd.read_excel(r'assets/Список сотрудников ЦОКР.xlsx')

app = dash.Dash(__name__,
                title='Оценка качества')

tab_selected_style = dict(backgroundColor='#ebecf1',
                          fontWeight='bold')
app.layout = html.Div([
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
                    html.Label('''ВАЖНО!!! Пожалуйста не удаляйте столбец № 1 из подготовленного программой файла.''',
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
                    html.Label('''ВАЖНО!!! Пожалуйста не удаляйте столбец № 1 из подготовленного программой файла.''',
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
        dcc.Tab(label='Сотрудники ЦОКР',
                value='about',
                children=[
                    html.Br(),
                    html.Br(),
                    html.Div([
                        dash_table.DataTable(id='table_staff',
                                             data=staff_tsokr_df.to_dict('records'),
                                             columns=[{'name': i, 'id': i} for i in staff_tsokr_df.columns],
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


@app.callback(Output('table_encrypt', 'data'),
              Output('table_encrypt', 'columns'),
              Output('error_msg_encrypt', 'children'),
              Output('error_msg_encrypt', 'style'),
              Input('upload-data', 'contents'),
              Input('upload-data', 'filename'))
def encrypt_file(contents, filename):
    if contents is not None:
        incoming_df = encrypt.parse_contents_encrypt(contents=contents,
                                                     filename=filename)

        staff_encrypt_df = encrypt.staff_table(staff_df=encrypt.staff_info_df)

        if len(incoming_df) > 0:
            filename_key_file = encrypt.write_key_file(staff_encrypt_df=staff_encrypt_df)

            data_df = encrypt.data_table(data_df=incoming_df,
                                         staff_encrypt_df=staff_encrypt_df,
                                         filename=filename)[0]
            msg = encrypt.data_table(data_df=incoming_df,
                                     staff_encrypt_df=staff_encrypt_df,
                                     filename=filename)[1]

            result_df = encrypt.create_result_table(data_df=data_df)

            result_df = encrypt.transform_result_table(filename_key_file=filename_key_file,
                                                       result_table=result_df,
                                                       staff_df=encrypt.staff_info_df)

            total_df = encrypt.create_total_table(result_table=result_df,
                                                  data_df=data_df)

            style = processing.set_styles(msg=msg)

            return total_df.to_dict('records'), [{'name': i, 'id': i} for i in total_df.columns], msg, style

        msg = encrypt.data_table(data_df=incoming_df,
                                 staff_encrypt_df=staff_encrypt_df,
                                 filename=filename)[1]
        total_df = processing.no_data()

        style = processing.set_styles(msg=msg)

        return total_df.to_dict('records'), [{'name': i, 'id': i} for i in total_df.columns], msg, style

    else:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update


@app.callback(Output('table_decrypt', 'data'),
              Output('table_decrypt', 'columns'),
              Output('error_msg', 'children'),
              Output('error_msg', 'style'),
              Input('upload-data_decrypt', 'contents'),
              Input('upload-data_decrypt', 'filename'))
def decrypt_file(contents, filename):
    if contents is not None:
        incoming_df = decrypt.parse_contents_decrypt(contents=contents,
                                                     filename=filename)
        if len(incoming_df) > 0:
            decrypted_df = decrypt.load_data(df=incoming_df,
                                             filename=filename)[0]

            msg = decrypt.load_data(df=incoming_df,
                                    filename=filename)[1]

            style = processing.set_styles(msg=msg)

            return decrypted_df.to_dict('records'), [{'name': i, 'id': i} for i in decrypted_df.columns], msg, style

        msg = decrypt.load_data(df=incoming_df,
                                filename=filename)[1]

        style = processing.set_styles(msg=msg)

        decrypted_df = processing.no_data()

        return decrypted_df.to_dict('records'), [{'name': i, 'id': i} for i in decrypted_df.columns], msg, style
    else:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update


if __name__ == '__main__':
    app.run_server(host='10.201.77.89')
