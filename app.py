from flask import Flask, render_template, request, jsonify
from utils.extractor import extrair_texto_pdf_com_ocr
import logging
import dropbox

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/listar_pastas")
def listar_pastas():
    token = request.args.get("token")
    if not token:
        return jsonify({"error": "Token não fornecido"}), 400

    try:
        dbx = dropbox.Dropbox(token)
        entradas = dbx.files_list_folder("").entries
        pastas = sorted(entry.name for entry in entradas if isinstance(entry, dropbox.files.FolderMetadata))
        return jsonify(pastas)
    except Exception as e:
        logging.error(f"Erro ao listar pastas: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/listar_arquivos")
def listar_arquivos():
    token = request.args.get("token")
    pasta = request.args.get("pasta")
    if not token or not pasta:
        return jsonify({"error": "Token e pasta são obrigatórios"}), 400

    try:
        dbx = dropbox.Dropbox(token)
        entradas = dbx.files_list_folder(f"/{pasta}").entries
        arquivos = sorted(entry.name for entry in entradas if isinstance(entry, dropbox.files.FileMetadata))
        return jsonify(arquivos)
    except Exception as e:
        logging.error(f"Erro ao listar arquivos: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/processar", methods=["POST"])
def processar():
    data = request.get_json()

    token = data.get("token")
    pasta = data.get("pasta")
    arquivo = data.get("arquivo")

    if not token or not pasta or not arquivo:
        return jsonify({"error": "Token, pasta e arquivo são obrigatórios"}), 400

    try:
        dbx = dropbox.Dropbox(token)
        caminho_completo = f"/{pasta}/{arquivo}"
        metadata, res = dbx.files_download(caminho_completo)
        pdf_bytes = res.content

        resultado = extrair_texto_pdf_com_ocr(pdf_bytes)
        return jsonify({
            "resultados": [{
                "nome": arquivo,
                "dados": resultado["dados"]
            }]
        })

    except Exception as e:
        logging.error(f"Erro no processamento: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
