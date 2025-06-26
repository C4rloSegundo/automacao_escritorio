import fitz
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image
import io
import logging
import re
import dateutil.parser as dparser

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def detectar_idioma(texto):
    """Detecta idioma baseado em caracteres específicos"""
    if re.search(r'\b(do|da|dos|das|de|em|é|não|com|por|que)\b', texto, re.IGNORECASE):
        return 'por'
    return 'eng'

def extrair_informacoes(texto):
    """Extrai informações estruturadas do texto usando regex e heurísticas"""
    dados = {
        "cpf": None,
        "rg": None,
        "nome_completo": None,
        #"nome_mae": None,
        "data_nascimento": None,
        "cep": None,
        "endereco": None
    }
    
    # Expressões regulares melhoradas
    cpf_regex = r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b'
    rg_regex = r'\b\d{1,3}\.?\d{1,3}\.?\d{1,3}-?\d{0,2}[A-Za-z]?\b'
    cep_regex = r'\b\d{5}-?\d{3}\b'
    data_regex = r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b'
    
    # CPF
    cpf_match = re.search(cpf_regex, texto)
    if cpf_match:
        # dados["cpf"] = re.sub(r'[^\d]', '', cpf_match.group(0))
        cpf_limpo = re.sub(r'[^\d]', '', cpf_match.group(0))
        if len(cpf_limpo) == 11:
            dados["cpf"] = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
        else:
            dados["cpf"] = cpf_limpo

    
    # RG
    rg_match = re.search(rg_regex, texto)
    if rg_match:
        dados["rg"] = rg_match.group(0)
    
    # Nome completo (heurística: maior sequência de palavras em maiúsculas)
    # palavras = re.findall(r'\b[A-Z][A-Z\s]+\b', texto)
    # if palavras:
    #     # Seleciona a sequência mais longa que parece um nome
    #     palavras.sort(key=len, reverse=True)
    #     for candidato in palavras:
    #         partes = candidato.split()
    #         if len(partes) >= 2 and len(candidato) > 6:
    #             dados["nome_completo"] = candidato.strip()
    #             break
    
    # Nome completo (busca por linhas com múltiplas palavras com iniciais maiúsculas e sem palavras proibidas)
    linhas = texto.splitlines()
    stopwords_nome = {"DATA", "CERTIFICAMOS", "DECLARAMOS", "NASCIMENTO", "ESTADO", "DIRETORIA", "SECRETARIA", "FILIAÇÃO"}

    for linha in linhas:
        palavras = linha.strip().split()
        if len(palavras) >= 2 and all(p[0].isupper() for p in palavras if p.isalpha()):
            if not any(p.upper() in stopwords_nome for p in palavras):
                dados["nome_completo"] = linha.strip().title()
                break


    
    # Nome da mãe (procura por padrões específicos)
    # mae_match = re.search(r'(MÃE|MAE|FILIAÇÃO|Filiação|Mãe)[:\s]*(.*?)(?:\n|$)', texto, re.IGNORECASE)
    # if mae_match:
    #     dados["nome_mae"] = mae_match.group(2).strip()
    # Nome da mãe (com fallback para tentativa heurística)
    # Nome da mãe (buscando bloco de filiação com até 2 nomes)
    mae_encontrada = False
    match_fil = re.search(r'(FILIACAO|FILIAÇÃO|Filiação|Mãe)[:\s]*\n?(.*)', texto, re.IGNORECASE)
    if match_fil:
        linhas = texto.splitlines()
        idx = next((i for i, linha in enumerate(linhas) if "FILIACAO" in linha.upper() or "FILIAÇÃO" in linha.upper()), -1)
        if idx != -1 and idx + 2 < len(linhas):
            possivel_mae = linhas[idx + 2].strip()
            # Verifica se é diferente do nome completo e parece um nome válido
            if possivel_mae and len(possivel_mae.split()) >= 2:
                if dados.get("nome_completo") and possivel_mae not in dados["nome_completo"]:
                    dados["nome_mae"] = possivel_mae.title()
                    mae_encontrada = True

    # Fallback: busca tradicional por MÃE: XXXXX
    if not mae_encontrada:
        mae_match = re.search(r'(MÃE|MAE|Mãe)[:\s]*(?P<nome_mae>[A-ZÁÉÍÓÚÂÊÔÃÕÇ\s]{8,})', texto, re.IGNORECASE)
        if mae_match:
            nome_mae = mae_match.group("nome_mae").strip()
            if len(nome_mae.split()) >= 2:
                dados["nome_mae"] = nome_mae.title()



    
    # Data de nascimento com validação
    data_matches = re.findall(data_regex, texto)
    for match in data_matches:
        try:
            # Tenta interpretar a data
            data = dparser.parse(match, dayfirst=True)
            dados["data_nascimento"] = data.strftime('%d/%m/%Y')
            break
        except:
            continue
    
    # CEP
    cep_match = re.search(cep_regex, texto)
    if cep_match:
        dados["cep"] = cep_match.group(0)
    
    # Endereço (procura por padrões de endereço)
    endereco_match = re.search(r'(RUA|AVENIDA|AV|TRAVESSA|TRAV|RODOVIA)[\s\.,]*(.*?)(?:\n|CEP|$)', texto, re.IGNORECASE)
    if endereco_match:
        dados["endereco"] = endereco_match.group(0).strip()
    
    return dados

