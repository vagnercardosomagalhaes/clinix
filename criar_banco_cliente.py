import pymysql
import configparser
import os
import django
import sys

from django.conf import settings
from django.core.management import call_command

# Caminho do settings.py
sys.path.append('C:\\Dev\\ConsultorioDigital')  # Altere se o caminho do projeto for outro
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'consultoriodigital.settings')  # Nome do seu projeto Django

# Lê o nome do banco no bd.ini
config = configparser.ConfigParser()
config.read('C:\\cdigital\\bd.ini')
nome_banco = config.get('database', 'nome', fallback=None)

if not nome_banco:
    print("Banco de dados não definido em C:\\cdigital\\bd.ini")
    exit()

# Configurações da conexão
usuario = 'Usuario_Root'
senha = 'Tr18365518AaBbCcDdEe#!'
host = 'localhost'
porta = 3308

# Cria o banco de dados
try:
    conexao = pymysql.connect(user=usuario, password=senha, host=host, port=porta)
    with conexao.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{nome_banco}` DEFAULT CHARACTER SET utf8mb4;")
    conexao.commit()
    conexao.close()
    print(f"Banco de dados `{nome_banco}` criado ou já existia.")
except Exception as e:
    print(f"Erro ao criar banco: {e}")
    exit()

# Inicializa o Django
django.setup()

# Altera dinamicamente o settings.DATABASES para apontar para o banco criado
settings.DATABASES['default']['NAME'] = nome_banco
settings.DATABASES['default']['USER'] = usuario
settings.DATABASES['default']['PASSWORD'] = senha
settings.DATABASES['default']['HOST'] = host
settings.DATABASES['default']['PORT'] = porta

# Executa o migrate
try:
    print("Executando migrate...")
    call_command('migrate', database='default', interactive=False)
    print("Migrate concluído com sucesso.")
except Exception as e:
    print(f"Erro ao executar migrate: {e}")
 