import mysql.connector
from datetime import date
from dotenv import load_dotenv
import os

# ===================== CONEXÃO COM O BANCO =====================
caminho_env = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=caminho_env)

db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_senha = os.getenv("DB_SENHA")
db_nome = os.getenv("DB_NOME")

conexao = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_senha,
    database=db_nome
)
cursor = conexao.cursor()


# ===================== FUNÇÕES DE LIVROS =====================
def adicionar_livro(titulo, editora, num_pag, genero, status, nota, autor):
    data = date.today()
    autores_ex = listar_autores()
    autores = [item[1].lower() for item in autores_ex]
    if autor.lower() in autores:
        cursor.execute("SELECT id from autores where LOWER(nome() = LOWER(%s)", (autor,))
        autorid = cursor.fetchone()[0]
    else:
        cursor.execute("INSERT INTO autores (nome,data_cad) VALUES (%s, %s)",(autor,data))
        autorid = cursor.lastrowid
    cursor.execute("INSERT INTO livros (titulo, editora, numero_pag, nota, genero, data_cad, status, autor_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",(titulo, editora, num_pag, nota, genero, data, status,autorid))
    conexao.commit()


def remover_livro(id_livro):
    cursor.execute("DELETE FROM livros WHERE id=%s", (id_livro,))
    conexao.commit()


def listar_livros():
    cursor.execute("SELECT * FROM livros")
    return cursor.fetchall()


def listar_autores():
    cursor.execute("SELECT * FROM autores")
    return cursor.fetchall()

def lista_desejos():
    cursor.execute("SELECT * FROM Desejos")
    return cursor.fetchall()


def atualizar_livro(id_livro, status, nota):
    cursor.execute("UPDATE livros SET status = %s, nota = %s WHERE id = %s",(status, nota, id_livro))
    conexao.commit()


# ===================== ENCERRAMENTO =====================
def fechar_conexao():
    cursor.close()
    conexao.close()