# def extrair_texto_pdf_com_ocr(pdf_bytes):
#     """Extrai texto de PDF, usando OCR apenas quando necessário"""
#     try:
#         doc = fitz.open(stream=pdf_bytes, filetype="pdf")
#         texto_total = ""
#         paginas_para_ocr = []
#         idioma = 'por'  # Idioma padrão
        
#         # Passo 1: Extrair texto nativo e identificar páginas para OCR
#         for i in range(len(doc)):
#             pagina = doc.load_page(i)
#             texto = pagina.get_text().strip()
#             if texto:
#                 texto_total += texto + "\n"
#                 if not idioma:
#                     idioma = detectar_idioma(texto)
#             else:
#                 paginas_para_ocr.append(i)
        
#         # Extrair informações mesmo se tiver texto nativo
#         dados_extraidos = extrair_informacoes(texto_total)
        
#         # Se todas páginas têm texto, retornar
#         if not paginas_para_ocr:
#             return {
#                 "texto_completo": texto_total.strip(),
#                 "dados": dados_extraidos
#             }
        
#         logging.info(f"Realizando OCR em {len(paginas_para_ocr)} página(s)")

#         # Passo 2: Processar páginas que precisam de OCR
#         for i in paginas_para_ocr:
#             pix = doc[i].get_pixmap(dpi=300)
#             img_bytes = pix.tobytes("ppm")
#             img = Image.open(io.BytesIO(img_bytes))
            
#             # Usar idioma detectado ou padrão
#             lang = idioma if idioma else 'por'
#             texto_ocr = pytesseract.image_to_string(img, lang=lang)
#             texto_total += texto_ocr + "\n"
        
#         # Re-extrair informações com texto completo
#         dados_extraidos = extrair_informacoes(texto_total)
#         return {
#             "texto_completo": texto_total.strip(),
#             "dados": dados_extraidos
#         }
    
#     except Exception as e:
#         logging.error(f"Erro na extração de texto: {e}")
#         return {
#             "texto_completo": f"Erro na extração: {str(e)}",
#             "dados": {}
#         }

def extrair_texto_pdf_com_ocr(pdf_bytes):
    """Extrai texto de PDF, aplicando OCR em DPI 200 e 300 e combinando os resultados"""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        texto_200 = ""
        texto_300 = ""
        idioma = 'por'
        paginas_para_ocr = []

        for i in range(len(doc)):
            pagina = doc.load_page(i)
            texto = pagina.get_text().strip()
            if texto:
                texto_200 += texto + "\n"
                texto_300 += texto + "\n"
            else:
                paginas_para_ocr.append(i)

        if paginas_para_ocr:
            logging.info(f"Realizando OCR em {len(paginas_para_ocr)} página(s) com DPI 200 e 300")

            for i in paginas_para_ocr:
                pix_200 = doc[i].get_pixmap(dpi=200)
                img_200 = Image.open(io.BytesIO(pix_200.tobytes("ppm")))
                texto_200 += pytesseract.image_to_string(img_200, lang=idioma) + "\n"

                pix_300 = doc[i].get_pixmap(dpi=300)
                img_300 = Image.open(io.BytesIO(pix_300.tobytes("ppm")))
                texto_300 += pytesseract.image_to_string(img_300, lang=idioma) + "\n"

        # Extrair de ambos
        dados_200 = extrair_informacoes(texto_200)
        dados_300 = extrair_informacoes(texto_300)

        # Mesclar: priorizar o campo mais confiável de cada OCR
        dados_finais = {}
        dados_finais["nome_completo"] = dados_300.get("nome_completo") or dados_200.get("nome_completo")
        dados_finais["data_nascimento"] = dados_200.get("data_nascimento") or dados_300.get("data_nascimento")
        dados_finais["cpf"] = dados_200.get("cpf") or dados_300.get("cpf")
        dados_finais["rg"] = dados_200.get("rg") or dados_300.get("rg")
        dados_finais["nome_mae"] = None

        # Validar se nome da mãe é diferente do nome completo (e não contém o próprio nome dentro)
        for nome in [dados_200.get("nome_mae"), dados_300.get("nome_mae")]:
            if nome and dados_finais["nome_completo"] and nome != dados_finais["nome_completo"] and not nome in dados_finais["nome_completo"]:
                dados_finais["nome_mae"] = nome
                break

        texto_final = texto_200 + "\n" + texto_300

        return {
            "texto_completo": texto_final.strip(),
            "dados": dados_finais
        }

    except Exception as e:
        logging.error(f"Erro na extração de texto: {e}")
        return {
            "texto_completo": f"Erro na extração: {str(e)}",
            "dados": {}
        }
