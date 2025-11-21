# Instruções de Deploy na Vercel

## ⚠️ Importante: Limitação do FFmpeg na Vercel

A Vercel **não suporta FFmpeg nativamente** em seus servidores. Para fazer o conversor funcionar na Vercel, você precisará:

### Opção 1: Usar um serviço externo de conversão
- Integrar com uma API externa que forneça conversão de áudio
- Exemplos: Cloudinary, AWS Lambda com FFmpeg, etc.

### Opção 2: Usar uma alternativa serverless
- Deploy em plataformas que suportam FFmpeg:
  - **Railway** (recomendado)
  - **Render**
  - **Fly.io**
  - **AWS Lambda** (com layer FFmpeg)

### Opção 3: Converter no cliente (browser)
- Usar bibliotecas JavaScript como `ffmpeg.wasm` para conversão no navegador
- Não requer servidor, mas pode ser mais lento

## 📋 Arquivos Configurados para Vercel

Os seguintes arquivos já estão configurados:

- ✅ `vercel.json` - Configuração de rotas e builds
- ✅ `api/index.py` - Entrypoint WSGI para Vercel
- ✅ `requirements.txt` - Dependências Python
- ✅ `app.py` - Aplicação Flask principal

## 🚀 Como Fazer Deploy

### Via CLI da Vercel:

```bash
# 1. Instale a CLI da Vercel (se ainda não tiver)
npm i -g vercel

# 2. Faça login
vercel login

# 3. Deploy
vercel

# 4. Para produção
vercel --prod
```

### Via GitHub (Recomendado):

1. Faça commit e push das alterações:
```bash
git add .
git commit -m "Atualização para deploy na Vercel"
git push
```

2. No dashboard da Vercel:
   - Conecte seu repositório GitHub
   - A Vercel detectará automaticamente o `vercel.json`
   - O deploy será feito automaticamente a cada push

## 🔧 Configurações Importantes

### Variáveis de Ambiente (se necessário):

No dashboard da Vercel, adicione variáveis de ambiente se precisar:
- `FFMPEG_PATH` - Caminho do FFmpeg (se disponível)
- `MAX_UPLOAD_SIZE_MB` - Limite máximo aceito por upload (ex.: 50 para plano Pro). O frontend mostra o limite atual e bloqueia arquivos maiores.
- `PYTHONUNBUFFERED=1` - Já configurado no vercel.json

### Limites da Vercel:

- **Timeout**: 10 segundos (Hobby), 60 segundos (Pro)
- **Tamanho máximo de upload**: 4.5MB (Hobby), 50MB (Pro)
- **Memória**: 1024MB

> Se precisar converter arquivos com mais de 50MB, execute o app localmente (`python app.py`) ou use a CLI (`python conversor_audio.py arquivo.mp4`). A Vercel retornará `FUNCTION_PAYLOAD_TOO_LARGE` quando o arquivo exceder o limite configurado.

## 📝 Notas

- O código está preparado para detectar automaticamente se está em produção ou desenvolvimento
- Em produção, usa URLs relativas
- Em desenvolvimento local, redireciona para a porta 5000 do Flask

## 🐛 Troubleshooting

Se encontrar erros:

1. Verifique os logs no dashboard da Vercel
2. Certifique-se de que todas as dependências estão no `requirements.txt`
3. Verifique se o FFmpeg está disponível (provavelmente não estará)

