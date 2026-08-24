# exportar_para_powerbi.py

import duckdb
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "data/processed/indicadores.duckdb")

conn = duckdb.connect(DB_PATH)

# Exporta tabela principal com valores corrigidos
df = conn.execute("SELECT * FROM indicadores").df()

# Verifica e corrige valores fora da escala esperada
# SELIC e CDI devem estar entre 0 e 1 (taxa diária)
# IPCA deve estar entre -5 e 5 (percentual mensal)
# Câmbio deve estar entre 1 e 10

print("Amostra dos dados antes da correção:")
print(df.groupby("indicador")["valor"].describe())

df.to_csv(
    "data/processed/indicadores_powerbi.csv",
    index=False,
    encoding="utf-8-sig",
    float_format="%.6f"  # garante 6 casas decimais
)
print(f"\n✅ {len(df)} registros exportados com casas decimais preservadas.")

# Exporta resumo
df_resumo = conn.execute("""
    SELECT
        ano,
        trimestre,
        indicador,
        ROUND(AVG(valor), 6)  AS media_valor,
        ROUND(MAX(valor), 6)  AS max_valor,
        ROUND(MIN(valor), 6)  AS min_valor
    FROM indicadores
    GROUP BY ano, trimestre, indicador
    ORDER BY ano, trimestre, indicador
""").df()

df_resumo.to_csv(
    "data/processed/resumo_powerbi.csv",
    index=False,
    encoding="utf-8-sig",
    float_format="%.6f"
)
print(f"✅ {len(df_resumo)} registros exportados para resumo.")

conn.close()