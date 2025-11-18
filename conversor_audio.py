#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversor de Áudio MP4 para M4A
Converte arquivos de áudio MP4 para formato M4A
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


def converter_mp4_para_m4a(arquivo_entrada, arquivo_saida=None, qualidade='192k'):
    """
    Converte um arquivo MP4 para M4A
    
    Args:
        arquivo_entrada: Caminho do arquivo MP4 de entrada
        arquivo_saida: Caminho do arquivo M4A de saída (opcional)
        qualidade: Bitrate de áudio (padrão: 192k)
    
    Returns:
        True se a conversão foi bem-sucedida, False caso contrário
    """
    # Verifica se o arquivo de entrada existe
    if not os.path.exists(arquivo_entrada):
        print(f"Erro: Arquivo não encontrado: {arquivo_entrada}")
        return False
    
    # Se não foi especificado arquivo de saída, cria um baseado no nome do arquivo de entrada
    if arquivo_saida is None:
        arquivo_base = Path(arquivo_entrada)
        arquivo_saida = arquivo_base.with_suffix('.m4a')
    
    # Garante que o diretório de saída existe
    os.makedirs(os.path.dirname(arquivo_saida) if os.path.dirname(arquivo_saida) else '.', exist_ok=True)
    
    try:
        print(f"Convertendo: {arquivo_entrada} -> {arquivo_saida}")
        
        # Carrega o arquivo de entrada
        stream = ffmpeg.input(arquivo_entrada)
        
        # Extrai o áudio e converte para M4A (AAC)
        stream = ffmpeg.output(
            stream,
            arquivo_saida,
            acodec='aac',
            audio_bitrate=qualidade,
            ac=2,  # 2 canais (estéreo)
            ar=44100  # Sample rate de 44.1kHz
        )
        
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


def converter_diretorio(diretorio, qualidade='192k'):
    """
    Converte todos os arquivos MP4 de um diretório para M4A
    
    Args:
        diretorio: Caminho do diretório
        qualidade: Bitrate de áudio (padrão: 192k)
    """
    diretorio_path = Path(diretorio)
    
    if not diretorio_path.exists():
        print(f"Erro: Diretório não encontrado: {diretorio}")
        return
    
    # Busca todos os arquivos MP4 no diretório
    arquivos_mp4 = list(diretorio_path.glob('*.mp4'))
    
    if not arquivos_mp4:
        print(f"Nenhum arquivo MP4 encontrado em: {diretorio}")
        return
    
    print(f"Encontrados {len(arquivos_mp4)} arquivo(s) MP4")
    print("-" * 50)
    
    sucessos = 0
    falhas = 0
    
    for arquivo in arquivos_mp4:
        if converter_mp4_para_m4a(str(arquivo), qualidade=qualidade):
            sucessos += 1
        else:
            falhas += 1
        print()
    
    print("-" * 50)
    print(f"Conversão concluída: {sucessos} sucesso(s), {falhas} falha(s)")


def main():
    parser = argparse.ArgumentParser(
        description='Conversor de Áudio MP4 para M4A',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Converter um arquivo único
  python conversor_audio.py arquivo.mp4
  
  # Converter um arquivo com nome de saída específico
  python conversor_audio.py entrada.mp4 -o saida.m4a
  
  # Converter todos os MP4 de um diretório
  python conversor_audio.py -d pasta/
  
  # Especificar qualidade de áudio
  python conversor_audio.py arquivo.mp4 -q 256k
        """
    )
    
    parser.add_argument(
        'entrada',
        nargs='?',
        help='Arquivo MP4 de entrada ou diretório (use -d para diretório)'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='saida',
        help='Arquivo M4A de saída (opcional)'
    )
    
    parser.add_argument(
        '-d', '--diretorio',
        action='store_true',
        help='Processar todos os arquivos MP4 do diretório especificado'
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
    
    # Verifica se FFmpeg está instalado no sistema
    try:
        ffmpeg.probe(args.entrada if os.path.exists(args.entrada) else 'test')
    except:
        print("Aviso: Verifique se o FFmpeg está instalado no sistema.")
        print("Download: https://ffmpeg.org/download.html")
        print()
    
    # Processa o diretório ou arquivo único
    if args.diretorio:
        converter_diretorio(args.entrada, qualidade=args.qualidade)
    else:
        converter_mp4_para_m4a(args.entrada, args.saida, qualidade=args.qualidade)


if __name__ == '__main__':
    main()

