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
const fileSizeLimit = document.getElementById('fileSizeLimit');

const MAX_FILES = 15;
let selectedFiles = [];

// Formatos de áudio suportados
const FORMATOS_AUDIO = ['mp3', 'wav', 'flac', 'ogg', 'aac', 'm4a', 'mp4', 'wma', 'aiff', 'aif', 
                        'opus', 'amr', '3gp', 'ac3', 'eac3', 'dts', 'mp2', 'mpa', 'ra', 'rm',
                        'au', 'snd', 'voc', 'wv', 'ape', 'tta', 'tak', 'webm'];

// Configurações dinâmicas
const FALLBACK_MAX_UPLOAD_SIZE_MB = 50;
const FALLBACK_EDGE_UPLOAD_LIMIT_MB = 50;
const MB_IN_BYTES = 1024 * 1024;
const PAYLOAD_LIMIT_ERROR = '__PAYLOAD_LIMIT__';
const flaskPort = 5000;
const apiBaseUrl = getApiBaseUrl();
const convertEndpoint = buildApiUrl('/convert');
const configEndpoint = buildApiUrl('/api/config');
let maxUploadSizeMB = FALLBACK_MAX_UPLOAD_SIZE_MB;
let edgeUploadLimitMB = FALLBACK_EDGE_UPLOAD_LIMIT_MB;
let serverConfigLoaded = false;
let deploymentHint = '';

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

