# Conversor de Áudio MP4 para M4A

Conversor simples e eficiente de arquivos de áudio MP4 para formato M4A usando Python e FFmpeg.

**Agora com interface web moderna e intuitiva!** 🎨

## 📋 Requisitos

- Python 3.6 ou superior
- FFmpeg instalado no sistema

### Instalação do FFmpeg

#### Windows

**⚠️ IMPORTANTE:** O FFmpeg é obrigatório para o funcionamento do conversor!

**Opção 1: Chocolatey (Mais fácil)**
```powershell
# Execute no PowerShell como Administrador
choco install ffmpeg
```

**Opção 2: Download Manual**
1. Baixe o FFmpeg de: https://www.gyan.dev/ffmpeg/builds/
   - Escolha: `ffmpeg-release-essentials.zip`
2. Extraia o arquivo ZIP (ex: `C:\ffmpeg`)
3. Adicione ao PATH do sistema:
   - Pressione `Win + X` → `Sistema`
   - `Configurações avançadas do sistema` → `Variáveis de Ambiente`
   - Em `Variáveis do sistema`, encontre `Path` → `Editar` → `Novo`
   - Adicione: `C:\ffmpeg\bin` (ou o caminho onde você extraiu)
   - Clique em `OK` em todas as janelas
4. **Feche e reabra o terminal** para aplicar as mudanças

**Opção 3: Scoop**
```powershell
scoop install ffmpeg
```

**Verificar instalação:**
```bash
# Execute este comando para verificar
python verificar_ffmpeg.py

# Ou teste diretamente:
ffmpeg -version
```

#### Linux
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

#### macOS
```bash
brew install ffmpeg
```

## 🚀 Instalação

1. Clone ou baixe este repositório
2. Instale as dependências Python:

```bash
pip install -r requirements.txt
```

## 💻 Uso

### 🌐 Interface Web (Recomendado)

1. Inicie o servidor web:
```bash
python app.py
```

2. Abra seu navegador e acesse:
```
http://localhost:5000
```

3. Arraste e solte seu arquivo MP4 ou clique para selecionar
4. Escolha a qualidade desejada
5. Clique em "Converter para M4A"
6. Baixe o arquivo convertido

A interface web oferece:
- ✨ Design moderno e responsivo
- 🎯 Drag and drop de arquivos
- 📊 Barra de progresso
- ⚙️ Seleção de qualidade
- 📱 Compatível com dispositivos móveis

### 💻 Linha de Comando

### Converter um arquivo único

```bash
python conversor_audio.py arquivo.mp4
```

O arquivo de saída será criado automaticamente com o mesmo nome, mas com extensão `.m4a`.

### Converter com nome de saída específico

```bash
python conversor_audio.py entrada.mp4 -o saida.m4a
```

### Converter todos os MP4 de um diretório

```bash
python conversor_audio.py pasta/ -d
```

### Especificar qualidade de áudio

```bash
python conversor_audio.py arquivo.mp4 -q 256k
```

Qualidades disponíveis: `128k`, `192k` (padrão), `256k`, `320k`

## 📝 Exemplos

```bash
# Conversão básica
python conversor_audio.py musica.mp4

# Conversão com qualidade alta
python conversor_audio.py musica.mp4 -q 320k -o musica_alta_qualidade.m4a

# Converter todos os arquivos de uma pasta
python conversor_audio.py ./musicas/ -d

# Converter com qualidade personalizada
python conversor_audio.py audio.mp4 -q 256k
```

## ⚙️ Parâmetros

- `entrada`: Arquivo MP4 de entrada ou diretório
- `-o, --output`: Arquivo M4A de saída (opcional)
- `-d, --diretorio`: Processar todos os arquivos MP4 do diretório
- `-q, --qualidade`: Bitrate de áudio (padrão: 192k)

## 🔧 Características

- ✨ **Interface Web Moderna**: Design elegante e fácil de usar
- 🚀 Conversão rápida e eficiente
- 📦 Suporte a conversão em lote (via CLI)
- 🎚️ Controle de qualidade de áudio
- 📱 Interface responsiva para mobile
- 🎨 Drag and drop de arquivos
- 📊 Barra de progresso em tempo real
- 💻 Interface de linha de comando disponível

## 📄 Licença

Este projeto é de código aberto e está disponível para uso livre.

