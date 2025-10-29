#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Trânsito Inteligente
Estruturas: Grafo Ponderado + Árvore AVL
"""

import os
import time
from datetime import datetime

# Importar módulos do sistema
from avl_tree import ArvoreAVL
from grafo_ponderado import GrafoPonderado
from sistema_transito import SistemaTransito

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
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def pausar():
    """Pausa a execução até pressionar Enter"""
    input(f"\n{Cores.OKCYAN}Pressione ENTER para continuar...{Cores.ENDC}")

def exibir_cabecalho():
    """Exibe o cabeçalho do sistema"""
    print(f"{Cores.HEADER}{Cores.BOLD}")
    print("=" * 60)
    print(" " * 15 + "SISTEMA DE TRÂNSITO INTELIGENTE")
    print("=" * 60)
    print(f"{Cores.ENDC}")

def sucesso(msg):
    """Exibe mensagem de sucesso"""
    print(f"{Cores.OKGREEN}✓ {msg}{Cores.ENDC}")

def erro(msg):
    """Exibe mensagem de erro"""
    print(f"{Cores.FAIL}✗ {msg}{Cores.ENDC}")

def aviso(msg):
    """Exibe mensagem de aviso"""
    print(f"{Cores.WARNING}⚠ {msg}{Cores.ENDC}")

def info(msg):
    """Exibe mensagem informativa"""
    print(f"{Cores.OKCYAN}→ {msg}{Cores.ENDC}")

def menu_principal():
    """Menu principal do sistema"""
    print(f"\n{Cores.OKBLUE}┌─────────────────────────────────────────────────┐")
    print("│  1. Gerenciar Malha Viária                     │")
    print("│  2. Gerenciar Eventos de Trânsito              │")
    print("│  3. Cálculo de Rotas                            │")
    print("│  4. Análise e Estatísticas                     │")
    print("│  5. Persistência de Dados                      │")
    print("│  0. Sair                                        │")
    print(f"└─────────────────────────────────────────────────┘{Cores.ENDC}")
    return input("\nEscolha uma opção: ").strip()

def menu_malha_viaria():
    """Submenu para gerenciar a malha viária"""
    print(f"\n{Cores.OKBLUE}┌─────────────────────────────────────────────────┐")
    print("│  GERENCIAR MALHA VIÁRIA                         │")
    print("├─────────────────────────────────────────────────┤")
    print("│  1. Adicionar interseção                        │")
    print("│  2. Adicionar via                               │")
    print("│  3. Remover via                                 │")
    print("│  4. Visualizar mapa                             │")
    print("│  0. Voltar                                      │")
    print(f"└─────────────────────────────────────────────────┘{Cores.ENDC}")
    return input("\nEscolha uma opção: ").strip()

def menu_eventos():
    """Submenu para gerenciar eventos"""
    print(f"\n{Cores.OKBLUE}┌─────────────────────────────────────────────────┐")
    print("│  GERENCIAR EVENTOS DE TRÂNSITO                  │")
    print("├─────────────────────────────────────────────────┤")
    print("│  1. Registrar novo evento                       │")
    print("│  2. Remover evento                              │")
    print("│  3. Listar eventos ativos                       │")
    print("│  4. Buscar evento por ID                        │")
    print("│  0. Voltar                                      │")
    print(f"└─────────────────────────────────────────────────┘{Cores.ENDC}")
    return input("\nEscolha uma opção: ").strip()

def menu_rotas():
    """Submenu para cálculo de rotas"""
    print(f"\n{Cores.OKBLUE}┌─────────────────────────────────────────────────┐")
    print("│  CÁLCULO DE ROTAS                               │")
    print("├─────────────────────────────────────────────────┤")
    print("│  1. Calcular rota ótima                         │")
    print("│  2. Comparar rotas (com/sem eventos)            │")
    print("│  3. Identificar eventos na rota                 │")
    print("│  0. Voltar                                      │")
    print(f"└─────────────────────────────────────────────────┘{Cores.ENDC}")
    return input("\nEscolha uma opção: ").strip()

def gerenciar_malha_viaria(sistema):
    """Gerencia operações da malha viária"""
    while True:
        limpar_tela()
        exibir_cabecalho()
        opcao = menu_malha_viaria()
        
        if opcao == '1':
            info("ADICIONAR INTERSEÇÃO")
            nome = input("Nome da interseção: ").strip().upper()
            if nome:
                sistema.grafo.adicionar_vertice(nome)
                sucesso(f"Interseção '{nome}' adicionada com sucesso!")
            else:
                erro("Nome inválido!")
            pausar()
            
        elif opcao == '2':
            info("ADICIONAR VIA (BIDIRECIONAL)")
            origem = input("Interseção de origem: ").strip().upper()
            destino = input("Interseção de destino: ").strip().upper()
            try:
                peso = float(input("Distância (km): ").strip())
                if peso > 0:
                    sistema.grafo.adicionar_aresta(origem, destino, peso)
                    sucesso(f"Via {origem} <-> {destino} adicionada!")
                else:
                    erro("Distância deve ser positiva!")
            except ValueError:
                erro("Distância inválida!")
            pausar()
            
        elif opcao == '3':
            info("REMOVER VIA")
            origem = input("Interseção de origem: ").strip().upper()
            destino = input("Interseção de destino: ").strip().upper()
            if sistema.grafo.remover_aresta(origem, destino):
                sucesso(f"Via {origem} <-> {destino} removida!")
            else:
                erro("Via não encontrada!")
            pausar()
            
        elif opcao == '4':
            print("\n")
            print(sistema.grafo.visualizar_grafo())
            pausar()
            
        elif opcao == '0':
            break
        else:
            erro("Opção inválida!")
            pausar()

def gerenciar_eventos(sistema):
    """Gerencia eventos de trânsito"""
    while True:
        limpar_tela()
        exibir_cabecalho()
        opcao = menu_eventos()
        
        if opcao == '1':
            info("REGISTRAR NOVO EVENTO")
            print(f"{Cores.WARNING}Tipos: acidente, obra, congestionamento{Cores.ENDC}")
            tipo = input("Tipo de evento: ").strip().lower()
            
            if tipo not in ['acidente', 'obra', 'congestionamento']:
                erro("Tipo inválido!")
                pausar()
                continue
            
            origem = input("Via - Origem: ").strip().upper()
            destino = input("Via - Destino: ").strip().upper()
            
            try:
                impacto = float(input("Impacto no tempo (km adicional): ").strip())
                if impacto > 0:
                    resultado, msg = sistema.registrar_evento(tipo, origem, destino, impacto)
                    if resultado:
                        sucesso(msg)
                    else:
                        erro(msg)
                else:
                    erro("Impacto deve ser positivo!")
            except ValueError:
                erro("Impacto inválido!")
            pausar()
            
        elif opcao == '2':
            info("REMOVER EVENTO")
            try:
                id_evento = int(input("ID do evento: ").strip())
                resultado, msg = sistema.remover_evento(id_evento)
                if resultado:
                    sucesso(msg)
                else:
                    erro(msg)
            except ValueError:
                erro("ID inválido!")
            pausar()
            
        elif opcao == '3':
            info("EVENTOS ATIVOS")
            eventos = sistema.avl.listar_todos()
            
            if not eventos:
                aviso("Nenhum evento ativo no momento.")
            else:
                print(f"\n{Cores.BOLD}Total: {len(eventos)} evento(s){Cores.ENDC}\n")
                print("-" * 80)
                print(f"{'ID':<5} {'Tipo':<18} {'Localização':<15} {'Impacto':<10} {'Data/Hora'}")
                print("-" * 80)
                
                for evento in eventos:
                    data_hora = datetime.fromtimestamp(evento.timestamp).strftime('%d/%m/%Y %H:%M')
                    cor_tipo = Cores.FAIL if evento.tipo == 'acidente' else Cores.WARNING
                    print(f"{evento.id:<5} {cor_tipo}{evento.tipo:<18}{Cores.ENDC} {evento.localizacao:<15} "
                          f"+{evento.impacto:<9.1f} {data_hora}")
                
                print("-" * 80)
            pausar()
            
        elif opcao == '4':
            info("BUSCAR EVENTO POR ID")
            try:
                id_evento = int(input("ID do evento: ").strip())
                evento = sistema.avl.buscar(id_evento)
                
                if evento:
                    print(f"\n{Cores.OKGREEN}{'=' * 50}")
                    print(f"ID: {evento.id}")
                    print(f"Tipo: {evento.tipo}")
                    print(f"Localização: {evento.localizacao}")
                    print(f"Impacto: +{evento.impacto} km")
                    data_hora = datetime.fromtimestamp(evento.timestamp).strftime('%d/%m/%Y às %H:%M')
                    print(f"Registrado em: {data_hora}")
                    print(f"{'=' * 50}{Cores.ENDC}")
                else:
                    erro("Evento não encontrado!")
            except ValueError:
                erro("ID inválido!")
            pausar()
            
        elif opcao == '0':
            break
        else:
            erro("Opção inválida!")
            pausar()

def calcular_rotas(sistema):
    """Calcula e compara rotas"""
    while True:
        limpar_tela()
        exibir_cabecalho()
        opcao = menu_rotas()
        
        if opcao == '1':
            info("CALCULAR ROTA ÓTIMA")
            origem = input("Origem: ").strip().upper()
            destino = input("Destino: ").strip().upper()
            
            print(f"\n{Cores.OKCYAN}Calculando...{Cores.ENDC}")
            caminho, distancia, status = sistema.calcular_rota_otima(origem, destino)
            
            if status == "OK":
                print(f"\n{Cores.OKGREEN}{'=' * 50}")
                print("ROTA ÓTIMA ENCONTRADA")
                print("=" * 50)
                print(f"Caminho: {' → '.join(caminho)}")
                print(f"Distância total: {distancia:.2f} km")
                print(f"{'=' * 50}{Cores.ENDC}")
                
                eventos = sistema.eventos_na_rota(caminho)
                if eventos:
                    aviso(f"Atenção: {len(eventos)} evento(s) afetando esta rota:")
                    for ev in eventos:
                        print(f"  • {ev.tipo} em {ev.localizacao} (+{ev.impacto} km)")
            else:
                erro(status)
            pausar()
            
        elif opcao == '2':
            info("COMPARAR ROTAS (COM/SEM EVENTOS)")
            origem = input("Origem: ").strip().upper()
            destino = input("Destino: ").strip().upper()
            
            print(f"\n{Cores.OKCYAN}Analisando...{Cores.ENDC}")
            resultado = sistema.comparar_rotas(origem, destino)
            
            caminho_ideal, dist_ideal = resultado['rota_ideal']
            caminho_atual, dist_atual = resultado['rota_atual']
            impacto = resultado['impacto']
            
            print("\n" + "=" * 60)
            print("COMPARAÇÃO DE ROTAS")
            print("=" * 60)
            
            if caminho_ideal:
                print(f"\n{Cores.OKGREEN}🟢 Rota ideal (sem eventos):")
                print(f"   Caminho: {' → '.join(caminho_ideal)}")
                print(f"   Distância: {dist_ideal:.2f} km{Cores.ENDC}")
            
            if caminho_atual:
                print(f"\n{Cores.FAIL}🔴 Rota atual (com eventos):")
                print(f"   Caminho: {' → '.join(caminho_atual)}")
                print(f"   Distância: {dist_atual:.2f} km{Cores.ENDC}")
            
            if impacto > 0:
                aviso(f"Impacto dos eventos: +{impacto:.2f} km ({(impacto/dist_ideal*100):.1f}%)")
            elif impacto == 0:
                sucesso("Nenhum impacto - rotas idênticas")
            
            print("=" * 60)
            pausar()
            
        elif opcao == '3':
            info("IDENTIFICAR EVENTOS NA ROTA")
            origem = input("Origem: ").strip().upper()
            destino = input("Destino: ").strip().upper()
            
            caminho, distancia, status = sistema.calcular_rota_otima(origem, destino)
            
            if status == "OK":
                eventos = sistema.eventos_na_rota(caminho)
                print(f"\nRota: {' → '.join(caminho)}")
                print(f"Distância: {distancia:.2f} km\n")
                
                if eventos:
                    aviso(f"{len(eventos)} evento(s) afetando esta rota:\n")
                    for ev in eventos:
                        print(f"  ID {ev.id}: {ev.tipo} em {ev.localizacao}")
                        print(f"           Impacto: +{ev.impacto} km")
                        data = datetime.fromtimestamp(ev.timestamp).strftime('%d/%m/%Y %H:%M')
                        print(f"           Registrado: {data}\n")
                else:
                    sucesso("Nenhum evento afetando esta rota")
            else:
                erro(status)
            pausar()
            
        elif opcao == '0':
            break
        else:
            erro("Opção inválida!")
            pausar()

def exibir_estatisticas(sistema):
    """Exibe estatísticas do sistema"""
    limpar_tela()
    exibir_cabecalho()
    
    info("ANÁLISE E ESTATÍSTICAS")
    
    stats = sistema.estatisticas()
    
    print(f"\n{Cores.BOLD}{'=' * 50}")
    print("RESUMO DO SISTEMA")
    print("=" * 50)
    print(f"Interseções cadastradas: {stats['total_intersecoes']}")
    print(f"Vias cadastradas: {stats['total_vias']}")
    print(f"Eventos ativos: {stats['eventos_ativos']}")
    print(f"{'=' * 50}{Cores.ENDC}")
    
    if stats['eventos_ativos'] > 0:
        print("\nDistribuição por tipo de evento:")
        eventos = sistema.avl.listar_todos()
        tipos = {}
        for ev in eventos:
            tipos[ev.tipo] = tipos.get(ev.tipo, 0) + 1
        
        for tipo, qtd in sorted(tipos.items()):
            print(f"  • {tipo.capitalize()}: {qtd}")
    
    pausar()

def gerenciar_persistencia(sistema):
    """Gerencia salvamento e carregamento de dados"""
    limpar_tela()
    exibir_cabecalho()
    
    print(f"\n{Cores.OKBLUE}┌─────────────────────────────────────────────────┐")
    print("│  PERSISTÊNCIA DE DADOS                          │")
    print("├─────────────────────────────────────────────────┤")
    print("│  1. Salvar dados                                │")
    print("│  2. Carregar dados                              │")
    print("│  0. Voltar                                      │")
    print(f"└─────────────────────────────────────────────────┘{Cores.ENDC}")
    
    opcao = input("\nEscolha uma opção: ").strip()
    
    if opcao == '1':
        resultado, msg = sistema.salvar_dados()
        if resultado:
            sucesso(msg)
        else:
            erro(msg)
        pausar()
        
    elif opcao == '2':
        resultado, msg = sistema.carregar_dados()
        if resultado:
            sucesso(msg)
        else:
            erro(msg)
        pausar()

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
    """Executa o loop principal do sistema"""
    while True:
        limpar_tela()
        exibir_cabecalho()
        opcao = menu_principal()
        
        if opcao == '1':
            gerenciar_malha_viaria(sistema)
        elif opcao == '2':
            gerenciar_eventos(sistema)
        elif opcao == '3':
            calcular_rotas(sistema)
        elif opcao == '4':
            exibir_estatisticas(sistema)
        elif opcao == '5':
            gerenciar_persistencia(sistema)
        elif opcao == '0':
            sucesso("Encerrando o sistema...")
            time.sleep(1)
            break
        else:
            erro("Opção inválida!")
            pausar()

def main():
    """Função principal"""
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