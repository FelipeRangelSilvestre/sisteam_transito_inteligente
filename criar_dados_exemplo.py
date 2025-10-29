#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar dados de exemplo do Sistema de Trânsito
Útil para demonstrações e testes
"""

import os


def criar_dados_manaus():
    """
    Cria dados baseados em bairros de Manaus
    Representação simplificada da malha viária
    """
    # Criar diretório
    os.makedirs("dados", exist_ok=True)
    
    # Bairros (vértices)
    bairros = [
        "CENTRO", "ADRIANOPOLIS", "CHAPADA", "ALEIXO",
        "PARQUE10", "FLORES", "CACHOEIRINHA", "PONTA_NEGRA",
        "TARUMA", "COROADO"
    ]
    
    # Vias principais (arestas) com distâncias aproximadas em km
    vias = [
        ("CENTRO", "ADRIANOPOLIS", 3.5),
        ("CENTRO", "CHAPADA", 4.2),
        ("CENTRO", "CACHOEIRINHA", 5.8),
        ("ADRIANOPOLIS", "PARQUE10", 2.1),
        ("ADRIANOPOLIS", "FLORES", 3.0),
        ("CHAPADA", "ALEIXO", 2.5),
        ("ALEIXO", "PARQUE10", 1.8),
        ("PARQUE10", "FLORES", 2.3),
        ("FLORES", "CACHOEIRINHA", 4.5),
        ("CACHOEIRINHA", "PONTA_NEGRA", 8.2),
        ("ALEIXO", "TARUMA", 6.5),
        ("TARUMA", "COROADO", 4.0),
        ("COROADO", "PONTA_NEGRA", 7.8),
    ]
    
    # Eventos de trânsito
    eventos = [
        # id, timestamp, tipo, localizacao, impacto
        (1, 1698768000, "obra", "CENTRO-ADRIANOPOLIS", 2.0),
        (2, 1698769800, "acidente", "CACHOEIRINHA-PONTA_NEGRA", 3.5),
        (3, 1698771600, "congestionamento", "PARQUE10-FLORES", 1.5),
    ]
    
    # Salvar grafo
    with open("dados/grafo.txt", 'w', encoding='utf-8') as f:
        f.write(f"{len(bairros)}\n")
        f.write(" ".join(bairros) + "\n")
        f.write(f"{len(vias)}\n")
        for origem, destino, peso in vias:
            f.write(f"{origem} {destino} {peso}\n")
    
    # Salvar eventos
    with open("dados/eventos.txt", 'w', encoding='utf-8') as f:
        f.write(f"{len(eventos)}\n")
        for id_ev, timestamp, tipo, loc, impacto in eventos:
            f.write(f"{id_ev} {timestamp} {tipo} {loc} {impacto}\n")
    
    print("✓ Dados de exemplo (Manaus) criados com sucesso!")
    print(f"  • {len(bairros)} bairros")
    print(f"  • {len(vias)} vias")
    print(f"  • {len(eventos)} eventos de trânsito")
    print("\nArquivos criados:")
    print("  - dados/grafo.txt")
    print("  - dados/eventos.txt")


def criar_dados_simples():
    """
    Cria dados simples para testes básicos
    """
    os.makedirs("dados", exist_ok=True)
    
    vertices = ["A", "B", "C", "D", "E", "F"]
    
    arestas = [
        ("A", "B", 5.0),
        ("A", "C", 3.0),
        ("B", "C", 2.0),
        ("B", "D", 6.0),
        ("C", "D", 4.0),
        ("C", "E", 7.0),
        ("D", "E", 2.0),
        ("D", "F", 5.0),
        ("E", "F", 3.0),
    ]
    
    eventos = [
        (1, 1698768000, "acidente", "A-B", 3.0),
        (2, 1698769800, "obra", "C-D", 5.0),
    ]
    
    with open("dados/grafo.txt", 'w', encoding='utf-8') as f:
        f.write(f"{len(vertices)}\n")
        f.write(" ".join(vertices) + "\n")
        f.write(f"{len(arestas)}\n")
        for origem, destino, peso in arestas:
            f.write(f"{origem} {destino} {peso}\n")
    
    with open("dados/eventos.txt", 'w', encoding='utf-8') as f:
        f.write(f"{len(eventos)}\n")
        for id_ev, timestamp, tipo, loc, impacto in eventos:
            f.write(f"{id_ev} {timestamp} {tipo} {loc} {impacto}\n")
    
    print("✓ Dados simples criados com sucesso!")
    print(f"  • {len(vertices)} vértices")
    print(f"  • {len(arestas)} arestas")
    print(f"  • {len(eventos)} eventos")


def criar_dados_complexos():
    """
    Cria dados mais complexos para testes de performance
    """
    os.makedirs("dados", exist_ok=True)
    
    # Grid 10x10
    n = 10
    vertices = []
    arestas = []
    
    for i in range(n):
        for j in range(n):
            vertices.append(f"P{i}{j}")
            
            # Conectar com vizinhos
            if i > 0:
                peso = round(1.0 + (i+j) * 0.1, 1)
                arestas.append((f"P{i}{j}", f"P{i-1}{j}", peso))
            
            if j > 0:
                peso = round(1.0 + (i+j) * 0.1, 1)
                arestas.append((f"P{i}{j}", f"P{i}{j-1}", peso))
    
    # Alguns eventos aleatórios
    eventos = [
        (1, 1698768000, "obra", "P00-P01", 2.0),
        (2, 1698769000, "acidente", "P55-P65", 3.0),
        (3, 1698770000, "congestionamento", "P99-P89", 1.5),
    ]
    
    with open("dados/grafo.txt", 'w', encoding='utf-8') as f:
        f.write(f"{len(vertices)}\n")
        f.write(" ".join(vertices) + "\n")
        f.write(f"{len(arestas)}\n")
        for origem, destino, peso in arestas:
            f.write(f"{origem} {destino} {peso}\n")
    
    with open("dados/eventos.txt", 'w', encoding='utf-8') as f:
        f.write(f"{len(eventos)}\n")
        for id_ev, timestamp, tipo, loc, impacto in eventos:
            f.write(f"{id_ev} {timestamp} {tipo} {loc} {impacto}\n")
    
    print("✓ Dados complexos criados com sucesso!")
    print(f"  • {len(vertices)} vértices (grid 10x10)")
    print(f"  • {len(arestas)} arestas")
    print(f"  • {len(eventos)} eventos")


def menu():
    """Menu de opções"""
    print("\n" + "="*60)
    print(" "*15 + "CRIAR DADOS DE EXEMPLO")
    print("="*60)
    print("\n1. Dados baseados em Manaus (recomendado)")
    print("2. Dados simples (A-F)")
    print("3. Dados complexos (grid 10x10)")
    print("0. Sair")
    print()
    
    opcao = input("Escolha uma opção: ").strip()
    
    if opcao == '1':
        criar_dados_manaus()
    elif opcao == '2':
        criar_dados_simples()
    elif opcao == '3':
        criar_dados_complexos()
    elif opcao == '0':
        print("\nSaindo...")
        return
    else:
        print("\n✗ Opção inválida!")
    
    print("\n✓ Agora você pode executar o sistema principal:")
    print("  python src/main.py")
    print("\n  Escolha a opção '1. Carregar dados salvos'\n")


if __name__ == "__main__":
    menu()
