from datetime import datetime
from glob import glob

from src.extract import extrair_todos, salvar_raw
from src.transform import transformar, salvar_processed
from src.load import carregar

def executar_pipeline():
    inicio = datetime.now()
    print("=" * 55)
    print(" PIPELINE - INDICADORES FINANCEIROS BACEN")
    print(f" Início: {inicio.strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 55)

    # Etapa 1 - Extração
    df_raw = extrair_todos()
    caminho_raw = salvar_raw(df_raw)

    # Etapa 2 - Transformação
    df_processed = transformar(caminho_raw)
    salvar_processed(df_processed)

    # Etapa 3 - Carga
    carregar(df_processed)

    # ETAPA 4 — Exportar CSVs
    import os
    os.makedirs("data/processed", exist_ok=True)

    # CSV para o Streamlit Cloud
    caminho_streamlit = "data/processed/indicadores_atual.csv"
    df_processed.to_csv(caminho_streamlit, index=False, encoding="utf-8")
    print(f"\n💾 CSV Streamlit exportado: {caminho_streamlit}")

    # CSV para o Power BI
    caminho_powerbi = "data/processed/indicadores_powerbi.csv"
    df_processed.to_csv(caminho_powerbi, index=False, encoding="utf-8-sig",
                        float_format="%.6f")
    print(f"💾 CSV Power BI exportado: {caminho_powerbi}")

    fim = datetime.now()
    duracao = (fim - inicio).seconds

    print("\n" + "=" * 55)
    print("   ✅ PIPELINE CONCLUÍDO COM SUCESSO")
    print(f"   Fim: {fim.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"   Duração: {duracao} segundos")
    print("=" * 55)

if __name__ == "__main__":
    executar_pipeline()

    