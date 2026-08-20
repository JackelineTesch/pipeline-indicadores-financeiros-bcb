import duckdb
import pandas as pd 
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "data/processed/indicadores.duckdb")

def conectar() -> duckdb.DuckDBPyConnection:
    """
    Cria ou conecta ao banco DuckDB.
    """

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = duckdb.connect(DB_PATH)
    print(f" Conectado ao banco: {DB_PATH}")
    return conn

def criar_tabela(conn: duckdb.DuckDBPyConnection):
    """
    Cria a tabela principal se não existir.
    """

    conn.execute("""
    CREATE TABLE IF NOT EXISTS indicadores (
            data            DATE,
            valor           DOUBLE,
            indicador       VARCHAR,
            ano             INTEGER,
            mes             INTEGER,
            trimestre       INTEGER,
            nome_mes        VARCHAR,
            media_movel_30d DOUBLE,
            variacao_pct    DOUBLE,
            nivel_selic     VARCHAR
        )
    """)
    print(" Tabela 'indicadores' verificada/criada.")

def carregar_dados(conn: duckdb.DuckDBPyConnection, df: pd.DataFrame):
    """
    Carrega o DataFrame no banco, evitando duplicatas por data e indicador.
    """

    # Verifica se já existem dados no banco
    total_existentes = conn.execute("SELECT COUNT(*) FROM indicadores").fetchone()[0]

    if total_existentes > 0:
        print(f"  Banco já contém {total_existentes} registros.")
        print("   Removendo registros existentes para recarga limpa...")
        conn.execute("DELETE FROM indicadores")

    # Insere os novos dados
    conn.execute("INSERT INTO indicadores SELECT * FROM df")

    total_inserido = conn.execute("SELECT COUNT(*) FROM indicadores").fetchone()[0]
    print(f"{total_inserido} registros carregados no banco.")


def validar_carga(conn: duckdb.DuckDBPyConnection):
    """
    Executa queries de validação para garantir que a carga foi bem-sucedida.
    """
    print("\nValidação da carga:")

    # Total por indicador
    resultado = conn.execute("""
        SELECT 
            indicador,
            COUNT(*) as total_registros,
            MIN(data) as data_inicio,
            MAX(data) as data_fim,
            ROUND(AVG(valor), 4) as media_valor
        FROM indicadores
        GROUP BY indicador
        ORDER BY indicador
    """).df()

    print(resultado.to_string(index=False))


def carregar(df: pd.DataFrame):
    """
    Executa o pipeline completo de carga.
    """
    print("\nIniciando carga no banco de dados...")

    conn = conectar()
    criar_tabela(conn)
    carregar_dados(conn, df)
    validar_carga(conn)
    conn.close()

    print("\nCarga concluída e conexão encerrada.")


    
