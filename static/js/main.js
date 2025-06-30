// === main.js ===

// Carrega as pastas do Dropbox após inserção do token
document.getElementById('token').addEventListener('change', async () => {
    const token = document.getElementById('token').value;
    const pastaSelect = document.getElementById('select-pasta');

    if (!token) return;

    pastaSelect.disabled = true;
    pastaSelect.innerHTML = '<option>Carregando pastas...</option>';

    try {
        const response = await fetch(`/listar_pastas?token=${encodeURIComponent(token)}`);
        const pastas = await response.json();

        pastaSelect.innerHTML = '';
        pastas.forEach(pasta => {
            const opt = document.createElement('option');
            opt.value = pasta;
            opt.textContent = pasta;
            pastaSelect.appendChild(opt);
        });

        pastaSelect.disabled = false;
    } catch (err) {
        alert('Erro ao listar pastas: ' + err.message);
    }
});

// Carrega os arquivos da pasta selecionada
document.getElementById('select-pasta').addEventListener('change', async () => {
    const token = document.getElementById('token').value;
    const pasta = document.getElementById('select-pasta').value;
    const arquivoSelect = document.getElementById('select-arquivo');

    arquivoSelect.disabled = true;
    arquivoSelect.innerHTML = '<option>Carregando arquivos...</option>';

    try {
        const response = await fetch(`/listar_arquivos?token=${encodeURIComponent(token)}&pasta=${encodeURIComponent(pasta)}`);
        const arquivos = await response.json();

        arquivoSelect.innerHTML = '';
        arquivos.forEach(arquivo => {
            const opt = document.createElement('option');
            opt.value = arquivo;
            opt.textContent = arquivo;
            arquivoSelect.appendChild(opt);
        });

        arquivoSelect.disabled = false;
    } catch (err) {
        alert('Erro ao listar arquivos: ' + err.message);
    }
});

// Processa o documento selecionado
document.getElementById('btn-processar').addEventListener('click', async () => {
    const token = document.getElementById('token').value;
    const pasta = document.getElementById('select-pasta').value;
    const arquivo = document.getElementById('select-arquivo').value;

    if (!token || !pasta || !arquivo) {
        alert('Preencha todas as informações');
        return;
    }

    const btn = document.getElementById('btn-processar');
    const spinner = document.getElementById('spinner');
    const btnText = document.getElementById('btn-text');
    btn.disabled = true;
    spinner.classList.remove('d-none');
    btnText.textContent = ' Processando...';

    const resultContainer = document.getElementById('result-container');
    resultContainer.classList.remove('d-none');
    document.getElementById('results').innerHTML = '';

    try {
        const response = await fetch('/processar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token, pasta, arquivo })
        });

        const data = await response.json();

        if (data.error) throw new Error(data.error);
        exibirResultados(data.resultados);
        document.getElementById('btn-exportar').classList.remove('d-none');
    } catch (error) {
        alert('Erro ao processar: ' + error.message);
    } finally {
        btn.disabled = false;
        spinner.classList.add('d-none');
        btnText.textContent = 'Processar Documentos';
    }
});

// Exibe os resultados extraídos no HTML
function exibirResultados(resultados) {
    const container = document.getElementById('results');
    container.innerHTML = '';

    resultados.forEach((resultado, index) => {
        const item = document.createElement('div');
        item.className = 'accordion-item';

        const header = `
            <h2 class="accordion-header" id="heading-${index}">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-${index}" aria-expanded="false">
                    <i class="bi bi-file-earmark-pdf me-2"></i> ${resultado.nome}
                </button>
            </h2>`;

        const campos = [
            { chave: 'nome_completo', rotulo: 'Nome Completo', icone: 'person-badge' },
            { chave: 'cpf', rotulo: 'CPF', icone: 'credit-card' },
            { chave: 'rg', rotulo: 'RG', icone: 'card-text' },
            { chave: 'data_nascimento', rotulo: 'Data de Nascimento', icone: 'calendar' },
            { chave: 'endereco', rotulo: 'Endereço', icone: 'geo-alt' },
            { chave: 'cep', rotulo: 'CEP', icone: 'postcard' }
        ];

        let camposHTML = '';
        campos.forEach(campo => {
            if (resultado.dados[campo.chave]) {
                camposHTML += `
                    <div class="col-md-6 mb-3">
                        <div class="info-item">
                            <label class="form-label"><i class="bi bi-${campo.icone} text-primary"></i> ${campo.rotulo}</label>
                            <input type="text" class="form-control campo-editavel" id="${campo.chave}-${index}" value="${resultado.dados[campo.chave]}" readonly />
                        </div>
                    </div>`;
            }
        });

        const body = `
            <div id="collapse-${index}" class="accordion-collapse collapse" data-bs-parent="#results">
                <div class="accordion-body">
                    <div class="form-check form-switch mb-3">
                        <input class="form-check-input editar-switch" type="checkbox" id="editar-${index}">
                        <label class="form-check-label" for="editar-${index}">Permitir edição dos campos</label>
                    </div>
                    <div class="row">${camposHTML}</div>
                </div>
            </div>`;

        item.innerHTML = header + body;
        container.appendChild(item);
    });

    document.querySelectorAll('.editar-switch').forEach((checkbox, idx) => {
        checkbox.addEventListener('change', () => {
            const inputs = document.querySelectorAll(`#collapse-${idx} .campo-editavel`);
            inputs.forEach(input => input.readOnly = !checkbox.checked);
        });
    });
}

// Gera a procuração em PDF

document.getElementById('btn-exportar').addEventListener('click', () => {
    const { jsPDF } = window.jspdf;

    document.querySelectorAll('.accordion-item').forEach((item, idx) => {
        const doc = new jsPDF();
        const nome = document.getElementById(`nome_completo-${idx}`)?.value || 'NOME';
        const cpf = document.getElementById(`cpf-${idx}`)?.value || 'CPF';
        const rg = document.getElementById(`rg-${idx}`)?.value || 'RG';
        const dataNascimento = document.getElementById(`data_nascimento-${idx}`)?.value || 'DATA';
        const endereco = document.getElementById(`endereco-${idx}`)?.value || 'ENDEREÇO';

        const hoje = new Date().toLocaleDateString('pt-BR');

        const texto = `
PROCURAÇÃO

Eu, ${nome}, inscrito(a) no CPF sob o nº ${cpf}, portador(a) do RG nº ${rg},
nascido(a) em ${dataNascimento}, residente à ${endereco}, nomeio e constituo como
meu bastante procurador o(a) Sr(a) _________________________________________,
com poderes para me representar perante órgãos públicos, privados, cartórios,
e onde mais se fizer necessário.

Feira de Santana - BA, ${hoje}.
        `;

        doc.setFont("Times", "normal");
        doc.setFontSize(12);
        const linhas = doc.splitTextToSize(texto.trim(), 180);
        doc.text(linhas, 15, 20);

        const pdfBlob = doc.output("blob");
        const url = URL.createObjectURL(pdfBlob);
        window.open(url, '_blank');
    });
});
