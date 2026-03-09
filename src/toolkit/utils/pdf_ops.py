"""
Utilitários para processamento de documentos PDF.
"""

import logging

import pdfplumber

logger = logging.getLogger(__name__)


def load_text_from_pdf(pdf_path: str) -> str:
    """
    Extrai todo o texto de um arquivo PDF de forma eficiente.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            logger.info(f"Processando PDF: {pdf_path} ({len(pdf.pages)} páginas)")

            # Extrai o texto de cada página e filtra as vazias
            pages_text = []
            for i, page in enumerate(pdf.pages, 1):
                content = page.extract_text()
                if content:
                    pages_text.append(content)
                logger.debug(f"Página {i} extraída.")

            full_text = "\n".join(pages_text)
            logger.info(f"Extração concluída: {len(full_text)} caracteres obtidos.")
            return full_text

    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {pdf_path}")
        raise
    except Exception as e:
        logger.error(f"Falha ao processar o PDF {pdf_path}: {e}")
        raise
