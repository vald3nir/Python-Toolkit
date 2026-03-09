"""
Operações de data e hora para manipulação de fuso horário e conversões.
"""

from datetime import datetime
from datetime import timezone

import pytz
from bson import ObjectId

# Configurações globais
LOCAL_TIME_ZONE = 'America/Sao_Paulo'
DATE_FORMAT_UTC = "%Y-%m-%dT%H:%M:%S.Z"
MONTH_LABELS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


def get_month_by_index(index: int) -> str:
    """Retorna a abreviação do mês pelo índice (1-12)."""
    if 1 <= index <= 12:
        return MONTH_LABELS[index - 1]
    raise IndexError("O índice do mês deve estar entre 1 e 12.")


def get_month_by_index_str(index: str) -> str:
    """Converte uma string de índice (ex: '01') na abreviação do mês."""
    return get_month_by_index(int(index))


def get_today_date_utc() -> str:
    """Retorna o timestamp UTC atual formatado como string."""
    return datetime.now(timezone.utc).strftime(DATE_FORMAT_UTC)


def timestamp_to_date_string(timestamp: float, time_zone: str = LOCAL_TIME_ZONE) -> str:
    """
    Converte timestamp Unix (ms) para string de data no fuso horário especificado.
    """
    # Converte milissegundos para segundos
    dt = datetime.fromtimestamp(timestamp / 1000, tz=pytz.timezone(time_zone))
    return str(dt)


def get_current_year() -> int:
    """Retorna o ano atual (local)."""
    return datetime.now().year


def object_id_to_date(object_id: ObjectId) -> str:
    """Extrai a data de criação de um ObjectId do MongoDB para formato UTC."""
    # O atributo generation_time já retorna um objeto datetime consciente de fuso horário
    return object_id.generation_time.astimezone(timezone.utc).strftime(DATE_FORMAT_UTC)
