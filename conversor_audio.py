#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversor de Áudio Universal
Converte arquivos de áudio entre todos os formatos suportados
"""

import os
import sys
import argparse
from pathlib import Path

try:
    import ffmpeg
except ImportError:
    print("Erro: Biblioteca ffmpeg-python não encontrada.")
    print("Instale com: pip install ffmpeg-python")
    sys.exit(1)

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
    'mp3': {'acodec': 'libmp3lame', 'ext': 'mp3'},
    'wav': {'acodec': 'pcm_s16le', 'ext': 'wav'},
    'flac': {'acodec': 'flac', 'ext': 'flac'},
    'ogg': {'acodec': 'libvorbis', 'ext': 'ogg'},
    'aac': {'acodec': 'aac', 'ext': 'aac'},
    'm4a': {'acodec': 'aac', 'ext': 'm4a'},
    'opus': {'acodec': 'libopus', 'ext': 'opus'},
    'wma': {'acodec': 'wmav2', 'ext': 'wma'},
    'aiff': {'acodec': 'pcm_s16be', 'ext': 'aiff'},
    'aif': {'acodec': 'pcm_s16be', 'ext': 'aif'},
    'ac3': {'acodec': 'ac3', 'ext': 'ac3'},
    'mp2': {'acodec': 'mp2', 'ext': 'mp2'},
    'amr': {'acodec': 'libopencore_amrnb', 'ext': 'amr'},
    'webm': {'acodec': 'libopus', 'ext': 'webm'}
}

def detectar_formato(arquivo):
    """Detecta o formato do arquivo pela extensão"""
    ext = Path(arquivo).suffix.lower().lstrip('.')
    return ext if ext in FORMATOS_ENTRADA else None


def converter_audio(arquivo_entrada, arquivo_saida=None, formato_saida='m4a', qualidade='192k'):
    """
    Converte um arquivo de áudio para outro formato
    
    Args:
        arquivo_entrada: Caminho do arquivo de entrada
        arquivo_saida: Caminho do arquivo de saída (opcional)
        formato_saida: Formato de saída (mp3, wav, flac, ogg, aac, m4a, opus, wma, etc.)
        qualidade: Bitrate de áudio (padrão: 192k) - apenas para formatos comprimidos
    
    Returns:
        True se a conversão foi bem-sucedida, False caso contrário
    """
    # Verifica se o arquivo de entrada existe
    if not os.path.exists(arquivo_entrada):
        print(f"Erro: Arquivo não encontrado: {arquivo_entrada}")
        return False
    
    # Normaliza o formato de saída
    formato_saida = formato_saida.lower().lstrip('.')
    
    # Verifica se o formato de saída é suportado
    if formato_saida not in FORMATOS_SAIDA:
        print(f"Erro: Formato de saída '{formato_saida}' não suportado.")
        print(f"Formatos suportados: {', '.join(sorted(FORMATOS_SAIDA.keys()))}")
        return False
    
    # Detecta formato de entrada
    formato_entrada = detectar_formato(arquivo_entrada)
    if formato_entrada is None:
        print(f"Aviso: Formato de entrada não reconhecido. Tentando converter mesmo assim...")
    
    # Se não foi especificado arquivo de saída, cria um baseado no nome do arquivo de entrada
    if arquivo_saida is None:
        arquivo_base = Path(arquivo_entrada)
        arquivo_saida = arquivo_base.with_suffix(f'.{FORMATOS_SAIDA[formato_saida]["ext"]}')
    
    # Garante que o diretório de saída existe
    os.makedirs(os.path.dirname(arquivo_saida) if os.path.dirname(arquivo_saida) else '.', exist_ok=True)
    
    try:
        print(f"Convertendo: {arquivo_entrada} ({formato_entrada or 'desconhecido'}) -> {arquivo_saida} ({formato_saida})")
        
        # Carrega o arquivo de entrada
        stream = ffmpeg.input(arquivo_entrada)
        
        # Obtém configurações do formato de saída
        config = FORMATOS_SAIDA[formato_saida]
        acodec = config['acodec']
        
        # Prepara parâmetros de saída
        output_params = {
            'acodec': acodec,
            'ac': 2,  # 2 canais (estéreo)
            'ar': 44100  # Sample rate de 44.1kHz
        }
        
        # Adiciona bitrate apenas para formatos comprimidos (não para WAV, FLAC lossless, etc.)
        formatos_sem_bitrate = {'wav', 'aiff', 'aif', 'flac'}
        if formato_saida not in formatos_sem_bitrate:
            output_params['audio_bitrate'] = qualidade
        
        # Para FLAC, usa compressão ao invés de bitrate
        if formato_saida == 'flac':
            output_params['compression_level'] = 5
        
        # Extrai o áudio e converte para o formato desejado
        stream = ffmpeg.output(stream, arquivo_saida, **output_params)
        
        # Executa a conversão (overwrite_output=True sobrescreve arquivos existentes)
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        
        print(f"✓ Conversão concluída: {arquivo_saida}")
        return True
        
    except ffmpeg.Error as e:
        print(f"Erro durante a conversão: {e.stderr.decode() if e.stderr else str(e)}")
        return False
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        return False


def converter_diretorio(diretorio, formato_saida='m4a', qualidade='192k'):
    """
    Converte todos os arquivos de áudio de um diretório para o formato especificado
    
    Args:
        diretorio: Caminho do diretório
        formato_saida: Formato de saída (mp3, wav, flac, ogg, aac, m4a, etc.)
        qualidade: Bitrate de áudio (padrão: 192k)
    """
    diretorio_path = Path(diretorio)
    
    if not diretorio_path.exists():
        print(f"Erro: Diretório não encontrado: {diretorio}")
        return
    
    # Busca todos os arquivos de áudio no diretório
    arquivos_audio = []
    for ext in FORMATOS_ENTRADA:
        arquivos_audio.extend(diretorio_path.glob(f'*.{ext}'))
        arquivos_audio.extend(diretorio_path.glob(f'*.{ext.upper()}'))
    
    if not arquivos_audio:
        print(f"Nenhum arquivo de áudio encontrado em: {diretorio}")
        print(f"Formatos suportados: {', '.join(sorted(FORMATOS_ENTRADA))}")
        return
    
    print(f"Encontrados {len(arquivos_audio)} arquivo(s) de áudio")
    print("-" * 50)
    
    sucessos = 0
    falhas = 0
    
    for arquivo in arquivos_audio:
        if converter_audio(str(arquivo), formato_saida=formato_saida, qualidade=qualidade):
            sucessos += 1
        else:
            falhas += 1
        print()
    
    print("-" * 50)
    print(f"Conversão concluída: {sucessos} sucesso(s), {falhas} falha(s)")


def main():
    formatos_saida_str = ', '.join(sorted(FORMATOS_SAIDA.keys()))
    
    parser = argparse.ArgumentParser(
        description='Conversor de Áudio Universal - Suporta todos os formatos de áudio',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Formatos de saída suportados: {formatos_saida_str}

Exemplos:
  # Converter um arquivo único (detecta formato de saída pela extensão)
  python conversor_audio.py arquivo.mp3 -o saida.wav
  
  # Converter para formato específico
  python conversor_audio.py entrada.mp4 -f m4a
  
  # Converter todos os arquivos de áudio de um diretório
  python conversor_audio.py -d pasta/ -f mp3
  
  # Especificar qualidade de áudio
  python conversor_audio.py arquivo.wav -f mp3 -q 320k
        """
    )
    
    parser.add_argument(
        'entrada',
        nargs='?',
        help='Arquivo de áudio de entrada ou diretório (use -d para diretório)'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='saida',
        help='Arquivo de saída (opcional, formato detectado pela extensão)'
    )
    
    parser.add_argument(
        '-f', '--formato',
        dest='formato_saida',
        default='m4a',
        help=f'Formato de saída (padrão: m4a). Formatos: {formatos_saida_str}'
    )
    
    parser.add_argument(
        '-d', '--diretorio',
        action='store_true',
        help='Processar todos os arquivos de áudio do diretório especificado'
    )
    
    parser.add_argument(
        '-q', '--qualidade',
        default='192k',
        help='Bitrate de áudio (padrão: 192k). Exemplos: 128k, 192k, 256k, 320k'
    )
    
    args = parser.parse_args()
    
    # Verifica se foi fornecido um argumento
    if not args.entrada:
        parser.print_help()
        sys.exit(1)
    
    # Se foi especificado arquivo de saída, tenta detectar o formato pela extensão
    if args.saida:
        formato_detectado = detectar_formato(args.saida)
        if formato_detectado and formato_detectado in FORMATOS_SAIDA:
            args.formato_saida = formato_detectado
    
    # Verifica se FFmpeg está instalado no sistema
    try:
        if os.path.exists(args.entrada):
            ffmpeg.probe(args.entrada)
    except:
        print("Aviso: Verifique se o FFmpeg está instalado no sistema.")
        print("Download: https://ffmpeg.org/download.html")
        print()
    
    # Processa o diretório ou arquivo único
    if args.diretorio:
        converter_diretorio(args.entrada, formato_saida=args.formato_saida, qualidade=args.qualidade)
    else:
        converter_audio(args.entrada, args.saida, formato_saida=args.formato_saida, qualidade=args.qualidade)


if __name__ == '__main__':
    main()

