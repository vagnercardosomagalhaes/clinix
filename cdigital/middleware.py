import configparser
from copy import deepcopy
from django.conf import settings
from django.db import connections


class ClienteDBMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        config = configparser.ConfigParser()
        config.read('C:\\cdigital\\bd.ini')
        nome_banco = config.get('database', 'nome', fallback=None)

        if nome_banco:
            # Registra dinamicamente a conexão com o nome do banco
            if nome_banco not in settings.DATABASES:
                db_config = deepcopy(settings.DATABASES['default'])
                db_config['NAME'] = nome_banco
                settings.DATABASES[nome_banco] = db_config

            # Fecha conexão antiga, se existir
            if nome_banco in connections:
                connections[nome_banco].close()
                del connections[nome_banco]

            # Define o nome do banco dinamicamente para usar depois nas views
            request.nome_banco_dinamico = nome_banco

        return self.get_response(request)