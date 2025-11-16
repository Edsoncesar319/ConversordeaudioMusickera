#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar se o FFmpeg está instalado e acessível
"""

import subprocess
import sys
import os

def verificar_ffmpeg():
    """Verifica se o FFmpeg está instalado"""
    try:
        resultado = subprocess.run(
            ['ffmpeg', '-version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        # Extrai a versão do FFmpeg
        primeira_linha = resultado.stdout.split('\n')[0]
        print("=" * 60)
        print("✓ FFmpeg está instalado e funcionando!")
        print("=" * 60)
        print(f"\n{primeira_linha}\n")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as e:
        print("=" * 60)
        print("⚠️  FFmpeg NÃO encontrado!")
        print("=" * 60)
        print("\nO FFmpeg é necessário para converter arquivos de áudio.")
        print("\n📥 Como instalar o FFmpeg no Windows:")
        print("\n" + "-" * 60)
        print("OPÇÃO 1: Download Manual")
        print("-" * 60)
        print("1. Acesse: https://www.gyan.dev/ffmpeg/builds/")
        print("   (ou https://ffmpeg.org/download.html)")
        print("2. Baixe 'ffmpeg-release-essentials.zip'")
        print("3. Extraia o arquivo ZIP em uma pasta (ex: C:\\ffmpeg)")
        print("4. Adicione ao PATH:")
        print("   a) Pressione Win + X e escolha 'Sistema'")
        print("   b) Clique em 'Configurações avançadas do sistema'")
        print("   c) Clique em 'Variáveis de Ambiente'")
        print("   d) Em 'Variáveis do sistema', encontre 'Path'")
        print("   e) Clique em 'Editar' → 'Novo'")
        print("   f) Adicione: C:\\ffmpeg\\bin")
        print("   g) Clique em 'OK' em todas as janelas")
        print("\n" + "-" * 60)
        print("OPÇÃO 2: Chocolatey (Recomendado)")
        print("-" * 60)
        print("1. Instale o Chocolatey (se não tiver):")
        print("   https://chocolatey.org/install")
        print("2. Execute no PowerShell (como Administrador):")
        print("   choco install ffmpeg")
        print("\n" + "-" * 60)
        print("OPÇÃO 3: Scoop")
        print("-" * 60)
        print("1. Instale o Scoop (se não tiver):")
        print("   https://scoop.sh/")
        print("2. Execute no PowerShell:")
        print("   scoop install ffmpeg")
        print("\n" + "-" * 60)
        print("Após instalar:")
        print("-" * 60)
        print("1. Feche TODOS os terminais abertos")
        print("2. Abra um novo terminal")
        print("3. Execute: ffmpeg -version")
        print("4. Se funcionar, execute o servidor novamente")
        print("\n" + "=" * 60)
        return False

if __name__ == '__main__':
    verificar_ffmpeg()

