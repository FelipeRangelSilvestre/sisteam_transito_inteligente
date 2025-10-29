#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir a estrutura do projeto e imports
Execute este script na raiz do projeto antes de rodar o main.py
"""

import os
import shutil

def criar_estrutura():
    """Cria a estrutura correta de pastas"""
    print("🔧 Corrigindo estrutura do projeto...\n")
    
    # Criar pasta src se não existir
    if not os.path.exists('src'):
        os.makedirs('src')
        print("✓ Pasta 'src' criada")
    
    # Criar __init__.py na pasta src
    init_path = os.path.join('src', '__init__.py')
    if not os.path.exists(init_path):
        with open(init_path, 'w', encoding='utf-8') as f:
            f.write('# Módulo do Sistema de Trânsito Inteligente\n')
        print("✓ Arquivo '__init__.py' criado em src/")
    
    # Lista de arquivos que devem estar em src/
    arquivos_src = [
        'avl_tree.py',
        'grafo_ponderado.py', 
        'sistema_transito.py',
        'main.py',
        'test_sistema.py',
        'criar_dados_exemplo.py'
    ]
    
    # Mover arquivos para src/ se estiverem na raiz
    movidos = 0
    for arquivo in arquivos_src:
        if os.path.exists(arquivo) and not os.path.exists(os.path.join('src', arquivo)):
            shutil.move(arquivo, os.path.join('src', arquivo))
            print(f"✓ '{arquivo}' movido para src/")
            movidos += 1
    
    if movidos == 0:
        print("✓ Arquivos já estão na estrutura correta")
    
    # Criar pasta dados se não existir
    if not os.path.exists('dados'):
        os.makedirs('dados')
        print("✓ Pasta 'dados' criada")
    
    print("\n✅ Estrutura corrigida com sucesso!")
    print("\nEstrutura atual:")
    print("├── src/")
    print("│   ├── __init__.py")
    print("│   ├── avl_tree.py")
    print("│   ├── grafo_ponderado.py")
    print("│   ├── sistema_transito.py")
    print("│   ├── main.py")
    print("│   ├── test_sistema.py")
    print("│   └── criar_dados_exemplo.py")
    print("└── dados/")
    print("\n📌 Agora execute: python src/main.py")


if __name__ == "__main__":
    criar_estrutura()