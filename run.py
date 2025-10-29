#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXECUTE ESTE ARQUIVO PARA RODAR O SISTEMA!
Coloque este arquivo na mesma pasta onde estão:
- AVL Tree - Estrutura Base.py
- grafo_ponderado.py
- sistema_transito.py
- main.py

Depois execute: python run.py
"""

import sys
import os

# Adiciona o diretório atual ao path do Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Agora importa os módulos
print("🚀 Iniciando Sistema de Trânsito Inteligente...\n")

try:
    # Importar com os nomes corretos dos arquivos
    import importlib.util
    
    # Carregar AVL Tree
    spec = importlib.util.spec_from_file_location("avl_tree", "AVL Tree - Estrutura Base.py")
    avl_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(avl_module)
    ArvoreAVL = avl_module.ArvoreAVL
    
    # Carregar Grafo
    from grafo_ponderado import GrafoPonderado
    
    # Carregar Sistema
    from sistema_transito import SistemaTransito
    
    print("✓ Módulos carregados com sucesso!\n")
    
except Exception as e:
    print(f"❌ Erro ao carregar módulos: {e}")
    print("\n📌 Verifique se todos os arquivos estão na mesma pasta:")
    print("   - AVL Tree - Estrutura Base.py")
    print("   - grafo_ponderado.py")
    print("   - sistema_transito.py")
    print("   - run.py (este arquivo)")
    sys.exit(1)

# Resto do código do main.py aqui
import time
from datetime import datetime

# Códigos ANSI para cores
class Cores:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def pausar():
    input(f"\n{Cores.OKCYAN}Pressione ENTER para continuar...{Cores.ENDC}")

def exibir_cabecalho():
    print(f"{Cores.HEADER}{Cores.BOLD}")
    print("=" * 60)
    print(" " * 15 + "SISTEMA DE TRÂNSITO INTELIGENTE")
    print("=" * 60)
    print(f"{Cores.ENDC}")

def sucesso(msg):
    print(f"{Cores.OKGREEN}✓ {msg}{Cores.ENDC}")

def erro(msg):
    print(f"{Cores.FAIL}✗ {msg}{Cores.ENDC}")

def info(msg):
    print(f"{Cores.OKCYAN}→ {msg}{Cores.ENDC}")

def menu_principal():
    print(f"\n{Cores.OKBLUE}┌─────────────────────────────────────────────────┐")
    print("│  1. Gerenciar Malha Viária                     │")
    print("│  2. Gerenciar Eventos de Trânsito              │")
    print("│  3. Cálculo de Rotas                            │")
    print("│  4. Análise e Estatísticas                     │")
    print("│  5. Persistência de Dados                      │")
    print("│  0. Sair                                        │")
    print(f"└─────────────────────────────────────────────────┘{Cores.ENDC}")
    return input("\nEscolha uma opção: ").strip()

def criar_dados_exemplo(sistema):
    """Cria dados de exemplo para demonstração"""
    intersecoes = ['A', 'B', 'C', 'D', 'E', 'F']
    for i in intersecoes:
        sistema.grafo.adicionar_vertice(i)
    
    vias = [
        ('A', 'B', 5.0),
        ('A', 'C', 3.0),
        ('B', 'C', 2.0),
        ('B', 'D', 6.0),
        ('C', 'D', 4.0),
        ('C', 'E', 7.0),
        ('D', 'E', 2.0),
        ('D', 'F', 5.0),
        ('E', 'F', 3.0),
    ]
    
    for origem, destino, peso in vias:
        sistema.grafo.adicionar_aresta(origem, destino, peso)
    
    sistema.registrar_evento('acidente', 'A', 'B', 3.0)
    sistema.registrar_evento('obra', 'C', 'D', 5.0)
    
    sucesso("Dados de exemplo carregados!")
    print("  • 6 interseções (A, B, C, D, E, F)")
    print("  • 9 vias bidirecionais")
    print("  • 2 eventos de trânsito")

def executar_sistema(sistema):
    """Executa o loop principal"""
    while True:
        limpar_tela()
        exibir_cabecalho()
        opcao = menu_principal()
        
        if opcao == '1':
            info("Gerenciar Malha Viária")
            print(sistema.grafo.visualizar_grafo())
            pausar()
        elif opcao == '2':
            info("Eventos Ativos")
            eventos = sistema.avl.listar_todos()
            if not eventos:
                print("Nenhum evento ativo")
            else:
                for ev in eventos:
                    print(f"  ID {ev.id}: {ev.tipo} em {ev.localizacao} (+{ev.impacto}km)")
            pausar()
        elif opcao == '3':
            info("Calcular Rota")
            origem = input("Origem: ").strip().upper()
            destino = input("Destino: ").strip().upper()
            caminho, dist, status = sistema.calcular_rota_otima(origem, destino)
            if status == "OK":
                print(f"\nCaminho: {' → '.join(caminho)}")
                print(f"Distância: {dist:.2f} km")
            else:
                erro(status)
            pausar()
        elif opcao == '4':
            info("Estatísticas")
            stats = sistema.estatisticas()
            print(f"Interseções: {stats['total_intersecoes']}")
            print(f"Vias: {stats['total_vias']}")
            print(f"Eventos: {stats['eventos_ativos']}")
            pausar()
        elif opcao == '5':
            print("\n1. Salvar dados")
            print("2. Carregar dados")
            op = input("Opção: ").strip()
            if op == '1':
                ok, msg = sistema.salvar_dados()
                print(msg)
            elif op == '2':
                ok, msg = sistema.carregar_dados()
                print(msg)
            pausar()
        elif opcao == '0':
            sucesso("Encerrando...")
            break
        else:
            erro("Opção inválida!")
            pausar()

def main():
    limpar_tela()
    exibir_cabecalho()
    
    print(f"\n{Cores.OKCYAN}Inicializando sistema...{Cores.ENDC}")
    
    grafo = GrafoPonderado()
    avl = ArvoreAVL()
    sistema = SistemaTransito(grafo, avl)
    
    print("\n1. Carregar dados salvos")
    print("2. Usar dados de exemplo")
    print("3. Começar vazio")
    
    opcao = input("\nEscolha uma opção: ").strip()
    
    if opcao == '1':
        resultado, msg = sistema.carregar_dados()
        print(f"\n{msg}")
        time.sleep(2)
    elif opcao == '2':
        criar_dados_exemplo(sistema)
        time.sleep(2)
    
    executar_sistema(sistema)
    
    limpar_tela()
    print(f"\n{Cores.HEADER}{'=' * 60}")
    print(" " * 15 + "Obrigado por usar o sistema!")
    print(f"{'=' * 60}{Cores.ENDC}\n")

if __name__ == "__main__":
    main()