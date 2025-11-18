// Elementos do DOM
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const selectFileBtn = document.getElementById('selectFileBtn');
const filesList = document.getElementById('filesList');
const filesContainer = document.getElementById('filesContainer');
const fileCount = document.getElementById('fileCount');
const clearAllBtn = document.getElementById('clearAllBtn');
const formatSelect = document.getElementById('formatSelect');
const qualitySelect = document.getElementById('qualitySelect');
const convertBtn = document.getElementById('convertBtn');
const convertCount = document.getElementById('convertCount');
const formatDisplay = document.getElementById('formatDisplay');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const result = document.getElementById('result');
const resultMessage = document.getElementById('resultMessage');
const downloadLinks = document.getElementById('downloadLinks');
const downloadAllBtn = document.getElementById('downloadAllBtn');
const error = document.getElementById('error');
const errorMessage = document.getElementById('errorMessage');

const MAX_FILES = 15;
let selectedFiles = [];

// Formatos de áudio suportados
const FORMATOS_AUDIO = ['mp3', 'wav', 'flac', 'ogg', 'aac', 'm4a', 'mp4', 'wma', 'aiff', 'aif', 
                        'opus', 'amr', '3gp', 'ac3', 'eac3', 'dts', 'mp2', 'mpa', 'ra', 'rm',
                        'au', 'snd', 'voc', 'wv', 'ape', 'tta', 'tak', 'webm'];

// Atualiza o formato exibido no botão quando o formato de saída muda
formatSelect.addEventListener('change', () => {
    formatDisplay.textContent = formatSelect.value.toUpperCase();
});

// Event Listeners
selectFileBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
clearAllBtn.addEventListener('click', clearAllFiles);
convertBtn.addEventListener('click', convertFiles);

// Drag and Drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
});

uploadArea.addEventListener('click', () => fileInput.click());

// Funções
function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    handleFiles(files);
}

function isAudioFile(file) {
    // Verifica pela extensão
    const ext = file.name.toLowerCase().split('.').pop();
    if (FORMATOS_AUDIO.includes(ext)) {
        return true;
    }
    // Verifica pelo tipo MIME
    if (file.type && file.type.startsWith('audio/')) {
        return true;
    }
    return false;
}

function handleFiles(files) {
    // Filtra apenas arquivos de áudio
    const audioFiles = files.filter(file => isAudioFile(file));

    if (audioFiles.length === 0) {
        showError('Por favor, selecione arquivos de áudio válidos.');
        return;
    }

    // Verifica limite de arquivos
    const totalFiles = selectedFiles.length + audioFiles.length;
    if (totalFiles > MAX_FILES) {
        const remaining = MAX_FILES - selectedFiles.length;
        if (remaining > 0) {
            audioFiles.splice(remaining);
            showError(`Limite de ${MAX_FILES} arquivos. Apenas os primeiros ${remaining} foram adicionados.`);
        } else {
            showError(`Limite de ${MAX_FILES} arquivos atingido. Remova alguns arquivos antes de adicionar mais.`);
            return;
        }
    }

    // Adiciona arquivos únicos (evita duplicatas)
    audioFiles.forEach(file => {
        if (!selectedFiles.find(f => f.name === file.name && f.size === file.size)) {
            selectedFiles.push(file);
        }
    });

    updateFilesList();
    updateConvertButton();
    hideError();
}

function updateFilesList() {
    if (selectedFiles.length === 0) {
        filesList.style.display = 'none';
        return;
    }

    filesList.style.display = 'block';
    fileCount.textContent = selectedFiles.length;
    filesContainer.innerHTML = '';

    selectedFiles.forEach((file, index) => {
        const fileItem = createFileItem(file, index);
        filesContainer.appendChild(fileItem);
    });
}

function createFileItem(file, index) {
    const div = document.createElement('div');
    div.className = 'file-item';
    div.innerHTML = `
        <div class="file-item-icon">🎵</div>
        <div class="file-item-info">
            <p class="file-item-name">${file.name}</p>
            <p class="file-item-size">${formatFileSize(file.size)}</p>
        </div>
        <button class="file-item-remove" data-index="${index}">✕</button>
    `;

    const removeBtn = div.querySelector('.file-item-remove');
    removeBtn.addEventListener('click', () => removeFile(index));

    return div;
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    updateFilesList();
    updateConvertButton();
    fileInput.value = '';
}

