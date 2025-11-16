// Elementos do DOM
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const selectFileBtn = document.getElementById('selectFileBtn');
const filesList = document.getElementById('filesList');
const filesContainer = document.getElementById('filesContainer');
const fileCount = document.getElementById('fileCount');
const clearAllBtn = document.getElementById('clearAllBtn');
const qualitySelect = document.getElementById('qualitySelect');
const convertBtn = document.getElementById('convertBtn');
const convertCount = document.getElementById('convertCount');
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

function handleFiles(files) {
    // Filtra apenas arquivos MP4
    const mp4Files = files.filter(file => 
        file.name.toLowerCase().endsWith('.mp4') || file.type.includes('mp4')
    );

    if (mp4Files.length === 0) {
        showError('Por favor, selecione arquivos MP4 válidos.');
        return;
    }

    // Verifica limite de arquivos
    const totalFiles = selectedFiles.length + mp4Files.length;
    if (totalFiles > MAX_FILES) {
        const remaining = MAX_FILES - selectedFiles.length;
        if (remaining > 0) {
            mp4Files.splice(remaining);
            showError(`Limite de ${MAX_FILES} arquivos. Apenas os primeiros ${remaining} foram adicionados.`);
        } else {
            showError(`Limite de ${MAX_FILES} arquivos atingido. Remova alguns arquivos antes de adicionar mais.`);
            return;
        }
    }

    // Adiciona arquivos únicos (evita duplicatas)
    mp4Files.forEach(file => {
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
    errorMessage.textContent = message;
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

                const response = await fetch('/convert', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Erro na conversão');
                }

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const filename = file.name.replace('.mp4', '.m4a');

                convertedFiles.push({
                    name: filename,
                    url: url,
                    originalName: file.name
                });

            } catch (err) {
                console.error(`Erro ao converter ${file.name}:`, err);
                failedFiles.push({
                    name: file.name,
                    error: err.message
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
        showError('Nenhum arquivo foi convertido com sucesso.');
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
