"""
Utilitários de tradução de texto usando Google Translate.
"""

import logging

from googletrans import Translator

logger = logging.getLogger(__name__)


async def translate_text(text: str, src: str = 'en', dest: str = 'pt') -> str:
    """
    Traduz texto de forma assíncrona.
    Retorna o texto original em caso de falha.
    """
    if not text or not text.strip():
        return text
    try:
        async with Translator() as translator:
            result = await translator.translate(text, src=src, dest=dest)
            return result.text
    except Exception as e:
        logger.error(f"Erro na tradução ({src} -> {dest}): {e}")
        return text
