import dropbox
import os
from pdf_utils import extrair_texto_pdf_com_ocr
import logging
import time
from dotenv import load_dotenv
from functools import lru_cache

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@lru_cache(maxsize=32)
def processar_arquivo(dbx, caminho_arquivo):
    """Processa um arquivo PDF com cache de resultados"""
    try:
        logging.info(f"Processando: {caminho_arquivo.split('/')[-1]}")
        _, resposta = dbx.files_download(caminho_arquivo)
        inicio = time.time()
        resultado_extracao = extrair_texto_pdf_com_ocr(resposta.content)
        tempo = time.time() - inicio
        
        return {
            "nome": caminho_arquivo.split("/")[-1],
            "texto": resultado_extracao['texto_completo'],
            "dados": resultado_extracao['dados'],
            "tempo": f"{tempo:.2f}s",
            "ocr_usado": "Sim" if "OCR aplicado" not in resultado_extracao['texto_completo'] else "Não",
            "status": "sucesso"
        }
    except Exception as e:
        logging.error(f"Erro no processamento: {str(e)}")
        return {
            "nome": caminho_arquivo.split("/")[-1],
            "erro": str(e),
            "dados": {},
            "status": "erro"
        }

def processar_pdfs(token=None, caminho_pasta="/documentos_entrada"):
    """Processa todos os PDFs em uma pasta do Dropbox"""
    if token is None:
        token = os.getenv("DROPBOX_TOKEN")
    
    if not token:
        raise ValueError("Token do Dropbox não fornecido")
    
    try:
        dbx = dropbox.Dropbox(token)
        resposta = dbx.files_list_folder(caminho_pasta)
    except Exception as e:
        logging.error(f"Erro ao acessar Dropbox: {e}")
        return [{"erro": f"Erro ao acessar Dropbox: {e}", "status": "erro"}]
    
    resultados = []
    
    for arquivo in resposta.entries:
        if isinstance(arquivo, dropbox.files.FileMetadata) and arquivo.name.lower().endswith(".pdf"):
            resultado = processar_arquivo(dbx, arquivo.path_lower)
            resultados.append(resultado)
    
    return resultados