function clearAllFiles() {
    selectedFiles = [];
    fileInput.value = '';
    updateFilesList();
    updateConvertButton();
    hideResult();
    hideError();
    hideProgress();
}

function updateConvertButton() {
    const count = selectedFiles.length;
    convertCount.textContent = count;
    formatDisplay.textContent = formatSelect.value.toUpperCase();
    convertBtn.disabled = count === 0;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function hideResult() {
    result.style.display = 'none';
    downloadLinks.innerHTML = '';
    downloadAllBtn.style.display = 'none';
}

function hideError() {
    error.style.display = 'none';
}

function hideProgress() {
    progressContainer.style.display = 'none';
    progressFill.style.width = '0%';
}

function showError(message) {
    // Substitui quebras de linha por <br> para exibição correta
    const formattedMessage = message.replace(/\n/g, '<br>');
    errorMessage.innerHTML = formattedMessage;
    error.style.display = 'block';
    hideResult();
    hideProgress();
}

async function convertFiles() {
    if (selectedFiles.length === 0) {
        showError('Por favor, selecione pelo menos um arquivo.');
        return;
    }

    // Desabilita o botão e mostra progresso
    convertBtn.disabled = true;
    const btnText = convertBtn.querySelector('.btn-text');
    const btnLoader = convertBtn.querySelector('.btn-loader');
    btnText.style.display = 'none';
    btnLoader.style.display = 'block';
    
    hideResult();
    hideError();
    progressContainer.style.display = 'block';
    progressFill.style.width = '10%';
    progressText.textContent = `Convertendo 0 de ${selectedFiles.length} arquivos...`;

    const convertedFiles = [];
    const failedFiles = [];

    try {
        for (let i = 0; i < selectedFiles.length; i++) {
            const file = selectedFiles[i];
            const progress = ((i + 1) / selectedFiles.length) * 100;
            
            progressFill.style.width = `${Math.min(progress, 95)}%`;
            progressText.textContent = `Convertendo ${i + 1} de ${selectedFiles.length}: ${file.name}`;

            try {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('quality', qualitySelect.value);
                formData.append('format', formatSelect.value);

                // Log para debug
                console.log('Enviando requisição para /convert', {
                    method: 'POST',
                    file: file.name,
                    format: formatSelect.value,
                    quality: qualitySelect.value
                });
                
                // Determina a URL base do servidor Flask
                // Em produção (Vercel), usa URL relativa
                // Em desenvolvimento local, detecta a porta correta
                const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
                const flaskPort = 5000;
                const currentPort = window.location.port || (window.location.protocol === 'https:' ? 443 : 80);
                
                // Se não estiver na porta do Flask e estiver em desenvolvimento local, usa a URL completa
                let apiUrl = '/convert';
                if (!isProduction && currentPort !== flaskPort.toString()) {
                    apiUrl = `http://localhost:${flaskPort}/convert`;
                }
                
                console.log('URL da API:', apiUrl, 'Porta atual:', currentPort, 'Produção:', isProduction);
                
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        // Não definir Content-Type manualmente - o browser define automaticamente para FormData
                    }
                });
                
                console.log('Resposta recebida:', {
                    status: response.status,
                    statusText: response.statusText,
                    contentType: response.headers.get('content-type'),
                    ok: response.ok
                });

                // Verifica o tipo de conteúdo da resposta
                const contentType = response.headers.get('content-type') || '';
                
                if (!response.ok) {
                    // Tenta ler como JSON se for um erro
                    let errorMessage = `Erro HTTP ${response.status}: ${response.statusText}`;
                    try {
                        // Clona a resposta para poder ler múltiplas vezes
                        const responseClone = response.clone();
                        if (contentType.includes('application/json')) {
                            const errorData = await responseClone.json();
                            errorMessage = errorData.error || errorMessage;
                        } else {
                            const text = await responseClone.text();
                            // Tenta parsear como JSON mesmo que o content-type não seja JSON
                            try {
                                const jsonData = JSON.parse(text);
                                errorMessage = jsonData.error || errorMessage;
                            } catch {
                                errorMessage = text || errorMessage;
                            }
                        }
                    } catch (e) {
                        console.error('Erro ao ler resposta de erro:', e);
                        errorMessage = `Erro HTTP ${response.status}: ${response.statusText}. Não foi possível ler a mensagem de erro detalhada.`;
                    }
                    throw new Error(errorMessage);
                }

                // Verifica se a resposta é um arquivo (blob) ou JSON de erro
                if (contentType.includes('application/json')) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Erro na conversão');
                }

                const blob = await response.blob();
                
                // Verifica se o blob não está vazio
                if (blob.size === 0) {
                    throw new Error('Arquivo convertido está vazio. Verifique se o FFmpeg está funcionando corretamente.');
                }
                
                const url = window.URL.createObjectURL(blob);
                
                // Obtém o nome do arquivo do header Content-Disposition ou gera um baseado no formato
                const contentDisposition = response.headers.get('Content-Disposition');
                let filename;
                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                    if (filenameMatch && filenameMatch[1]) {
                        filename = filenameMatch[1].replace(/['"]/g, '');
                    } else {
                        const ext = file.name.split('.').pop();
                        filename = file.name.replace(`.${ext}`, `.${formatSelect.value}`);
                    }
                } else {
                    const ext = file.name.split('.').pop();
                    filename = file.name.replace(`.${ext}`, `.${formatSelect.value}`);
                }

                convertedFiles.push({
                    name: filename,
                    url: url,
                    originalName: file.name
                });

            } catch (err) {
                console.error(`Erro ao converter ${file.name}:`, err);
                const errorMsg = err.message || 'Erro desconhecido na conversão';
                failedFiles.push({
                    name: file.name,
                    error: errorMsg
                });
            }
        }

        progressFill.style.width = '100%';
        progressText.textContent = 'Concluído!';

        // Mostra resultado
        setTimeout(() => {
            displayResults(convertedFiles, failedFiles);
            hideProgress();
            btnText.style.display = 'block';
            btnLoader.style.display = 'none';
            convertBtn.disabled = false;
        }, 500);

    } catch (err) {
        console.error('Erro:', err);
        showError(err.message || 'Ocorreu um erro durante a conversão. Tente novamente.');
        btnText.style.display = 'block';
        btnLoader.style.display = 'none';
        convertBtn.disabled = false;
        hideProgress();
    }
}

