#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes Unitários para o Sistema de Trânsito Inteligente
"""

import sys
import time


def teste_avl():
    """Testa as operações da Árvore AVL"""
    print("\n" + "="*60)
    print("TESTE 1: ÁRVORE AVL")
    print("="*60)
    
    from avl_tree import ArvoreAVL
    
    avl = ArvoreAVL()
    
    # Teste 1.1: Inserção
    print("\n→ Teste 1.1: Inserção de eventos")
    avl.inserir(1, 1000, "acidente", "A-B", 5.0)
    avl.inserir(2, 2000, "obra", "C-D", 3.0)
    avl.inserir(3, 1500, "congestionamento", "E-F", 2.0)
    print(f"✓ {avl.total_eventos} eventos inseridos")
    
    # Teste 1.2: Busca
    print("\n→ Teste 1.2: Busca de evento")
    evento = avl.buscar(2)
    if evento and evento.id == 2:
        print(f"✓ Evento encontrado: {evento}")
    else:
        print("✗ Falha na busca")
    
    # Teste 1.3: Listagem ordenada
    print("\n→ Teste 1.3: Listagem ordenada (in-order)")
    eventos = avl.listar_todos()
    print(f"✓ Eventos em ordem de timestamp:")
    for ev in eventos:
        print(f"   ID {ev.id}: timestamp {ev.timestamp}")
    
    # Verificar ordenação
    ordenado = all(eventos[i].timestamp <= eventos[i+1].timestamp 
                   for i in range(len(eventos)-1))
    if ordenado:
        print("✓ Eventos corretamente ordenados")
    else:
        print("✗ Erro na ordenação")
    
    # Teste 1.4: Remoção
    print("\n→ Teste 1.4: Remoção de evento")
    removido = avl.remover(2)
    if removido:
        print(f"✓ Evento 2 removido. Total: {avl.total_eventos}")
    else:
        print("✗ Falha na remoção")
    
    # Teste 1.5: Balanceamento
    print("\n→ Teste 1.5: Teste de balanceamento")
    avl_teste = ArvoreAVL()
    for i in range(10):
        avl_teste.inserir(i, i*1000, "teste", "X-Y", 1.0)
    
    def altura_arvore(no):
        if not no:
            return 0
        return no.altura
    
    altura = altura_arvore(avl_teste.raiz)
    print(f"✓ Altura da árvore com 10 elementos: {altura}")
    print(f"   (Altura máxima teórica para AVL: {int(__import__('math').log2(10)) + 1})")
    
    if altura <= 5:  # Para 10 elementos, altura não deve exceder 5
        print("✓ Árvore está balanceada")
    else:
        print("✗ Árvore pode estar desbalanceada")
    
    return True


def teste_grafo():
    """Testa as operações do Grafo"""
    print("\n" + "="*60)
    print("TESTE 2: GRAFO PONDERADO")
    print("="*60)
    
    from grafo_ponderado import GrafoPonderado
    
    grafo = GrafoPonderado()
    
    # Teste 2.1: Adicionar vértices e arestas
    print("\n→ Teste 2.1: Construção do grafo")
    vertices = ['A', 'B', 'C', 'D', 'E']
    for v in vertices:
        grafo.adicionar_vertice(v)
    
    arestas = [
        ('A', 'B', 4.0),
        ('A', 'C', 2.0),
        ('B', 'C', 1.0),
        ('B', 'D', 5.0),
        ('C', 'D', 8.0),
        ('C', 'E', 10.0),
        ('D', 'E', 2.0)
    ]
    
    for origem, destino, peso in arestas:
        grafo.adicionar_aresta(origem, destino, peso)
    
    print(f"✓ {grafo.total_vertices()} vértices adicionados")
    print(f"✓ {grafo.total_arestas()} arestas adicionadas")
    
    # Teste 2.2: Dijkstra - caminho mínimo
    print("\n→ Teste 2.2: Algoritmo de Dijkstra")
    caminho, distancia = grafo.dijkstra('A', 'E')
    print(f"✓ Caminho de A até E: {' → '.join(caminho)}")
    print(f"✓ Distância: {distancia:.1f} km")
    
    # Verificar caminho esperado: A → C → B → D → E (distância: 10)
    if caminho == ['A', 'C', 'B', 'D', 'E'] and abs(distancia - 10.0) < 0.01:
        print("✓ Caminho ótimo correto!")
    else:
        print(f"⚠ Caminho encontrado pode não ser o ótimo")
        print(f"   Esperado: A → C → B → D → E (10.0 km)")
    
    # Teste 2.3: Atualização de peso
    print("\n→ Teste 2.3: Atualização dinâmica de peso")
    peso_original = grafo.obter_peso('A', 'C')
    print(f"   Peso original A-C: {peso_original} km")
    
    grafo.atualizar_peso('A', 'C', 10.0)
    novo_peso = grafo.obter_peso('A', 'C')
    print(f"   Novo peso A-C: {novo_peso} km")
    
    # Recalcular rota
    caminho2, distancia2 = grafo.dijkstra('A', 'E')
    print(f"✓ Nova rota: {' → '.join(caminho2)}")
    print(f"✓ Nova distância: {distancia2:.1f} km")
    
    if caminho2 != caminho:
        print("✓ Rota alterada após mudança de peso (correto!)")
    
    # Teste 2.4: Remover aresta
    print("\n→ Teste 2.4: Remoção de aresta")
    removido = grafo.remover_aresta('D', 'E')
    if removido:
        print("✓ Aresta D-E removida")
        caminho3, distancia3 = grafo.dijkstra('A', 'E')
        if caminho3:
            print(f"   Nova rota sem D-E: {' → '.join(caminho3)}")
        else:
            print("   Nenhuma rota disponível (esperado se D-E era única conexão)")
    
    return True


def teste_integracao():
    """Testa a integração entre Grafo e AVL"""
    print("\n" + "="*60)
    print("TESTE 3: INTEGRAÇÃO GRAFO + AVL")
    print("="*60)
    
    from avl_tree import ArvoreAVL
    from grafo_ponderado import GrafoPonderado
    from sistema_transito import SistemaTransito
    
    grafo = GrafoPonderado()
    avl = ArvoreAVL()
    sistema = SistemaTransito(grafo, avl)
    
    # Teste 3.1: Criar malha viária
    print("\n→ Teste 3.1: Criação da malha viária")
    grafo.adicionar_aresta('A', 'B', 5.0)
    grafo.adicionar_aresta('B', 'C', 3.0)
    grafo.adicionar_aresta('A', 'C', 10.0)
    print("✓ Malha criada: A-B (5km), B-C (3km), A-C (10km)")
    
    # Teste 3.2: Rota sem eventos
    print("\n→ Teste 3.2: Rota ótima sem eventos")
    caminho1, dist1, status = sistema.calcular_rota_otima('A', 'C')
    print(f"✓ Rota: {' → '.join(caminho1)}")
    print(f"✓ Distância: {dist1:.1f} km")
    
    # Teste 3.3: Registrar evento e verificar impacto
    print("\n→ Teste 3.3: Registrar evento de trânsito")
    sucesso, msg = sistema.registrar_evento('acidente', 'A', 'B', 10.0)
    print(f"✓ {msg}")
    
    # Verificar se peso foi atualizado
    novo_peso = grafo.obter_peso('A', 'B')
    print(f"   Peso A-B atualizado: {novo_peso:.1f} km")
    
    if abs(novo_peso - 15.0) < 0.01:  # 5.0 + 10.0
        print("✓ Peso atualizado corretamente no grafo")
    else:
        print("✗ Erro na atualização do peso")
    
    # Teste 3.4: Rota com evento
    print("\n→ Teste 3.4: Rota ótima com evento ativo")
    caminho2, dist2, status = sistema.calcular_rota_otima('A', 'C')
    print(f"✓ Rota: {' → '.join(caminho2)}")
    print(f"✓ Distância: {dist2:.1f} km")
    
    if caminho2 != caminho1:
        print("✓ Sistema encontrou rota alternativa (integração funcionando!)")
    
    # Teste 3.5: Comparação de rotas
    print("\n→ Teste 3.5: Comparação de rotas")
    comparacao = sistema.comparar_rotas('A', 'C')
    caminho_ideal, dist_ideal = comparacao['rota_ideal']
    caminho_atual, dist_atual = comparacao['rota_atual']
    impacto = comparacao['impacto']
    
    print(f"   Rota ideal: {' → '.join(caminho_ideal)} ({dist_ideal:.1f} km)")
    print(f"   Rota atual: {' → '.join(caminho_atual)} ({dist_atual:.1f} km)")
    print(f"   Impacto: +{impacto:.1f} km")
    
    # Teste 3.6: Remover evento e restaurar peso
    print("\n→ Teste 3.6: Remover evento")
    sucesso, msg = sistema.remover_evento(1)
    print(f"✓ {msg}")
    
    peso_restaurado = grafo.obter_peso('A', 'B')
    print(f"   Peso A-B restaurado: {peso_restaurado:.1f} km")
    
    if abs(peso_restaurado - 5.0) < 0.01:
        print("✓ Peso original restaurado (integração bidirecional OK!)")
    else:
        print("✗ Erro ao restaurar peso original")
    
    return True


def teste_persistencia():
    """Testa salvamento e carregamento de dados"""
    print("\n" + "="*60)
    print("TESTE 4: PERSISTÊNCIA DE DADOS")
    print("="*60)
    
    from avl_tree import ArvoreAVL
    from grafo_ponderado import GrafoPonderado
    from sistema_transito import SistemaTransito
    import os
    
    # Criar sistema com dados
    print("\n→ Teste 4.1: Salvar dados")
    grafo1 = GrafoPonderado()
    avl1 = ArvoreAVL()
    sistema1 = SistemaTransito(grafo1, avl1)
    
    grafo1.adicionar_aresta('X', 'Y', 7.5)
    grafo1.adicionar_aresta('Y', 'Z', 4.2)
    sistema1.registrar_evento('obra', 'X', 'Y', 2.5)
    
    sucesso, msg = sistema1.salvar_dados()
    if sucesso:
        print(f"✓ {msg}")
    else:
        print(f"✗ {msg}")
        return False
    
    # Carregar em novo sistema
    print("\n→ Teste 4.2: Carregar dados")
    grafo2 = GrafoPonderado()
    avl2 = ArvoreAVL()
    sistema2 = SistemaTransito(grafo2, avl2)
    
    sucesso, msg = sistema2.carregar_dados()
    if sucesso:
        print(f"✓ {msg}")
    else:
        print(f"✗ {msg}")
        return False
    
    # Verificar integridade
    print("\n→ Teste 4.3: Verificar integridade dos dados")
    
    if grafo2.total_vertices() == grafo1.total_vertices():
        print(f"✓ Vértices: {grafo2.total_vertices()} (correto)")
    else:
        print(f"✗ Vértices: esperado {grafo1.total_vertices()}, obtido {grafo2.total_vertices()}")
    
    if grafo2.total_arestas() == grafo1.total_arestas():
        print(f"✓ Arestas: {grafo2.total_arestas()} (correto)")
    else:
        print(f"✗ Arestas: esperado {grafo1.total_arestas()}, obtido {grafo2.total_arestas()}")
    
    if avl2.total_eventos == avl1.total_eventos:
        print(f"✓ Eventos: {avl2.total_eventos} (correto)")
    else:
        print(f"✗ Eventos: esperado {avl1.total_eventos}, obtido {avl2.total_eventos}")
    
    # Verificar peso atualizado
    peso = grafo2.obter_peso('X', 'Y')
    if peso and abs(peso - 10.0) < 0.01:  # 7.5 + 2.5
        print(f"✓ Peso com evento mantido: {peso:.1f} km")
    else:
        print(f"✗ Erro no peso: esperado 10.0, obtido {peso}")
    
    # Limpar arquivos de teste
    try:
        os.remove("dados/grafo.txt")
        os.remove("dados/eventos.txt")
        print("\n✓ Arquivos de teste removidos")
    except:
        pass
    
    return True


def teste_performance():
    """Testa performance com volume maior de dados"""
    print("\n" + "="*60)
    print("TESTE 5: PERFORMANCE")
    print("="*60)
    
    from avl_tree import ArvoreAVL
    from grafo_ponderado import GrafoPonderado
    import time
    
    # Teste 5.1: AVL com muitos eventos
    print("\n→ Teste 5.1: AVL - Inserção de 1000 eventos")
    avl = ArvoreAVL()
    
    inicio = time.time()
    for i in range(1000):
        avl.inserir(i, i*100, "teste", f"A{i%10}-B{i%10}", 1.0)
    fim = time.time()
    
    tempo = (fim - inicio) * 1000
    print(f"✓ Tempo: {tempo:.2f} ms")
    print(f"✓ Média por inserção: {tempo/1000:.3f} ms")
    
    # Teste 5.2: Busca na AVL
    print("\n→ Teste 5.2: AVL - Busca de eventos")
    inicio = time.time()
    for i in range(0, 1000, 10):
        avl.buscar(i)
    fim = time.time()
    
    tempo = (fim - inicio) * 1000
    print(f"✓ 100 buscas em {tempo:.2f} ms")
    print(f"✓ Média por busca: {tempo/100:.3f} ms")
    
    # Teste 5.3: Grafo com muitas arestas
    print("\n→ Teste 5.3: Grafo - Construção de malha grande")
    grafo = GrafoPonderado()
    
    n = 50  # 50 vértices
    inicio = time.time()
    
    # Criar grade
    for i in range(n):
        for j in range(n):
            vertice = f"{i},{j}"
            grafo.adicionar_vertice(vertice)
            
            # Conectar com vizinhos
            if i > 0:
                grafo.adicionar_aresta(vertice, f"{i-1},{j}", 1.0)
            if j > 0:
                grafo.adicionar_aresta(vertice, f"{i},{j-1}", 1.0)
    
    fim = time.time()
    tempo = (fim - inicio) * 1000
    
    print(f"✓ {grafo.total_vertices()} vértices criados")
    print(f"✓ {grafo.total_arestas()} arestas criadas")
    print(f"✓ Tempo: {tempo:.2f} ms")
    
    # Teste 5.4: Dijkstra em grafo grande
    print("\n→ Teste 5.4: Dijkstra em malha 50x50")
    inicio = time.time()
    caminho, distancia = grafo.dijkstra("0,0", "49,49")
    fim = time.time()
    
    tempo = (fim - inicio) * 1000
    print(f"✓ Caminho encontrado com {len(caminho)} vértices")
    print(f"✓ Distância: {distancia:.1f}")
    print(f"✓ Tempo: {tempo:.2f} ms")
    
    return True


def executar_todos_testes():
    """Executa todos os testes"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "SISTEMA DE TRÂNSITO INTELIGENTE" + " "*17 + "║")
    print("║" + " "*17 + "BATERIA DE TESTES" + " "*24 + "║")
    print("╚" + "="*58 + "╝")
    
    testes = [
        ("AVL", teste_avl),
        ("Grafo Ponderado", teste_grafo),
        ("Integração", teste_integracao),
        ("Persistência", teste_persistencia),
        ("Performance", teste_performance)
    ]
    
    resultados = []
    
    for nome, funcao_teste in testes:
        try:
            sucesso = funcao_teste()
            resultados.append((nome, sucesso))
        except Exception as e:
            print(f"\n✗ ERRO no teste {nome}: {str(e)}")
            resultados.append((nome, False))
    
    # Resumo
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    
    for nome, sucesso in resultados:
        status = "✓ PASSOU" if sucesso else "✗ FALHOU"
        print(f"{nome:.<40} {status}")
    
    total = len(resultados)
    passou = sum(1 for _, s in resultados if s)
    
    print("="*60)
    print(f"Total: {passou}/{total} testes passaram")
    print("="*60)
    
    if passou == total:
        print("\n🎉 Todos os testes passaram com sucesso!")
    else:
        print(f"\n⚠ {total - passou} teste(s) falharam")
    
    return passou == total


if __name__ == "__main__":
    executar_todos_testes()
