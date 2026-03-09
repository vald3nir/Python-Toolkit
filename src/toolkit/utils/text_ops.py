"""
Utilitários para processamento e formatação de texto.
"""

import re


def sanitize_string(text: str) -> str:
    """
    Substitui qualquer caractere não alfanumérico por um underscore (_).
    Útil para gerar nomes de arquivos ou identificadores seguros.
    """
    return re.sub(r'[^a-zA-Z0-9]', '_', text)


def capitalize_text(text: str) -> str:
    """
    Capitaliza a primeira letra de cada palavra no texto.
    """
    # .title() é a forma Pythônica de capitalizar cada palavra
    return text.title()
