"""
DataFrame utilities for pandas DataFrame operations.

This module provides functions for loading, manipulating, and converting pandas DataFrames.
"""

import pandas as pd
from tabulate import tabulate

LOCAL_TIME_ZONE = 'America/Sao_Paulo'
DATE_FORMAT_UTC = "%Y-%m-%dT%H:%M:%S.Z"


def load_dataframe(file_csv: str) -> pd.DataFrame:
    """Carrega um arquivo CSV para um DataFrame pandas."""
    return pd.read_csv(file_csv)


def count_lines(file_csv: str) -> int:
    """Retorna o número total de linhas de um CSV."""
    # Usar len(df) é simples e direto após o carregamento
    return len(load_dataframe(file_csv))


def dataframe_to_json(df: pd.DataFrame) -> list[dict]:
    """Converte um DataFrame para uma lista de dicionários (formato JSON)."""
    # orient='records' já retorna a estrutura de lista de dicts se não especificar arquivo
    return df.to_dict(orient="records")


def file_csv_to_json(file_csv: str) -> list[dict]:
    """Lê um CSV e o converte diretamente para uma lista de dicionários."""
    df = load_dataframe(file_csv)
    return df.to_dict(orient='records')


def json_to_file_csv(file_csv: str, data_json: list[dict]):
    """Converte dados em formato JSON (lista de dicts) para um arquivo CSV."""
    pd.DataFrame(data_json).to_csv(file_csv, index=False)


def split_data_frame_by_value(file_csv: str, column: str, value):
    """Divide o DataFrame em dois com base em um valor de corte (threshold)."""
    df = load_dataframe(file_csv)
    # Filtros booleanos diretos do pandas
    low_values = df[df[column] < value]
    high_values = df[df[column] >= value]
    return low_values, high_values


def normalize_column_value(file_csv: str, column: str, value):
    """Limita valores de uma coluna que excedem um limite (threshold)."""
    df = load_dataframe(file_csv)
    # .loc é a forma recomendada para modificar valores no pandas
    df.loc[df[column] >= value, column] = value
    df.to_csv(file_csv, index=False)


def format_time_zone(series: pd.Series) -> pd.Series:
    """Converte uma série de datas para o fuso horário local e formata como string."""
    return (series.dt.tz_convert(LOCAL_TIME_ZONE)
            .dt.strftime(DATE_FORMAT_UTC)
            .astype(str))


def print_dataframe(df: pd.DataFrame, max_rows: int = 10):
    """Exibe o DataFrame de forma estilizada no console."""
    if df.empty:
        print("DataFrame vazio.")
        return

    # Exibe apenas as primeiras 'n' linhas em formato de grade
    print(tabulate(df.head(max_rows), headers='keys', tablefmt='fancy_grid', showindex=False))

    if len(df) > max_rows:
        print(f"\n... ({len(df) - max_rows} linhas omitidas)")
