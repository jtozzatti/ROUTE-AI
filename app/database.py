
import sqlite3
from pathlib import Path

# Caminho do banco de dados
DB_PATH = Path(__file__).resolve().parent.parent / "route_ai.db"


def conectar():
    return sqlite3.connect(DB_PATH)


def inicializar_banco():
    # Cria a tabela caso ela ainda não exista
    with conectar() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS ocorrencias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rodovia TEXT NOT NULL,
                km REAL NOT NULL,
                sentido TEXT NOT NULL,
                descricao TEXT NOT NULL,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


def salvar_ocorrencia(dados):
    # Salva somente os dados confirmados
    with conectar() as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO ocorrencias
            (rodovia, km, sentido, descricao)
            VALUES (?, ?, ?, ?)
            """,
            (
                dados.rodovia,
                dados.km,
                dados.sentido,
                dados.descricao
            )
        )

        return cursor.lastrowid

def listar_ocorrencias():
    # Abre conexão com o banco SQLite
    with conectar() as conexao:

        # Permite acessar as colunas pelos nomes
        conexao.row_factory = sqlite3.Row

        # Busca as ocorrências mais recentes primeiro
        cursor = conexao.execute("""
            SELECT
                id,
                rodovia,
                km,
                sentido,
                descricao,
                criado_em
            FROM ocorrencias
            ORDER BY id DESC
        """)

        # Converte os registros para dicionários
        return [dict(linha) for linha in cursor.fetchall()]
