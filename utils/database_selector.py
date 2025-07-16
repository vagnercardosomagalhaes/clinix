import configparser
import os

def get_local_database_name():
    config = configparser.ConfigParser()
    caminho = 'C:\\cdigital\\bd.ini'
    if not os.path.exists(caminho):
        raise FileNotFoundError('Erro ao tentar acessar o sistema. Nome do banco de dados indefinido.')

    config.read(caminho)
    return config.get('database', 'nome', fallback='default')