#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor Flask para conversão de áudio MP4 para M4A
"""

import io
import os
import sys
import subprocess
import tempfile
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import ffmpeg

app = Flask(__name__)
CORS(app)

# Configurações
FFMPEG_BINARY = os.environ.get('FFMPEG_PATH', 'ffmpeg')
os.environ['FFMPEG_BINARY'] = FFMPEG_BINARY

BASE_TEMP_DIR = os.path.join(tempfile.gettempdir(), 'audio-converter')
UPLOAD_FOLDER = os.path.join(BASE_TEMP_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_TEMP_DIR, 'outputs')
ALLOWED_EXTENSIONS = {'mp4'}

# Cria os diretórios se não existirem
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def check_ffmpeg():
    """Verifica se o FFmpeg está instalado e acessível"""
    try:
        subprocess.run(
            [FFMPEG_BINARY, '-version'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return False


def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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


@app.route('/convert', methods=['POST'])
def convert():
    """Converte arquivo MP4 para M4A"""
    try:
        # Verifica se o arquivo foi enviado
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        quality = request.form.get('quality', '192k')
        
        # Verifica se o arquivo foi selecionado
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        # Verifica se é um arquivo permitido
        if not allowed_file(file.filename):
            return jsonify({'error': 'Formato de arquivo não permitido. Use arquivos MP4.'}), 400
        
        # Salva o arquivo temporariamente
        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(input_path)
        
        # Gera o nome do arquivo de saída
        output_filename = os.path.splitext(file.filename)[0] + '.m4a'
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        try:
            # Converte o arquivo
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.output(
                stream,
                output_path,
                acodec='aac',
                audio_bitrate=quality,
                ac=2,  # 2 canais (estéreo)
                ar=44100  # Sample rate de 44.1kHz
            )
            
            # Executa a conversão
            ffmpeg.run(stream, overwrite_output=True, quiet=True)

            # Lê o arquivo convertido da pasta temporária
            with open(output_path, 'rb') as converted_file:
                file_bytes = io.BytesIO(converted_file.read())

            file_bytes.seek(0)

            response = send_file(
                file_bytes,
                as_attachment=True,
                download_name=output_filename,
                mimetype='audio/mp4'
            )

            response.headers['Cache-Control'] = 'no-store'

            return response
        
        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            # Verifica se o erro é relacionado ao FFmpeg não encontrado
            if 'ffmpeg' in error_message.lower() or 'not found' in error_message.lower() or 'WinError 2' in str(e):
                return jsonify({
                    'error': 'FFmpeg não encontrado. Por favor, instale o FFmpeg e adicione ao PATH do sistema.\n\nWindows: Baixe de https://ffmpeg.org/download.html ou use: choco install ffmpeg'
                }), 500
            return jsonify({'error': f'Erro na conversão: {error_message}'}), 500
        
        except FileNotFoundError as e:
            if 'ffmpeg' in str(e).lower() or 'WinError 2' in str(e):
                return jsonify({
                    'error': 'FFmpeg não encontrado. Por favor, instale o FFmpeg e adicione ao PATH do sistema.\n\nWindows: Baixe de https://ffmpeg.org/download.html ou use: choco install ffmpeg'
                }), 500
            return jsonify({'error': f'Erro: {str(e)}'}), 500
        
        except OSError as e:
            if 'WinError 2' in str(e) or 'not found' in str(e).lower():
                return jsonify({
                    'error': 'FFmpeg não encontrado. Por favor, instale o FFmpeg e adicione ao PATH do sistema.\n\nWindows: Baixe de https://ffmpeg.org/download.html ou use: choco install ffmpeg'
                }), 500
            return jsonify({'error': f'Erro no sistema: {str(e)}'}), 500
        
        except Exception as e:
            error_str = str(e)
            if 'WinError 2' in error_str or 'ffmpeg' in error_str.lower() or 'not found' in error_str.lower():
                return jsonify({
                    'error': 'FFmpeg não encontrado. Por favor, instale o FFmpeg e adicione ao PATH do sistema.\n\nWindows: Baixe de https://ffmpeg.org/download.html ou use: choco install ffmpeg'
                }), 500
            return jsonify({'error': f'Erro inesperado: {error_str}'}), 500
        
        finally:
            # Remove os arquivos temporários
            try:
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
            except:
                pass
    
    except Exception as e:
        return jsonify({'error': f'Erro no servidor: {str(e)}'}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Trata arquivos muito grandes"""
    return jsonify({'error': 'Arquivo muito grande. Tamanho máximo: 100MB'}), 413


if __name__ == '__main__':
    # Verifica se o FFmpeg está instalado
    if not check_ffmpeg():
        print("=" * 60)
        print("⚠️  ERRO: FFmpeg não encontrado!")
        print("=" * 60)
        print("\nO FFmpeg é necessário para converter os arquivos de áudio.")
        print("\n📥 Como instalar o FFmpeg no Windows:")
        print("   1. Baixe de: https://ffmpeg.org/download.html")
        print("   2. Extraia o arquivo ZIP")
        print("   3. Adicione a pasta 'bin' ao PATH do sistema:")
        print("      - Pressione Win + X e escolha 'Sistema'")
        print("      - Clique em 'Configurações avançadas do sistema'")
        print("      - Clique em 'Variáveis de Ambiente'")
        print("      - Em 'Variáveis do sistema', encontre 'Path' e clique em 'Editar'")
        print("      - Clique em 'Novo' e adicione o caminho da pasta 'bin' do FFmpeg")
        print("      - Exemplo: C:\\ffmpeg\\bin")
        print("\n   OU use o Chocolatey (se tiver instalado):")
        print("      choco install ffmpeg")
        print("\n   4. Reinicie o terminal e execute este script novamente")
        print("\n" + "=" * 60)
        sys.exit(1)
    
    # Configura o tamanho máximo de upload (100MB)
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
    
    print("=" * 50)
    print("🎵 Servidor de Conversão de Áudio")
    print("=" * 50)
    print("✓ FFmpeg encontrado e funcionando")
    print("Servidor rodando em: http://localhost:5000")
    print("Pressione Ctrl+C para parar o servidor")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

