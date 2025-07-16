import pymysql
import configparser
import os

# Lê o arquivo C:\cdigital\bd.ini
config = configparser.ConfigParser()
config.read('C:\\cdigital\\bd.ini')
nome_banco = config.get('database', 'nome', fallback=None)

if not nome_banco:
    print("Banco de dados não definido em C:\\cdigital\\bd.ini")
    exit()

# Configurações de conexão (ajuste conforme sua instalação)
usuario = 'Usuario_Root'
senha = 'Tr18365518AaBbCcDdEe#!'
host = 'localhost'
porta = 3308

# Conecta ao MySQL e cria o banco, se não existir
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