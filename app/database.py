
import sqlite3
from pathlib import Path

# Caminho do banco de dados
DB_PATH = Path(__file__).resolve().parent.parent / "route_ai.db"


def conectar():
    return sqlite3.connect(DB_PATH)


def criar_tabela(conexao):
    # Campos km e sentido são opcionais
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS ocorrencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rodovia TEXT NOT NULL,
            km REAL,
            sentido TEXT,
            descricao TEXT NOT NULL,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)


def inicializar_banco():
    with conectar() as conexao:
        # Cria a tabela se ainda não existir
        criar_tabela(conexao)

        # Verifica a estrutura atual do banco
        colunas = conexao.execute(
            "PRAGMA table_info(ocorrencias)"
        ).fetchall()

        # Identifica colunas antigas que exigem valores
        precisa_migrar = any(
            coluna[1] in ("km", "sentido") and coluna[3] == 1
            for coluna in colunas
        )

        if not precisa_migrar:
            return

        print("Atualizando estrutura do banco de dados...")

        # Migração executada em uma transação
        # Os registros existentes são preservados
        conexao.execute("""
            CREATE TABLE ocorrencias_nova (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rodovia TEXT NOT NULL,
                km REAL,
                sentido TEXT,
                descricao TEXT NOT NULL,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Copia os registros antigos para a nova tabela
        conexao.execute("""
            INSERT INTO ocorrencias_nova
                (id, rodovia, km, sentido, descricao, criado_em)
            SELECT
                id, rodovia, km, sentido, descricao, criado_em
            FROM ocorrencias
        """)

        # Substitui a tabela antiga
        conexao.execute("DROP TABLE ocorrencias")

        conexao.execute("""
            ALTER TABLE ocorrencias_nova
            RENAME TO ocorrencias
        """)

        print("Banco atualizado com sucesso!")


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
