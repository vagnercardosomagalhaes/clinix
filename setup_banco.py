import os
import django
import pymysql
import configparser
import sys
from django.conf import settings
from django.core.management import call_command


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurações MySQL
MYSQL_USER = 'Usuario_Root'
MYSQL_PASSWORD = 'Tr18365518AaBbCcDdEe#!'
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3308

# Lê o nome do banco do arquivo ini
config = configparser.ConfigParser()
config.read('C:\\cdigital\\bd.ini')
nome_banco = config.get('database', 'nome', fallback=None)

if not nome_banco:
    print("❌ Banco de dados não definido no arquivo bd.ini.")
    exit()

# Cria o banco se não existir
try:
    conexao = pymysql.connect(user=MYSQL_USER, password=MYSQL_PASSWORD, host=MYSQL_HOST, port=MYSQL_PORT)
    with conexao.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{nome_banco}` DEFAULT CHARACTER SET utf8mb4;")
    conexao.commit()
    conexao.close()
    print(f"✅ Banco `{nome_banco}` criado ou já existia.")
except Exception as e:
    print(f"❌ Erro ao criar banco: {e}")
    exit()

# Inicializa o Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "consultoriodigital.settings")  # ***********************************
django.setup()


# Adiciona dinamicamente o banco no settings
from django.conf import settings
from copy import deepcopy

# Clona a configuração do banco 'default'
banco_config = deepcopy(settings.DATABASES['default'])
banco_config['NAME'] = nome_banco

# Registra no settings com nome do banco lido
settings.DATABASES[nome_banco] = banco_config

#settings.DATABASES[nome_banco] = {
#    'ENGINE': 'django.db.backends.mysql',
#    'NAME': nome_banco,
#    'USER': MYSQL_USER,
#    'PASSWORD': MYSQL_PASSWORD,
#    'HOST': MYSQL_HOST,
#    'PORT': str(MYSQL_PORT),
#    'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"},
#    'TIME_ZONE': settings.TIME_ZONE,  # ✅ Adiciona a configuração de fuso
#}

# Roda as migrations para esse banco
print(f" Rodando migrations no banco `{nome_banco}`...")
call_command('migrate', database=nome_banco)
print(" Migrations finalizadas.")