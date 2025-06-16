# 📄 Extrator de Documentos PDF com OCR

Este projeto é uma aplicação web que permite o **processamento automatizado de arquivos PDF** armazenados no **Dropbox**, utilizando **OCR (Reconhecimento Óptico de Caracteres)** quando necessário. Os dados extraídos são exibidos de forma estruturada e interativa.

## 🚀 Funcionalidades

- Interface web amigável com Bootstrap
- Processamento em lote de arquivos PDF do Dropbox
- Extração de:
  - Nome completo
  - CPF e RG
  - Data de nascimento
  - Nome da mãe
  - Endereço e CEP
- Suporte a OCR com `pytesseract` para PDFs digitalizados
- Exportação de resultados em `.txt`
- Filtros interativos por erro e OCR

## 🧠 Tecnologias Utilizadas

- Python 3
- Flask
- Dropbox API
- pytesseract + pdf2image + PyMuPDF (fitz)
- Bootstrap 5 (frontend)
- HTML/CSS/JS puro

## 🖥️ Interface Web

A página principal (`index.html`) permite:

1. Inserir um token de acesso ao Dropbox
2. Processar documentos da pasta `/documentos_entrada`
3. Visualizar resultados com detalhes
4. Exportar dados extraídos

## 🔧 Requisitos

- Python 3.8+
- Tesseract OCR instalado no sistema
- Conta no Dropbox
- Token de acesso do Dropbox (com permissão de leitura)

### Instalação do Tesseract

Linux:
```bash
sudo apt install tesseract-ocr
```

Windows:
[Download do instalador](https://github.com/UB-Mannheim/tesseract/wiki)

## 🛠️ Instalação

1. Clone este repositório:

```bash
git clone https://github.com/C4rloSegundo/automacao_escritorio.git
cd seu-repo
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Crie um arquivo `.env` com seu token do Dropbox (opcional):

```
DROPBOX_TOKEN=seu_token_aqui
```

## ▶️ Como usar

Execute o app com:

```bash
python app.py
```

Acesse em: [http://localhost:5000](http://localhost:5000)

## 📂 Estrutura do Projeto

```
.
├── app.py              # Servidor Flask
├── extractor.py        # Lógica de processamento dos PDFs via Dropbox
├── pdf_utils.py        # Funções de OCR e extração de informações
├── templates/
│   └── index.html      # Interface web
├── .env                # (opcional) Token do Dropbox
└── requirements.txt    # Bibliotecas necessárias
```

## ✅ Exemplo de extração bem-sucedida

```json
{
  "nome": "documento.pdf",
  "texto": "Texto completo extraído...",
  "dados": {
    "nome_completo": "JOÃO SILVA",
    "cpf": "12345678900",
    "rg": "12345678",
    "data_nascimento": "01/01/1990",
    "nome_mae": "MARIA SILVA",
    "cep": "12345-678",
    "endereco": "RUA EXEMPLO, 123"
  },
  "tempo": "1.53s",
  "ocr_usado": "Sim",
  "status": "sucesso"
}
```

## 🧪 Testes

Para testar, adicione arquivos PDF na pasta `/documentos_entrada` do seu Dropbox, e insira seu token na interface.

## 📄 Licença

Este projeto está sob a licença MIT.

---

💡 Desenvolvido por Carlos Segundo(https://github.com/C4rloSegundo)