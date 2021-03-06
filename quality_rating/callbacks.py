import dash
from dash.dependencies import Output, Input, State

import pandas as pd
import datetime

import quality_rating as qr
import quality_rating.decrypt as decrypt
import quality_rating.encrypt as encrypt
import quality_rating.processing as processing
from quality_rating.load_cfg import config, write_config, conn_string, table, db_schema


def register_callbacks(app):
    @app.callback(Output('encrypt_storage', 'data'),
                  Output('error_msg_encrypt', 'children'),
                  Output('error_msg_encrypt', 'style'),
                  Output('curr_tasks_input', 'value'),
                  Output('curr_lim', 'children'),
                  Input('upload-data', 'contents'),
                  Input('upload-data', 'filename'),
                  Input('submit_btn', 'n_clicks'),
                  State('curr_tasks_input', 'value')
                  )
    def encrypt_file(contents, filename, clicks, value):
        max_tasks_limit = config['main']['max_tasks_limit']
        current_limit = value
        if current_limit != max_tasks_limit:
            config.set('main', 'max_tasks_limit', str(current_limit))
            write_config(conf=config)

        if clicks:
            current_limit = value
            if current_limit != max_tasks_limit:
                config.set('main', 'max_tasks_limit', str(current_limit))
                write_config(conf=config)
        config_tasks_limit = config['main']['max_tasks_limit']

        if contents is not None:
            incoming_df = encrypt.parse_contents_encrypt(contents=contents,
                                                         filename=filename)

            staff_encrypt_df = encrypt.staff_table(staff_df=encrypt.staff_info_df)

            incoming_df = incoming_df[incoming_df['Кем решен (сотрудник)'].isin(staff_encrypt_df['ФИО'].unique())]

            if len(incoming_df) > 0:
                filename_key_file = encrypt.write_key_file(staff_encrypt_df=staff_encrypt_df)

                data_df = encrypt.data_table(data_df=incoming_df,
                                             staff_encrypt_df=staff_encrypt_df,
                                             filename=filename)[0]

                msg = encrypt.data_table(data_df=incoming_df,
                                         staff_encrypt_df=staff_encrypt_df,
                                         filename=filename)[1]

                data_df = encrypt.get_difficult_level(df=data_df)

                data_df = encrypt.get_category_level(df=data_df)

                data_df = encrypt.main_categories(df=data_df)

                result_df = encrypt.create_result_table(data_df=data_df, limit=int(current_limit))

                result_df = encrypt.transform_result_table(filename_key_file=filename_key_file,
                                                           result_table=result_df,
                                                           staff_df=encrypt.staff_info_df)

                total_df = encrypt.create_total_table(result_table=result_df,
                                                      data_df=data_df)

                style = processing.set_styles(msg=msg)

                return total_df.to_dict('records'), msg, style, current_limit, config_tasks_limit

            msg = encrypt.data_table(data_df=incoming_df,
                                     staff_encrypt_df=staff_encrypt_df,
                                     filename=filename)[1]
            total_df = processing.no_data()

            style = processing.set_styles(msg=msg)

            return total_df.to_dict('records'), msg, style, current_limit, config_tasks_limit

        else:
            return dash.no_update, dash.no_update, dash.no_update, current_limit, config_tasks_limit

    @app.callback(
        Output('table_encrypt', 'data'),
        Output('table_encrypt', 'columns'),
        Input('encrypt_storage', 'data'),
        Input('filter_query', 'value'),
    )
    def update_table(data, filter_region):
        if data:
            df = pd.DataFrame(data)
            columns = [{'name': i, 'id': i} for i in df.columns]
            if filter_region == 'Все регионы':
                return df.to_dict('records'), columns
            else:
                df = df[df['Проверяющий регион'] == filter_region]
                return df.to_dict('records'), columns
        return dash.no_update, dash.no_update

    @app.callback(Output('decrypt_storage', 'data'),
                  Output('error_msg', 'children'),
                  Output('error_msg', 'style'),
                  Output('person', 'options'),
                  Output('person_table', 'data'),
                  Output('person_table', 'columns'),
                  Output('regions', 'options'),
                  Output('total_table_store', 'data'),
                  Input('upload-data_decrypt', 'contents'),
                  Input('upload-data_decrypt', 'filename'),
                  Input('person', 'value'),
                  Input('regions', 'value')
                  )
    def decrypt_file(contents, filename, person, region):
        staff_df = processing.load_staff(table_name=table, connection_string=conn_string)
        if contents is not None:
            incoming_df = decrypt.parse_contents_decrypt(
                contents=contents,
                filename=filename
            )
            if len(incoming_df) > 0:
                decrypted_df = decrypt.load_data(
                    df=incoming_df,
                    filename=filename
                )[0]
                stored_df = staff_df.merge(decrypted_df[['ФИО', 'Номер', 'Проверяющий регион', 'Описание',
                                                         'Описание решения', 'Оценка', 'Комментарий к оценке']],
                                           how='right',
                                           on='ФИО')

                total_df, options, regions = processing.filter_region_person(
                    df=stored_df,
                    person=person,
                    region=region
                )

                count_mean_difficult_level_df = decrypt.count_mean_difficult_level(df=decrypted_df)

                decrypted_df = decrypt.make_decrypted_table(mean_diff_level_df=count_mean_difficult_level_df,
                                                            decrypt_df=decrypted_df)

                msg = decrypt.load_data(df=incoming_df,
                                        filename=filename)[1]

                style = processing.set_styles(msg=msg)

                return (decrypted_df.to_dict('records'), msg,
                        style, options, total_df.to_dict('records'), [{'name': i, 'id': i} for i in total_df.columns],
                        regions, stored_df.to_dict('records'))

            msg = decrypt.load_data(df=incoming_df,
                                    filename=filename)[1]

            style = processing.set_styles(msg=msg)

            decrypted_df = processing.no_data()

            return (decrypted_df.to_dict('records'), msg, style, dash.no_update, dash.no_update, dash.no_update,
                    dash.no_update, dash.no_update)
        else:
            return (dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update,
                    dash.no_update, dash.no_update)

    @app.callback(Output('table_decrypt', 'data'),
                  Output('table_decrypt', 'columns'),
                  Input('decrypt_storage', 'data'),
                  Input('filter_query_total', 'value'),
                  )
    def upd_table_decrypt(data, filter_region):
        if data:
            decrypt_df = pd.DataFrame(data)
            columns = [{'name': column, 'id': column} for column in decrypt_df.columns]
            if filter_region == 'Все регионы':
                return decrypt_df.to_dict('records'), columns
            else:
                decrypt_df = decrypt_df[decrypt_df['Регион сотрудника'] == filter_region]
                return decrypt_df.to_dict('records'), columns
        return dash.no_update, dash.no_update

    @app.callback(
        Output('load_data_label', 'children'),
        Output('choose_db', 'options'),
        Input('total_table_store', 'data'),
        Input('load_data_to_db', 'n_clicks')
    )
    def write_df_to_db(data, clicks):
        table_options = processing.load_db_dropdown(con=conn_string,
                                                    schema=db_schema)
        if clicks:
            cur_date = datetime.date.today().strftime('%d_%m_%Y')
            pd.DataFrame(data).to_sql(
                '_'.join(['result', cur_date]),
                con=conn_string,
                schema=db_schema,
                if_exists='replace',
                index=False
            )
            msg = 'Таблица записана в базу данных'
            table_options = processing.load_db_dropdown(con=conn_string,
                                                        schema=db_schema)
            return msg, table_options
        return dash.no_update, table_options

    @app.callback(
        Output('db_table', 'data'),
        Output('db_table', 'columns'),
        Input('choose_db', 'value')
    )
    def load_table_from_db(table_name):
        if table_name:
            df = processing.load_result_from_db(table=table_name,
                                                conn=conn_string,
                                                schema=db_schema)
            columns = [{'name': i, 'id': i} for i in df.columns]
            return df.to_dict('records'), columns
        return dash.no_update, dash.no_update

    @app.callback(
        Output('table_staff', 'data'),
        Output('table_staff', 'columns'),
        Input('filter_query_staff', 'value'),
        Input('filter_query_works', 'value'),
        Input('filter_query_tasks', 'value')
    )
    def filter_staff_table(region, state, work_tasks):
        staff_df = qr.load_staff_table(table_name=table, connection_string=conn_string)
        staff_columns = qr.set_staff_columns()

        if region == 'Все' and state == 'Все' and work_tasks == 'Все':
            return staff_df.to_dict('records'), staff_columns

        if region != 'Все' and state != 'Все' and work_tasks != 'Все':
            staff_df = staff_df[(staff_df[1] == region) & (staff_df[2] == state) & (staff_df[3] == work_tasks)]
            return staff_df.to_dict('records'), staff_columns

        if region == 'Все' and state != 'Все' and work_tasks != 'Все':
            staff_df = staff_df[(staff_df[2] == state) & (staff_df[3] == work_tasks)]
            return staff_df.to_dict('records'), staff_columns

        if region != 'Все' and state == 'Все' and work_tasks != 'Все':
            staff_df = staff_df[(staff_df[1] == region) & (staff_df[3] == work_tasks)]
            return staff_df.to_dict('records'), staff_columns

        if region != 'Все' and state != 'Все' and work_tasks == 'Все':
            staff_df = staff_df[(staff_df[1] == region) & (staff_df[2] == state)]
            return staff_df.to_dict('records'), staff_columns

        if region == 'Все' and state == 'Все' and work_tasks != 'Все':
            staff_df = staff_df[staff_df[3] == work_tasks]
            return staff_df.to_dict('records'), staff_columns

        if region == 'Все' and state != 'Все' and work_tasks == 'Все':
            staff_df = staff_df[(staff_df[2] == state)]
            return staff_df.to_dict('records'), staff_columns

        if region != 'Все' and state == 'Все' and work_tasks == 'Все':
            staff_df = staff_df[(staff_df[1] == region)]
            return staff_df.to_dict('records'), staff_columns

        return dash.no_update, dash.no_update

    @app.callback(
        Output('load_state', 'children'),
        Output('load_state', 'style'),
        Output('refresh_staff_table', 'href'),
        Input('load_staff_to_db', 'n_clicks'),
        Input('new_staff_fio', 'value'),
        Input('add_new_staff_region', 'value'),
        Input('add_new_staff_work', 'value'),
        Input('add_new_staff_task', 'value'),
        Input('add_new_staff_subs', 'value'),
        prevent_initial_call=True,
    )
    def write_new_staff(n_clicks, fio, region, work, task, subs):
        if n_clicks:
            row = qr.make_row(fio=fio, region=region, work=work, task=task, subs=subs)

            df = pd.DataFrame(columns=['fio', 'region', 'state', 'works_w_tasks', 'bgu', 'zkgu', 'admin', 'command'])
            df.loc[0] = row
            df.to_sql(table,
                      con=conn_string,
                      index=False,
                      if_exists='append')
            return 'Success', dict(color='green'), "/"
        return dash.no_update, dash.no_update, dash.no_update

    @app.callback(
        Output('modify_staff_fio', 'value'),
        Output('modify_staff_region', 'value'),
        Output('modify_staff_work', 'value'),
        Output('modify_staff_task', 'value'),
        Output('modify_staff_subs', 'value'),
        Input('list_staff_fio_modify', 'value')
    )
    def fill_form(fio):
        df = qr.load_staff_table(table_name=table, connection_string=conn_string)
        if fio:
            row = df[df[0] == fio].iloc[0].tolist()

            subs_type = [index for index, element in enumerate(row[4:]) if element == 'Да']
            if subs_type == [0]:
                subs = 'ПУНФА/ПУИО'
            elif subs_type == [1]:
                subs = 'ПУОТ'
            elif subs_type == [2]:
                subs = 'Администрирование'
            elif subs_type == [3]:
                subs = 'Командирование'
            else:
                subs = ''
            return row[0], row[1], row[2], row[3], subs
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    @app.callback(
        Output('modify_state', 'children'),
        Output('modify_state', 'style'),
        Output('refresh_modify_staff_table', 'href'),
        Input('list_staff_fio_modify', 'value'),
        Input('modify_staff_to_db', 'n_clicks'),
        Input('modify_staff_fio', 'value'),
        Input('modify_staff_region', 'value'),
        Input('modify_staff_work', 'value'),
        Input('modify_staff_task', 'value'),
        Input('modify_staff_subs', 'value'),
        prevent_initial_call=True,
    )
    def modify_staff(fio_index, n_clicks, fio, region, work, task, subs):
        if n_clicks and fio_index:
            df = pd.read_sql(f"SELECT * from {table}", con=conn_string)
            mask = df[df['fio'] == fio_index].index
            row = qr.make_row(fio=fio, region=region, work=work, task=task, subs=subs)

            df.loc[mask, df.columns] = row

            df.to_sql(table,
                      con=conn_string,
                      index=False,
                      if_exists='replace')

            return 'Success', dict(color='green'), '/'
        return dash.no_update, dash.no_update
