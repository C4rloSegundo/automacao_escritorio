from flask import Flask, render_template, request, jsonify
from utils.extractor import processar_pdfs
import logging
from flask import Flask, request, jsonify
import dropbox

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)

@app.route("/listar_pastas")
def listar_pastas():
    token = request.args.get("token")
    dbx = dropbox.Dropbox(token)
    pastas = set()

    for entry in dbx.files_list_folder("").entries:
        if isinstance(entry, dropbox.files.FolderMetadata):
            pastas.add(entry.name)

    return jsonify(sorted(pastas))

@app.route("/listar_arquivos")
def listar_arquivos():
    token = request.args.get("token")
    pasta = request.args.get("pasta")
    dbx = dropbox.Dropbox(token)
    arquivos = []

    for entry in dbx.files_list_folder("/" + pasta).entries:
        if isinstance(entry, dropbox.files.FileMetadata):
            arquivos.append(entry.name)

    return jsonify(sorted(arquivos))

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/processar", methods=["POST"])
def processar():
    token = request.form.get("token")
    if not token:
        return jsonify({"error": "Token não fornecido"}), 400
    
    try:
        resultados = processar_pdfs(token)
        return jsonify({"resultados": resultados})
    except Exception as e:
        logging.error(f"Erro no processamento: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)