// Inicialização
initializeApp();

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

    const { validFiles, oversizedFiles } = splitFilesBySize(audioFiles);
    if (oversizedFiles.length > 0) {
        showError(buildOversizedFilesMessage(oversizedFiles));
    }

    // Verifica limite de arquivos
    const totalFiles = selectedFiles.length + validFiles.length;
    if (totalFiles > MAX_FILES) {
        const remaining = Math.max(MAX_FILES - selectedFiles.length, 0);
        if (remaining > 0) {
            validFiles.splice(remaining);
            showError(`Limite de ${MAX_FILES} arquivos. Apenas os primeiros ${remaining} foram adicionados.`);
        } else {
            showError(`Limite de ${MAX_FILES} arquivos atingido. Remova alguns arquivos antes de adicionar mais.`);
            return;
        }
    }

    // Adiciona arquivos únicos (evita duplicatas)
    let filesAdded = 0;
    validFiles.forEach(file => {
        if (!selectedFiles.find(f => f.name === file.name && f.size === file.size)) {
            selectedFiles.push(file);
            filesAdded += 1;
        }
    });

    updateFilesList();
    updateConvertButton();
    if (filesAdded > 0 && oversizedFiles.length === 0) {
        hideError();
    }
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
                
                const response = await fetch(convertEndpoint, {
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
                    if (response.status === 413) {
                        throw new Error(PAYLOAD_LIMIT_ERROR);
                    }

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
                if (errorMsg === PAYLOAD_LIMIT_ERROR || isPayloadTooLarge(errorMsg)) {
                    failedFiles.push({
                        name: file.name,
                        error: buildLargeFileError(file.name, file.size, { preferEdgeLimit: true })
                    });
                    continue;
                }

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

function initializeApp() {
    updateFileLimitHint();
    loadServerConfig();
}

function getApiBaseUrl() {
    const hostname = window.location.hostname;
    const currentPort = window.location.port || (window.location.protocol === 'https:' ? 443 : 80);
    const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1';

    if (isLocalhost && currentPort !== flaskPort.toString()) {
        return `http://localhost:${flaskPort}`;
    }

    return '';
}

function buildApiUrl(path) {
    if (!apiBaseUrl) {
        return path;
    }
    if (path.startsWith('/')) {
        return `${apiBaseUrl}${path}`;
    }
    return `${apiBaseUrl}/${path}`;
}

async function loadServerConfig() {
    try {
        const response = await fetch(configEndpoint);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const data = await response.json();

        if (isPositiveNumber(data.max_upload_size_mb)) {
            maxUploadSizeMB = data.max_upload_size_mb;
        }

        if (isPositiveNumber(data.edge_upload_limit_mb)) {
            edgeUploadLimitMB = data.edge_upload_limit_mb;
        }

        if (typeof data.deployment_hint === 'string') {
            deploymentHint = data.deployment_hint;
        }

        serverConfigLoaded = true;
        updateFileLimitHint();
    } catch (err) {
        console.warn('Não foi possível carregar as configurações do servidor. Usando fallback.', err);
        serverConfigLoaded = false;
        updateFileLimitHint(true);
    }
}

function updateFileLimitHint(hasError = false) {
    if (!fileSizeLimit) {
        return;
    }

    if (hasError) {
        fileSizeLimit.textContent = `Limite de tamanho: ${getReadableLimitText()} (valor padrão)`;
        return;
    }

    if (!serverConfigLoaded && maxUploadSizeMB === FALLBACK_MAX_UPLOAD_SIZE_MB) {
        fileSizeLimit.textContent = `Limite de tamanho: ${getReadableLimitText()} (detectando...)`;
        return;
    }

    fileSizeLimit.textContent = `Limite de tamanho: até ${getReadableLimitText()} por arquivo`;
}

function splitFilesBySize(files) {
    const limitMB = getActiveLimitMB();
    if (!limitMB) {
        return { validFiles: files, oversizedFiles: [] };
    }

    const limitBytes = limitMB * MB_IN_BYTES;
    const oversizedFiles = [];
    const validFiles = [];

    files.forEach(file => {
        if (file.size > limitBytes) {
            oversizedFiles.push(file);
        } else {
            validFiles.push(file);
        }
    });

    return { validFiles, oversizedFiles };
}

function buildOversizedFilesMessage(oversizedFiles) {
    const limitText = getReadableLimitText();
    const list = oversizedFiles
        .map(file => `• ${file.name} (${formatFileSize(file.size)})`)
        .join('\n');

    let message = `Alguns arquivos foram ignorados porque excedem o limite de ${limitText}.\n\n${list}`;

    if (deploymentHint) {
        message += `\n\n${deploymentHint}`;
    } else {
        message += '\n\nDica: Para converter arquivos maiores, execute o app localmente (python app.py) ou utilize o conversor via linha de comando.';
    }

    return message;
}

function buildLargeFileError(fileName, fileSizeBytes, options = {}) {
    const limitText = getReadableLimitText(options.preferEdgeLimit);
    const formattedSize = formatFileSize(fileSizeBytes);
    let message = `O arquivo "${fileName}" tem ${formattedSize} e excede o limite de ${limitText} imposto pelo servidor atual.`;

    if (deploymentHint) {
        message += `\n\n${deploymentHint}`;
    } else {
        message += '\n\nExecute o aplicativo localmente (python app.py) para converter arquivos grandes ou use a linha de comando: python conversor_audio.py <arquivo.mp4>';
    }

    return message;
}

function getReadableLimitText(preferEdgeLimit = false) {
    const limitMB = getActiveLimitMB(preferEdgeLimit);
    if (!limitMB) {
        return 'tamanho indefinido';
    }
    return `${stripTrailingZeros(limitMB)} MB`;
}

function isPayloadTooLarge(message) {
    if (!message) {
        return false;
    }
    const normalized = message.toLowerCase();
    return normalized.includes('entity too large') ||
        normalized.includes('payload too large') ||
        normalized.includes('function_payload_too_large');
}

function getActiveLimitMB(preferEdgeLimit = false) {
    const limits = [];
    if (isPositiveNumber(maxUploadSizeMB)) {
        limits.push(maxUploadSizeMB);
    }
    if (isPositiveNumber(edgeUploadLimitMB)) {
        limits.push(edgeUploadLimitMB);
    }

    if (limits.length === 0) {
        return undefined;
    }

    if (preferEdgeLimit && isPositiveNumber(edgeUploadLimitMB)) {
        return edgeUploadLimitMB;
    }

    return Math.min(...limits);
}

function isPositiveNumber(value) {
    return typeof value === 'number' && !Number.isNaN(value) && value > 0;
}

function stripTrailingZeros(value) {
    if (Number.isInteger(value)) {
        return value.toString();
    }
    return value.toFixed(2).replace(/\.?0+$/, '');
}
