import configparser

from sqlalchemy import create_engine


def write_config(conf):
    with open('assets/config.ini', "w") as file_object:
        conf.write(file_object)


cfg_parser = configparser.ConfigParser()
cfg_parser.read(r'assets/settings.rkz', encoding="utf-8")

db_username = cfg_parser['connect']['username']
db_password = cfg_parser['connect']['password']
db_name = cfg_parser['connect']['db']
db_host = cfg_parser['connect']['host']
db_port = cfg_parser['connect']['port']
db_dialect = cfg_parser['connect']['dialect']

table = cfg_parser['table_names']['db_table']

conn_string = create_engine(f'{db_dialect}://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}')


config = configparser.ConfigParser()
config.read(r'assets/config.ini', encoding="utf-8")

max_tasks_limit = config['main']['max_tasks_limit']
