"""
Utilitários para manipulação de arquivos e diretórios.
"""

import shutil
from pathlib import Path


def list_all_subfolders(directory: str) -> list[str]:
    """Lista todos os subdiretórios recursivamente."""
    root = Path(directory)
    return [str(p) for p in root.rglob('*') if p.is_dir() and p != root]


def list_all_files(directory: str) -> list[str]:
    """Lista todos os arquivos recursivamente."""
    return [str(p) for p in Path(directory).rglob('*') if p.is_file()]


def list_files_for_extension(directory: str, extension: str) -> list[str]:
    """Lista arquivos com uma extensão específica (ex: '.txt')."""
    return [str(p) for p in Path(directory).rglob(f'*{extension}') if p.is_file()]


def get_file_name(file_path: str) -> str:
    """Retorna o nome do arquivo sem a extensão."""
    return Path(file_path).stem


def write_lines(file_path: str, lines: list[str]):
    """Escreve linhas em um arquivo, criando pastas se necessário."""
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('\n'.join(lines))
    except Exception as e:
        print(f"Erro ao escrever em {file_path}: {e}")


def rename_file(file_name: str, new_file_name: str):
    """Renomeia um arquivo caso o destino não exista."""
    old_path, new_path = Path(file_name), Path(new_file_name)
    if not new_path.exists():
        try:
            old_path.rename(new_path)
        except Exception as e:
            print(f"Erro ao renomear: {e}")
    else:
        print(f"O destino {new_file_name} já existe.")


def delete_file(file_path: str):
    """Remove um arquivo se ele existir."""
    path = Path(file_path)
    if path.is_file():
        path.unlink()


def delete_folder(folder_path: str):
    """Remove uma pasta com conteúdo."""
    path = Path(folder_path)
    if path.is_dir():
        shutil.rmtree(path)


def exist_file(file_path: str) -> bool:
    """Verifica se o arquivo existe."""
    return Path(file_path).exists()


def create_folder(directory: str):
    """Cria um diretório (e pais) se não existir."""
    Path(directory).mkdir(parents=True, exist_ok=True)
