import os
import django
import pymysql
import configparser
import sys
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

# Roda as migrations para esse banco
print(f" Rodando migrations no banco `{nome_banco}`...")
call_command('migrate', database=nome_banco)
print(" Migrations finalizadas.")