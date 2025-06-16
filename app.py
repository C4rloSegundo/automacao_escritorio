from flask import Flask, render_template, request, jsonify
from extractor import processar_pdfs
import logging

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)

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