#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor Flask para conversão de áudio universal
Suporta todos os formatos de áudio
"""

import io
import os
import sys
import subprocess
import tempfile
import uuid
import re
from pathlib import Path
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import ffmpeg

app = Flask(__name__)

# Configurações globais
MAX_UPLOAD_SIZE_MB = int(os.environ.get('MAX_UPLOAD_SIZE_MB', '100'))
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Configura CORS para permitir todas as origens e métodos
CORS(app, resources={
    r"/convert": {
        "origins": "*",
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})
# Também configura CORS globalmente como fallback
CORS(app, supports_credentials=True)

# Configurações
FFMPEG_BINARY = os.environ.get('FFMPEG_PATH', 'ffmpeg')
os.environ['FFMPEG_BINARY'] = FFMPEG_BINARY

BASE_TEMP_DIR = os.path.join(tempfile.gettempdir(), 'audio-converter')
UPLOAD_FOLDER = os.path.join(BASE_TEMP_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_TEMP_DIR, 'outputs')

# Formatos de áudio suportados
FORMATOS_ENTRADA = {
    'mp3', 'wav', 'flac', 'ogg', 'aac', 'm4a', 'mp4', 'wma', 'aiff', 'aif',
    'opus', 'amr', '3gp', 'ac3', 'eac3', 'dts', 'mp2', 'mpa', 'ra', 'rm',
    'au', 'snd', 'voc', 'wv', 'ape', 'tta', 'tak', 'ofr', 'ofs', 'ofc',
    'rka', 'shn', 'aa', 'aax', 'act', 'alac', 'awb', 'dct', 'dss', 'dvf',
    'gsm', 'iklax', 'ivs', 'mmf', 'mpc', 'msv', 'nmf', 'oga', 'mogg',
    'raw', 'rf64', 'sln', 'vox', 'webm'
}

FORMATOS_SAIDA = {
    'mp3': {'acodec': 'libmp3lame', 'ext': 'mp3', 'mimetype': 'audio/mpeg'},
    'wav': {'acodec': 'pcm_s16le', 'ext': 'wav', 'mimetype': 'audio/wav'},
    'flac': {'acodec': 'flac', 'ext': 'flac', 'mimetype': 'audio/flac'},
    'ogg': {'acodec': 'libvorbis', 'ext': 'ogg', 'mimetype': 'audio/ogg'},
    'aac': {'acodec': 'aac', 'ext': 'aac', 'mimetype': 'audio/aac'},
    'm4a': {'acodec': 'aac', 'ext': 'm4a', 'mimetype': 'audio/mp4'},
    'opus': {'acodec': 'libopus', 'ext': 'opus', 'mimetype': 'audio/opus'},
    'wma': {'acodec': 'wmav2', 'ext': 'wma', 'mimetype': 'audio/x-ms-wma'},
    'aiff': {'acodec': 'pcm_s16be', 'ext': 'aiff', 'mimetype': 'audio/aiff'},
    'aif': {'acodec': 'pcm_s16be', 'ext': 'aif', 'mimetype': 'audio/aiff'},
    'ac3': {'acodec': 'ac3', 'ext': 'ac3', 'mimetype': 'audio/ac3'},
    'mp2': {'acodec': 'mp2', 'ext': 'mp2', 'mimetype': 'audio/mpeg'},
    'amr': {'acodec': 'libopencore_amrnb', 'ext': 'amr', 'mimetype': 'audio/amr'},
    'webm': {'acodec': 'libopus', 'ext': 'webm', 'mimetype': 'audio/webm'}
}

ALLOWED_EXTENSIONS = FORMATOS_ENTRADA

# Cria os diretórios se não existirem
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def check_ffmpeg():
    """Verifica se o FFmpeg está instalado e acessível"""
    # Tenta verificar com o binário configurado
    try:
        subprocess.run(
            [FFMPEG_BINARY, '-version'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            timeout=5
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, OSError, subprocess.TimeoutExpired):
        pass
    
    # Tenta verificar com 'ffmpeg' diretamente
    try:
        subprocess.run(
            ['ffmpeg', '-version'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            timeout=5
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, OSError, subprocess.TimeoutExpired):
        pass
    
    # Tenta verificar em locais comuns do Windows
    if sys.platform == 'win32':
        common_paths = [
            r'C:\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe',
            os.path.expanduser(r'~\ffmpeg\bin\ffmpeg.exe'),
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                try:
                    subprocess.run(
                        [path, '-version'],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=True,
                        timeout=5
                    )
                    # Atualiza a variável de ambiente se encontrou
                    os.environ['FFMPEG_BINARY'] = path
                    return True
                except (subprocess.CalledProcessError, OSError, subprocess.TimeoutExpired):
                    continue
    
    return False


def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detectar_formato(arquivo):
    """Detecta o formato do arquivo pela extensão"""
    ext = Path(arquivo).suffix.lower().lstrip('.')
    return ext if ext in FORMATOS_ENTRADA else None


# Rotas de API devem vir antes das rotas de arquivos estáticos
@app.route('/convert', methods=['POST', 'OPTIONS'])
def convert():
    """Converte arquivo de áudio para outro formato"""
    # Log para debug
    print(f"=== Requisição recebida: {request.method} /convert ===")
    print(f"URL: {request.url}")
    print(f"Headers: {dict(request.headers)}")
    print(f"Content-Type: {request.content_type}")
    print(f"Form data: {dict(request.form)}")
    print(f"Files: {list(request.files.keys())}")
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    if request.method != 'POST':
        return jsonify({
            'error': f'Método {request.method} não permitido. Use POST.',
            'method_received': request.method,
            'methods_allowed': ['POST', 'OPTIONS']
        }), 405
    
    try:
        # Verifica se o arquivo foi enviado
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        quality = request.form.get('quality', '192k')
        formato_saida = request.form.get('format', 'm4a').lower().lstrip('.')
        
        # Verifica se o arquivo foi selecionado
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        # Verifica se é um arquivo permitido
        if not allowed_file(file.filename):
            formatos_str = ', '.join(sorted(FORMATOS_ENTRADA))
            return jsonify({'error': f'Formato de arquivo não permitido. Formatos suportados: {formatos_str}'}), 400
        
        # Verifica se o formato de saída é suportado
        if formato_saida not in FORMATOS_SAIDA:
            formatos_str = ', '.join(sorted(FORMATOS_SAIDA.keys()))
            return jsonify({'error': f'Formato de saída não suportado. Formatos disponíveis: {formatos_str}'}), 400
        
        # Sanitiza o nome do arquivo para evitar problemas com espaços e caracteres especiais
        # Gera um nome temporário seguro para o arquivo de entrada
        file_ext = os.path.splitext(file.filename)[1] or '.tmp'
        safe_input_name = f"{uuid.uuid4().hex}{file_ext}"
        input_path = os.path.join(UPLOAD_FOLDER, safe_input_name)
        
        # Salva o arquivo temporariamente
        file.save(input_path)
        
        # Gera o nome do arquivo de saída (mantém nome original para download)
        config_saida = FORMATOS_SAIDA[formato_saida]
        output_filename = os.path.splitext(file.filename)[0] + '.' + config_saida['ext']
        safe_output_name = f"{uuid.uuid4().hex}.{config_saida['ext']}"
        output_path = os.path.join(OUTPUT_FOLDER, safe_output_name)
        
        try:
            # Verifica se o arquivo de entrada existe e tem conteúdo
            if not os.path.exists(input_path):
                return jsonify({'error': 'Arquivo de entrada não foi salvo corretamente'}), 500
            
            file_size = os.path.getsize(input_path)
            if file_size == 0:
                return jsonify({'error': 'Arquivo de entrada está vazio'}), 400
            
            # Converte o arquivo - usa caminhos absolutos e entre aspas para evitar problemas com espaços
            input_path_abs = os.path.abspath(input_path)
            output_path_abs = os.path.abspath(output_path)
            
            # Verifica se o arquivo de entrada é realmente um arquivo de áudio válido (opcional)
            # Se ffprobe não estiver disponível, tenta converter mesmo assim
            try:
                probe = ffmpeg.probe(input_path_abs)
                if 'streams' not in probe or len(probe['streams']) == 0:
                    return jsonify({'error': 'Arquivo não contém streams de áudio válidos'}), 400
            except (ffmpeg.Error, FileNotFoundError, OSError) as probe_error:
                # Se ffprobe não estiver disponível, apenas loga e continua
                # O FFmpeg pode converter mesmo sem o probe
                error_msg = str(probe_error)
                if 'ffprobe' in error_msg.lower() or 'no such file' in error_msg.lower():
                    print(f"Aviso: ffprobe não encontrado. Tentando converter sem validação prévia: {error_msg}")
                    # Continua com a conversão mesmo sem probe
                else:
                    # Outro tipo de erro do probe - pode ser arquivo inválido
                    probe_msg = probe_error.stderr.decode('utf-8', errors='ignore') if hasattr(probe_error, 'stderr') and probe_error.stderr else str(probe_error)
                    print(f"Aviso ao fazer probe do arquivo: {probe_msg[:300]}. Tentando converter mesmo assim.")
            
            stream = ffmpeg.input(input_path_abs)
            
            # Prepara parâmetros de saída
            output_params = {
                'acodec': config_saida['acodec'],
                'ac': 2,  # 2 canais (estéreo)
                'ar': 44100  # Sample rate de 44.1kHz
            }
            
            # Adiciona bitrate apenas para formatos comprimidos
            formatos_sem_bitrate = {'wav', 'aiff', 'aif', 'flac'}
            if formato_saida not in formatos_sem_bitrate:
                output_params['audio_bitrate'] = quality
            
            # Para FLAC, usa compressão ao invés de bitrate
            if formato_saida == 'flac':
                output_params['compression_level'] = 5
                # Remove audio_bitrate se foi adicionado
                output_params.pop('audio_bitrate', None)
            
            stream = ffmpeg.output(stream, output_path_abs, **output_params)
            
            # Executa a conversão com captura de erros
            try:
                ffmpeg.run(stream, overwrite_output=True, quiet=True)
            except Exception as conv_error:
                # Captura erro mais detalhado
                error_details = str(conv_error)
                if hasattr(conv_error, 'stderr') and conv_error.stderr:
                    try:
                        error_details = conv_error.stderr.decode('utf-8', errors='ignore')
                    except:
                        error_details = str(conv_error.stderr)
                raise Exception(f'Erro durante conversão FFmpeg: {error_details[:500]}')

            # Verifica se o arquivo de saída foi criado
            if not os.path.exists(output_path_abs):
                return jsonify({'error': 'Arquivo de saída não foi criado. Verifique se o FFmpeg está funcionando corretamente.'}), 500
            
            output_size = os.path.getsize(output_path_abs)
            if output_size == 0:
                return jsonify({'error': 'Arquivo convertido está vazio. Verifique se o formato de entrada é válido.'}), 500

            # Lê o arquivo convertido da pasta temporária
            with open(output_path_abs, 'rb') as converted_file:
                file_bytes = io.BytesIO(converted_file.read())

            file_bytes.seek(0)

            response = send_file(
                file_bytes,
                as_attachment=True,
                download_name=output_filename,
                mimetype=config_saida['mimetype']
            )

            response.headers['Cache-Control'] = 'no-store'

            return response
        
        except ffmpeg.Error as e:
            error_message = ''
            if e.stderr:
                try:
                    error_message = e.stderr.decode('utf-8', errors='ignore')
                except:
                    error_message = str(e.stderr)
            else:
                error_message = str(e)
            
            # Verifica se o erro é relacionado ao FFmpeg não encontrado
            error_lower = error_message.lower()
            if 'ffmpeg' in error_lower or 'not found' in error_lower or 'winerror 2' in error_lower or 'no such file' in error_lower:
                # Verifica novamente se o FFmpeg está disponível
                if not check_ffmpeg():
                    return jsonify({
                        'error': 'FFmpeg não encontrado. Por favor, instale o FFmpeg e adicione ao PATH do sistema.\n\n📥 Instalação no Windows:\n\n1. Chocolatey (Recomendado):\n   choco install ffmpeg\n\n2. Download Manual:\n   - Baixe de: https://www.gyan.dev/ffmpeg/builds/\n   - Extraia e adicione a pasta \\bin ao PATH\n\n3. Após instalar, feche e reabra o terminal\n4. Execute: python verificar_ffmpeg.py'
                    }), 500
                else:
                    # FFmpeg foi encontrado, mas houve outro erro
                    return jsonify({'error': f'Erro na conversão FFmpeg: {error_message[:500]}'}), 500
            
            # Extrai mensagem de erro mais útil
            if 'invalid data found' in error_lower or 'could not find codec' in error_lower:
                return jsonify({'error': f'Formato de arquivo não suportado ou corrompido: {error_message[:200]}'}), 400
            
            # Retorna mensagem de erro detalhada
            return jsonify({'error': f'Erro na conversão FFmpeg: {error_message[:500]}'}), 500
        
        except Exception as e:
            # Captura outros erros genéricos
            error_str = str(e)
            error_lower = error_str.lower()
            
            if 'winerror 2' in error_lower or 'ffmpeg' in error_lower or 'not found' in error_lower or 'no such file' in error_lower:
                # Verifica novamente se o FFmpeg está disponível
                if not check_ffmpeg():
                    return jsonify({
                        'error': 'FFmpeg não encontrado. Por favor, instale o FFmpeg e adicione ao PATH do sistema.\n\n📥 Instalação no Windows:\n\n1. Chocolatey (Recomendado):\n   choco install ffmpeg\n\n2. Download Manual:\n   - Baixe de: https://www.gyan.dev/ffmpeg/builds/\n   - Extraia e adicione a pasta \\bin ao PATH\n\n3. Após instalar, feche e reabra o terminal\n4. Execute: python verificar_ffmpeg.py\n\n⚠️ IMPORTANTE: Se o FFmpeg já está instalado, reinicie o servidor Flask!'
                    }), 500
                else:
                    # FFmpeg foi encontrado, mas houve outro erro
                    return jsonify({'error': f'Erro na conversão: {error_str[:500]}'}), 500
            
            return jsonify({'error': f'Erro inesperado: {error_str[:500]}'}), 500
        
        
        finally:
            # Remove os arquivos temporários
            try:
                if 'input_path' in locals() and os.path.exists(input_path):
                    os.remove(input_path)
                if 'output_path_abs' in locals() and os.path.exists(output_path_abs):
                    os.remove(output_path_abs)
            except:
                pass
    
    except Exception as e:
        return jsonify({'error': f'Erro no servidor: {str(e)}'}), 500


@app.route('/api/formats', methods=['GET'])
def get_formats():
    """Retorna lista de formatos suportados"""
    return jsonify({
        'input_formats': sorted(list(FORMATOS_ENTRADA)),
        'output_formats': sorted(list(FORMATOS_SAIDA.keys()))
    })

@app.route('/')
def index():
    """Serve a página principal"""
    return send_file('index.html')


@app.route('/style.css')
def style():
    """Serve o arquivo CSS"""
    return send_file('style.css')


@app.route('/script.js')
def script():
    """Serve o arquivo JavaScript"""
    return send_file('script.js')


@app.errorhandler(405)
def method_not_allowed(error):
    """Trata método HTTP não permitido"""
    return jsonify({
        'error': f'Método não permitido. A rota /convert aceita apenas POST. Método usado: {request.method}'
    }), 405

@app.errorhandler(413)
def request_entity_too_large(error):
    """Trata arquivos muito grandes"""
    return jsonify({
        'error': (
            f'Arquivo muito grande para o ambiente atual. '
            f'Tamanho máximo permitido: {MAX_UPLOAD_SIZE_MB}MB.\n\n'
            'Para converter arquivos maiores, execute o app localmente '
            '(python app.py) ou utilize a linha de comando.'
        )
    }), 413


@app.route('/api/config', methods=['GET'])
def get_config():
    """Retorna informações de configuração para o frontend"""
    deploy_hint = os.environ.get(
        'DEPLOYMENT_HINT',
        'Em produção (Vercel), uploads grandes são bloqueados. '
        'Para arquivos maiores, execute localmente: python app.py'
    )
    return jsonify({
        'max_upload_size_mb': MAX_UPLOAD_SIZE_MB,
        'ffmpeg_binary': FFMPEG_BINARY,
        'deployment_hint': deploy_hint
    })


if __name__ == '__main__':
    # Verifica se o FFmpeg está instalado
    if not check_ffmpeg():
        print("=" * 60)
        print("⚠️  ERRO: FFmpeg não encontrado!")
        print("=" * 60)
        print("\nO FFmpeg é necessário para converter os arquivos de áudio.")
        print("\n📥 Como instalar o FFmpeg no Windows:")
        print("\n" + "-" * 60)
        print("OPÇÃO 1: Chocolatey (Recomendado - Mais Fácil)")
        print("-" * 60)
        print("1. Abra o PowerShell como Administrador")
        print("2. Execute: choco install ffmpeg")
        print("3. Feche e reabra o terminal")
        print("\n" + "-" * 60)
        print("OPÇÃO 2: Download Manual")
        print("-" * 60)
        print("1. Baixe de: https://www.gyan.dev/ffmpeg/builds/")
        print("   Escolha: ffmpeg-release-essentials.zip")
        print("2. Extraia o arquivo ZIP (ex: C:\\ffmpeg)")
        print("3. Adicione a pasta 'bin' ao PATH do sistema:")
        print("   a) Pressione Win + X → 'Sistema'")
        print("   b) 'Configurações avançadas do sistema'")
        print("   c) 'Variáveis de Ambiente'")
        print("   d) Em 'Variáveis do sistema', encontre 'Path' → 'Editar'")
        print("   e) 'Novo' → Adicione: C:\\ffmpeg\\bin")
        print("   f) 'OK' em todas as janelas")
        print("4. Feche TODOS os terminais e abra um novo")
        print("\n" + "-" * 60)
        print("OPÇÃO 3: Scoop")
        print("-" * 60)
        print("1. Instale o Scoop: https://scoop.sh/")
        print("2. Execute: scoop install ffmpeg")
        print("\n" + "-" * 60)
        print("Após instalar:")
        print("-" * 60)
        print("1. Feche TODOS os terminais abertos")
        print("2. Abra um novo terminal")
        print("3. Execute: python verificar_ffmpeg.py")
        print("   OU teste: ffmpeg -version")
        print("4. Se funcionar, execute o servidor novamente")
        print("\n" + "=" * 60)
        sys.exit(1)
    
    print("=" * 50)
    print("🎵 Servidor de Conversão de Áudio")
    print("=" * 50)
    print("✓ FFmpeg encontrado e funcionando")
    print("Servidor rodando em: http://localhost:5000")
    print("Pressione Ctrl+C para parar o servidor")
    print("=" * 50)
    
    # Lista todas as rotas registradas para debug
    print("\nRotas registradas:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")
    print("=" * 50)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)

