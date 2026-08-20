import pandas as pd
import os

def carregar_raw(caminho: str) -> pd.DataFrame:
    """
    Carrega o arquivo CSV bruto gerado pela extração.
    """

    print(f"\n Carregando dados brutos de: {caminho}")
    df = pd.read_csv(caminho, parse_dates=["data"])
    print(f"  {len(df)} registros carregados.")
    return df

def limpar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove registros com valores mulos ou inválidos
    """

    total_antes = len(df)
    df = df.dropna(subset=["valor"])
    df = df[df["valor"].notnull()]
    total_depois = len(df)

    removidos = total_antes - total_depois

    if removidos > 0:
        print(f"  {removidos} registros removidos por valores nulos.")

    else:
        print(f"  Nenhum valor nulo encontrado")

    return df.reset_index(drop=True)

def enriquecer_dados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona colunas de contexto temporal e métricas calculadas.
    """

    # Colunas temporais
    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.month
    df["trimestre"] = df["data"].dt.quarter
    df["nome_mes"] = df["data"].dt.strftime("%b/%Y")

    # Média móvel de 30 dias por indicador
    df = df.sort_values(["indicador", "data"])
    df["media_movel_30d"] = (
        df.groupby("indicador")["valor"]
        .transform(lambda x: x.rolling(window=30, min_periods=1).mean())
    )

    # Variação percentual diária por indicador

    df["variacao_pct"] = (
        df.groupby("indicador")["valor"] 
        .transform(lambda x: x.pct_change() * 100)
    )

    # Classificação do nível da SELIC
    def classificar_selic(row):
        if row["valor"] != "selic":
            return None
        if row["valor"] < 0.03:
            return "Baixo"
        elif row["valor"] < 0.05:
            return "Médio"
        else:
            return "Alto"

    df["nivel_selic"] = df.apply(classificar_selic, axis=1)

    print("   Colunas adicionadas: ano, mes, trimestre, nome_mes")
    print("   média_movel_30d, variacao_pct, nivel_selic")

    return df

def salvar_processed(df: pd.DataFrame) -> str:
    """
    Salva os dados transformados em CSV na pasta data/processed.
    """
    os.makedirs("data/processed", exist_ok=True)

    from datetime import datetime
    hoje = datetime.today().strftime("%Y%m%d")
    caminho = f"data/processed/indicadores_processed_{hoje}.CSV"

    df.to_csv(caminho, index=False, encoding="utf-8")
    print(f"\n Dados transformados salvos em {caminho}")

    return caminho

def transformar(caminho_raw: str) -> pd.DataFrame:
    """
    Executa o pipeline completo de transformação.
    """

    print("\n Iniciando transformação dos dados...")

    df = carregar_raw(caminho_raw)
    df = limpar_dados(df)
    df = enriquecer_dados(df)

    print(f"\n Transformação concluída: {len(df)}: registros processados.")
    print(f"   Colunas: {list(df.columns)}")

    return df

