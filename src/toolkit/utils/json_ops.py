"""
Utilitários para manipulação de dados JSON e conversão de objetos.
"""

import json
from pathlib import Path
from typing import Any
from typing import Type
from typing import TypeVar

T = TypeVar('T')


def dict_size(d: dict) -> int:
    """Calcula a soma do tamanho de todos os valores no dicionário."""
    return sum(len(v) for v in d.values() if hasattr(v, '__len__'))


def format_json(data: dict) -> dict:
    """Garante a estrutura JSON válida convertendo tipos complexos (como datas) em strings."""
    return json.loads(json.dumps(data, default=str))


def convert_json_to_object(data: dict, class_name: Type[T]) -> T:
    """Converte um dicionário JSON em uma instância de classe Python."""
    # O format_json garante que tipos incompatíveis com JSON sejam tratados antes do unpack (**)
    return class_name(**format_json(data))


def convert_array_json_to_objects(data: list[dict], class_name: Type[T]) -> list[T]:
    """Converte uma lista de dicionários em uma lista de objetos Python."""
    return [convert_json_to_object(item, class_name) for item in data]


def read_json(file_path: str) -> Any:
    """Lê um arquivo JSON e retorna seu conteúdo."""
    with open(file_path, 'r', encoding="utf8") as f:
        return json.load(f)


def write_json(file_path: str, data: Any):
    """Escreve dados em um arquivo JSON com formatação amigável (indent=4)."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