function displayResults(convertedFiles, failedFiles) {
    if (convertedFiles.length === 0) {
        let errorMsg = 'Nenhum arquivo foi convertido com sucesso.';
        if (failedFiles.length > 0) {
            const errors = failedFiles.map(f => `\n• ${f.name}: ${f.error}`).join('');
            errorMsg += '\n\nErros encontrados:' + errors;
        }
        showError(errorMsg);
        return;
    }

    result.style.display = 'block';
    
    if (convertedFiles.length === 1) {
        resultMessage.textContent = 'Seu arquivo foi convertido com sucesso.';
        const link = document.createElement('a');
        link.href = convertedFiles[0].url;
        link.download = convertedFiles[0].name;
        link.className = 'btn-download';
        link.textContent = `⬇️ Baixar ${convertedFiles[0].name}`;
        downloadLinks.appendChild(link);
    } else {
        resultMessage.textContent = `${convertedFiles.length} arquivo(s) convertido(s) com sucesso.`;
        
        // Lista de downloads individuais
        convertedFiles.forEach(file => {
            const linkItem = document.createElement('div');
            linkItem.className = 'download-link-item';
            linkItem.innerHTML = `
                <a href="${file.url}" download="${file.name}">⬇️ ${file.name}</a>
            `;
            downloadLinks.appendChild(linkItem);
        });

        // Botão para baixar todos como ZIP (se houver mais de 1 arquivo)
        if (convertedFiles.length > 1) {
            downloadAllBtn.style.display = 'inline-block';
            downloadAllBtn.onclick = () => {
                convertedFiles.forEach(file => {
                    const link = document.createElement('a');
                    link.href = file.url;
                    link.download = file.name;
                    link.style.display = 'none';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                });
            };
        }
    }

    if (failedFiles.length > 0) {
        const errorMsg = `\n\n${failedFiles.length} arquivo(s) falharam:\n${failedFiles.map(f => `- ${f.name}`).join('\n')}`;
        showError(`Alguns arquivos não puderam ser convertidos.${errorMsg}`);
    }
}
