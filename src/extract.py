import requests
import pandas as pd
from datetime import datetime
import os

# Dicionário com os indicadores que serão extraídos
# Chave = nome amigável, Valor = código da série no BACEN

INDICADORES = {
    "selic": 11,
    "ipca": 433,
    "cdi": 12,
    "cambio_dolar": 1
}

# Período de extração: Últimos 5 anos

DATA_INICIO = "01/01/2020"
DATA_FIM = datetime.today().strftime("%d/%m/%Y")  #hoje

def extrair_serie(nome: str, codigo: int) -> pd.DataFrame:
    """
    Chama a API do BACEN e retorna um DataFrame com os ados da série.

    Args:
        nome (str): nome do indicador (ex: 'selic')
        codigo (int): código da série no BACEN

    Returns:
        DataFrame com colunas: data, valor, indicador
    """

    url = (
        f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
        f"?formato=json&dataInicial={DATA_INICIO}&dataFinal={DATA_FIM}"
    )

    print(f"Extraindo {nome} (código {codigo})...")

    response = requests.get(url, timeout=30)

    # Verifica se a requisição foi bem-sucedida

    if response.status_code !=200:
        print(f"ERRO ao extrair {nome}: status {response.status_code}")
        return pd.DataFrame()

    dados = response.json()

    # Converte para DataFrame

    df = pd.DataFrame(dados)

    # Renomeia colunas para o padrão do projeto

    df.columns = ["data", "valor"]

    # Converte tipos de dados 

    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    # Adiciona coluna identificando o indicador

    df["indicador"] = nome

    return df

def extrair_todos() -> pd.DataFrame:
    """
    Extrai todos os indicadores e retorna um DataFrame consolidado.
    
    """
    print("\n Iniciando extração dos indicadores do BACEN...")

    frames = []

    for nome, codigo in INDICADORES.items():
        df = extrair_serie(nome, codigo)
        if not df.empty:
            frames.append(df)

    # Consolida todos em um único DataFrame

    df_consolidado = pd.concat(frames, ignore_index=True)

    print(f"Extração concluída: {len(df_consolidado)} registros extraídos.")

    return df_consolidado

def salvar_raw(df: pd.DataFrame) -> str:
    """
    Salva os dados brutos em CSV na pasta data/raw.
    O nome do arquivo inclui a data de hoje para manter histórico.
    """

    os.makedirs("data/raw", exist_ok=True)

    hoje = datetime.today().strftime("%Y%m%d")
    caminho = f"data/raw/indicadores_raw_{hoje}.csv"

    df.to_csv(caminho, index=False, encoding="utf-8")

    print(f"Dados brutos salvos em: {caminho}")

    return caminho


    