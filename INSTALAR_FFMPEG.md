# 🔧 Como Instalar o FFmpeg no Windows

Se você está recebendo o erro **"[WinError 2] O sistema não pode encontrar o arquivo especificado"**, significa que o FFmpeg não está instalado ou não está no PATH do sistema.

## ✅ Solução Rápida (Recomendada)

### Usando Chocolatey

1. Abra o PowerShell **como Administrador**
2. Execute:
   ```powershell
   choco install ffmpeg
   ```
3. Feche e reabra o terminal
4. Teste: `ffmpeg -version`

---

## 📥 Instalação Manual

### Passo 1: Download
1. Acesse: https://www.gyan.dev/ffmpeg/builds/
2. Baixe: **ffmpeg-release-essentials.zip**

### Passo 2: Extrair
1. Extraia o ZIP em uma pasta (ex: `C:\ffmpeg`)
2. Você deve ter uma estrutura como:
   ```
   C:\ffmpeg\
   └── bin\
       ├── ffmpeg.exe
       ├── ffplay.exe
       └── ffprobe.exe
   ```

### Passo 3: Adicionar ao PATH

1. Pressione `Win + X` e escolha **"Sistema"**
2. Clique em **"Configurações avançadas do sistema"**
3. Clique em **"Variáveis de Ambiente"**
4. Em **"Variáveis do sistema"**, encontre a variável **`Path`**
5. Clique em **"Editar"**
6. Clique em **"Novo"**
7. Adicione o caminho da pasta `bin`:
   ```
   C:\ffmpeg\bin
   ```
   (Ajuste o caminho se você extraiu em outro local)
8. Clique em **"OK"** em todas as janelas

### Passo 4: Verificar

1. **Feche TODOS os terminais abertos**
2. Abra um novo terminal (PowerShell ou CMD)
3. Execute:
   ```bash
   ffmpeg -version
   ```
4. Se aparecer informações sobre o FFmpeg, está funcionando! ✅

---

## 🧪 Testar a Instalação

Execute este script Python para verificar:

```bash
python verificar_ffmpeg.py
```

Ou teste diretamente no terminal:

```bash
ffmpeg -version
```

---

## ❓ Problemas Comuns

### "ffmpeg não é reconhecido como comando"
- Certifique-se de ter **fechado e reaberto** o terminal após adicionar ao PATH
- Verifique se o caminho está correto no PATH
- Reinicie o computador se necessário

### "Ainda recebo o erro WinError 2"
- Verifique se o FFmpeg está realmente instalado: `ffmpeg -version`
- Certifique-se de que a pasta `bin` contém `ffmpeg.exe`
- Tente executar o servidor em um novo terminal

### "Não consigo adicionar ao PATH"
- Certifique-se de estar usando uma conta de administrador
- Tente adicionar manualmente editando a variável de ambiente

---

## 🚀 Após Instalar

Depois de instalar o FFmpeg corretamente:

1. Feche o servidor se estiver rodando (Ctrl+C)
2. Feche e reabra o terminal
3. Execute novamente:
   ```bash
   python app.py
   ```

O servidor agora deve iniciar sem erros! 🎉

