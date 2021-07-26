import dash
from dash.dependencies import Output, Input

import quality_rating.decrypt as decrypt
import quality_rating.encrypt as encrypt
import quality_rating.processing as processing


def register_callbacks(app):
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

                data_df = encrypt.get_difficult_level(df=data_df)

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

                count_mean_difficult_level_df = decrypt.count_mean_difficult_level(df=decrypted_df)

                decrypted_df = decrypt.make_decrypted_table(mean_diff_level_df=count_mean_difficult_level_df,
                                                            decrypt_df=decrypted_df)

                msg = decrypt.load_data(df=incoming_df,
                                        filename=filename)[1]

                style = processing.set_styles(msg=msg)
                # print(decrypted_df["Итоговая оценка"].max())

                return decrypted_df.to_dict('records'), [{'name': i, 'id': i} for i in decrypted_df.columns], msg, style

            msg = decrypt.load_data(df=incoming_df,
                                    filename=filename)[1]

            style = processing.set_styles(msg=msg)

            decrypted_df = processing.no_data()
            #
            # style_data_conditional = [
            #     {'if': {'filter_query': f'{{Итоговая оценка}} > {decrypted_df["Итоговая оценка"].max()}', },
            #      'backgroundColor': 'red'
            #      }]

            return decrypted_df.to_dict('records'), [{'name': i, 'id': i} for i in decrypted_df.columns], msg, style,
        else:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update
