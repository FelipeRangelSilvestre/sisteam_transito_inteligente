#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementação de Grafo Ponderado para o Sistema de Trânsito Inteligente
Representa a malha viária com vértices (interseções) e arestas (vias)
"""

import heapq
from collections import defaultdict


class GrafoPonderado:
    """Grafo ponderado para representar a malha viária"""
    
    def __init__(self):
        self.vertices = set()
        self.arestas = defaultdict(dict)  # {origem: {destino: peso}}
        self.pesos_originais = {}  # Armazena pesos originais antes de eventos
    
    def adicionar_vertice(self, vertice):
        """
        Adiciona uma interseção/ponto ao grafo
        Complexidade: O(1)
        """
        self.vertices.add(vertice)
        return True
    
    def adicionar_aresta(self, origem, destino, peso):
        """
        Adiciona uma via bidirecional entre duas interseções
        Complexidade: O(1)
        
        Args:
            origem: Vértice de origem
            destino: Vértice de destino
            peso: Distância/custo da via
        """
        if origem not in self.vertices:
            self.adicionar_vertice(origem)
        if destino not in self.vertices:
            self.adicionar_vertice(destino)
        
        # Aresta bidirecional (grafo não direcionado)
        self.arestas[origem][destino] = peso
        self.arestas[destino][origem] = peso
        
        # Salvar peso original para restauração posterior
        chave1 = f"{origem}-{destino}"
        chave2 = f"{destino}-{origem}"
        self.pesos_originais[chave1] = peso
        self.pesos_originais[chave2] = peso
        
        return True
    
    def remover_aresta(self, origem, destino):
        """
        Remove uma via do grafo
        Complexidade: O(1)
        """
        if origem in self.arestas and destino in self.arestas[origem]:
            del self.arestas[origem][destino]
            del self.arestas[destino][origem]
            
            # Remover pesos originais
            chave1 = f"{origem}-{destino}"
            chave2 = f"{destino}-{origem}"
            if chave1 in self.pesos_originais:
                del self.pesos_originais[chave1]
            if chave2 in self.pesos_originais:
                del self.pesos_originais[chave2]
            
            return True
        return False
    
    def atualizar_peso(self, origem, destino, novo_peso):
        """
        Atualiza o peso de uma aresta (usado quando eventos são registrados)
        Complexidade: O(1)
        """
        if origem in self.arestas and destino in self.arestas[origem]:
            self.arestas[origem][destino] = novo_peso
            self.arestas[destino][origem] = novo_peso
            return True
        return False
    
    def obter_peso(self, origem, destino):
        """
        Obtém o peso atual de uma aresta
        Complexidade: O(1)
        """
        if origem in self.arestas and destino in self.arestas[origem]:
            return self.arestas[origem][destino]
        return None
    
    def obter_peso_original(self, origem, destino):
        """
        Obtém o peso original de uma aresta (antes de eventos)
        Complexidade: O(1)
        """
        chave = f"{origem}-{destino}"
        return self.pesos_originais.get(chave)
    
    def obter_vizinhos(self, vertice):
        """
        Retorna os vizinhos de um vértice
        Complexidade: O(1)
        """
        return self.arestas.get(vertice, {})
    
    def dijkstra(self, origem, destino):
        """
        Algoritmo de Dijkstra para encontrar o caminho mínimo
        Complexidade: O((V + E) log V) usando heap binário
        
        Args:
            origem: Vértice inicial
            destino: Vértice final
            
        Returns:
            tupla (caminho, distancia) onde:
            - caminho: lista de vértices do caminho ótimo
            - distancia: custo total do caminho
        """
        if origem not in self.vertices or destino not in self.vertices:
            return None, float('inf')
        
        # Inicialização
        distancias = {v: float('inf') for v in self.vertices}
        distancias[origem] = 0
        predecessores = {v: None for v in self.vertices}
        visitados = set()
        
        # Fila de prioridade: (distância, vértice)
        fila = [(0, origem)]
        
        while fila:
            dist_atual, atual = heapq.heappop(fila)
            
            # Se já foi visitado, pular
            if atual in visitados:
                continue
            
            visitados.add(atual)
            
            # Se chegou ao destino, pode parar (otimização)
            if atual == destino:
                break
            
            # Relaxamento das arestas (verificar vizinhos)
            for vizinho, peso in self.arestas[atual].items():
                if vizinho not in visitados:
                    nova_dist = dist_atual + peso
                    
                    # Se encontrou caminho mais curto
                    if nova_dist < distancias[vizinho]:
                        distancias[vizinho] = nova_dist
                        predecessores[vizinho] = atual
                        heapq.heappush(fila, (nova_dist, vizinho))
        
        # Reconstruir caminho do destino até a origem
        caminho = []
        atual = destino
        while atual is not None:
            caminho.append(atual)
            atual = predecessores[atual]
        
        caminho.reverse()
        
        # Se não há caminho (caminho só tem destino mas não origem)
        if len(caminho) == 1 and caminho[0] != origem:
            return None, float('inf')
        
        return caminho, distancias[destino]
    
    def obter_todas_arestas(self):
        """
        Retorna todas as arestas únicas do grafo
        Complexidade: O(E) onde E é o número de arestas
        """
        arestas_unicas = []
        processadas = set()
        
        for origem in self.arestas:
            for destino, peso in self.arestas[origem].items():
                # Evitar duplicatas (A-B e B-A são a mesma aresta)
                aresta = tuple(sorted([origem, destino]))
                if aresta not in processadas:
                    arestas_unicas.append((origem, destino, peso))
                    processadas.add(aresta)
        
        return arestas_unicas
    
    def visualizar_grafo(self):
        """
        Retorna uma representação textual do grafo para exibição no terminal
        """
        if not self.vertices:
            return "Grafo vazio"
        
        linhas = ["=" * 50]
        linhas.append("MALHA VIÁRIA")
        linhas.append("=" * 50)
        linhas.append(f"Total de interseções: {len(self.vertices)}")
        linhas.append(f"Interseções: {', '.join(sorted(self.vertices))}")
        linhas.append("\nVias (bidirecionais):")
        linhas.append("-" * 50)
        
        arestas = self.obter_todas_arestas()
        for origem, destino, peso in sorted(arestas):
            peso_orig = self.obter_peso_original(origem, destino)
            if peso != peso_orig:
                # Via com evento ativo
                linhas.append(f"{origem} <-> {destino}: {peso:.1f}km (original: {peso_orig:.1f}km) *")
            else:
                linhas.append(f"{origem} <-> {destino}: {peso:.1f}km")
        
        linhas.append("-" * 50)
        linhas.append("* Via com evento de trânsito ativo")
        
        return "\n".join(linhas)
    
    def total_vertices(self):
        """Retorna o número de vértices no grafo"""
        return len(self.vertices)
    
    def total_arestas(self):
        """Retorna o número de arestas únicas no grafo"""
        return len(self.obter_todas_arestas())
    
    def existe_caminho(self, origem, destino):
        """
        Verifica se existe um caminho entre dois vértices
        Usa BFS (Busca em Largura)
        Complexidade: O(V + E)
        """
        if origem not in self.vertices or destino not in self.vertices:
            return False
        
        if origem == destino:
            return True
        
        visitados = set()
        fila = [origem]
        visitados.add(origem)
        
        while fila:
            atual = fila.pop(0)
            
            if atual == destino:
                return True
            
            for vizinho in self.arestas[atual]:
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    fila.append(vizinho)
        
        return False


# Teste simples (executar apenas se for o arquivo principal)
if __name__ == "__main__":
    print("Testando Grafo Ponderado...\n")
    
    # Criar grafo
    grafo = GrafoPonderado()
    
    # Adicionar vértices e arestas
    grafo.adicionar_aresta('A', 'B', 5.0)
    grafo.adicionar_aresta('A', 'C', 3.0)
    grafo.adicionar_aresta('B', 'C', 2.0)
    grafo.adicionar_aresta('B', 'D', 6.0)
    grafo.adicionar_aresta('C', 'D', 4.0)
    grafo.adicionar_aresta('D', 'E', 2.0)
    
    # Visualizar
    print(grafo.visualizar_grafo())
    
    # Testar Dijkstra
    print("\n\nTestando Dijkstra de A até E:")
    caminho, distancia = grafo.dijkstra('A', 'E')
    print(f"Caminho: {' → '.join(caminho)}")
    print(f"Distância: {distancia:.1f} km")
    
    # Simular evento
    print("\n\nSimulando acidente em A-B (+10 km)...")
    grafo.atualizar_peso('A', 'B', 15.0)
    
    caminho2, distancia2 = grafo.dijkstra('A', 'E')
    print(f"Novo caminho: {' → '.join(caminho2)}")
    print(f"Nova distância: {distancia2:.1f} km")
    
    print("\n✓ Teste concluído!")
