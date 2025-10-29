#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Trânsito Inteligente - Integração entre Grafo e AVL
Este módulo integra as estruturas de dados para gerenciar
a malha viária e os eventos de trânsito de forma eficiente
"""

import time
import os


class SistemaTransito:
    """
    Sistema de Trânsito Inteligente
    Integra Grafo (malha viária) + AVL (eventos de trânsito)
    """
    
    def __init__(self, grafo, avl):
        """
        Inicializa o sistema com um grafo e uma árvore AVL
        
        Args:
            grafo: Instância de GrafoPonderado
            avl: Instância de ArvoreAVL
        """
        self.grafo = grafo
        self.avl = avl
        self.proximo_id_evento = 1
    
    def registrar_evento(self, tipo, origem, destino, impacto):
        """
        Registra um evento de trânsito e atualiza o grafo
        Integração: AVL + Grafo
        
        Args:
            tipo: Tipo do evento ('acidente', 'obra', 'congestionamento')
            origem: Vértice de origem da aresta afetada
            destino: Vértice de destino da aresta afetada
            impacto: Acréscimo no peso da aresta (em km)
        
        Returns:
            tupla (sucesso, mensagem)
        
        Complexidade: O(log n) - dominada pela inserção na AVL
        """
        # Validar se a aresta existe no grafo
        peso_atual = self.grafo.obter_peso(origem, destino)
        if peso_atual is None:
            return False, "Via não encontrada no mapa"
        
        # Criar evento com timestamp atual
        timestamp = int(time.time())
        localizacao = f"{origem}-{destino}"
        id_evento = self.proximo_id_evento
        
        # Inserir na AVL - O(log n)
        self.avl.inserir(id_evento, timestamp, tipo, localizacao, impacto)
        
        # Atualizar peso no grafo - O(1)
        novo_peso = peso_atual + impacto
        self.grafo.atualizar_peso(origem, destino, novo_peso)
        
        self.proximo_id_evento += 1
        
        return True, f"Evento {id_evento} registrado com sucesso"
    
    def remover_evento(self, id_evento):
        """
        Remove um evento e restaura o peso original da via
        Integração: AVL + Grafo
        
        Args:
            id_evento: ID do evento a ser removido
        
        Returns:
            tupla (sucesso, mensagem)
        
        Complexidade: O(log n) - dominada pela busca e remoção na AVL
        """
        # Buscar evento na AVL - O(log n)
        evento = self.avl.buscar(id_evento)
        if not evento:
            return False, "Evento não encontrado"
        
        # Extrair origem e destino da localização
        origem, destino = evento.localizacao.split('-')
        
        # Restaurar peso original no grafo - O(1)
        peso_original = self.grafo.obter_peso_original(origem, destino)
        if peso_original:
            self.grafo.atualizar_peso(origem, destino, peso_original)
        
        # Remover da AVL - O(log n)
        self.avl.remover(id_evento)
        
        return True, f"Evento {id_evento} removido com sucesso"
    
    def calcular_rota_otima(self, origem, destino):
        """
        Calcula a rota ótima considerando os eventos ativos
        Usa Dijkstra no grafo com pesos atualizados pelos eventos
        
        Args:
            origem: Vértice de origem
            destino: Vértice de destino
        
        Returns:
            tupla (caminho, distancia, status)
        
        Complexidade: O((V + E) log V) - Dijkstra
        """
        caminho, distancia = self.grafo.dijkstra(origem, destino)
        
        if caminho is None:
            return None, None, "Não há rota disponível"
        
        return caminho, distancia, "OK"
    
    def comparar_rotas(self, origem, destino):
        """
        Compara rota atual (com eventos) vs rota ideal (sem eventos)
        
        Args:
            origem: Vértice de origem
            destino: Vértice de destino
        
        Returns:
            dicionário com 'rota_ideal', 'rota_atual' e 'impacto'
        
        Complexidade: O((V + E) log V) - dois Dijkstras
        """
        # Salvar pesos atuais (com eventos)
        pesos_temp = {}
        for o, destinos in self.grafo.arestas.items():
            for d, peso in destinos.items():
                pesos_temp[f"{o}-{d}"] = peso
        
        # Restaurar pesos originais temporariamente (sem eventos)
        for chave, peso_orig in self.grafo.pesos_originais.items():
            o, d = chave.split('-')
            if o in self.grafo.arestas and d in self.grafo.arestas[o]:
                self.grafo.arestas[o][d] = peso_orig
        
        # Calcular rota sem eventos - O((V + E) log V)
        caminho_ideal, dist_ideal = self.grafo.dijkstra(origem, destino)
        
        # Restaurar pesos com eventos
        for chave, peso in pesos_temp.items():
            o, d = chave.split('-')
            if o in self.grafo.arestas and d in self.grafo.arestas[o]:
                self.grafo.arestas[o][d] = peso
        
        # Calcular rota com eventos - O((V + E) log V)
        caminho_atual, dist_atual = self.grafo.dijkstra(origem, destino)
        
        return {
            'rota_ideal': (caminho_ideal, dist_ideal),
            'rota_atual': (caminho_atual, dist_atual),
            'impacto': dist_atual - dist_ideal if dist_ideal != float('inf') else 0
        }
    
    def eventos_na_rota(self, caminho):
        """
        Identifica eventos que afetam uma rota específica
        
        Args:
            caminho: Lista de vértices representando o caminho
        
        Returns:
            lista de eventos que afetam a rota
        
        Complexidade: O(k * log n) onde k é o tamanho do caminho
        """
        if not caminho or len(caminho) < 2:
            return []
        
        eventos_afetando = []
        
        # Verificar cada segmento da rota
        for i in range(len(caminho) - 1):
            origem = caminho[i]
            destino = caminho[i + 1]
            localizacao = f"{origem}-{destino}"
            
            # Buscar eventos nesta localização - O(n) no pior caso
            # mas geralmente será rápido pois poucos eventos por via
            eventos = self.avl.buscar_por_localizacao(localizacao)
            eventos_afetando.extend(eventos)
        
        return eventos_afetando
    
    def salvar_dados(self, arquivo_grafo="dados/grafo.txt", arquivo_eventos="dados/eventos.txt"):
        """
        Salva o estado atual do sistema em arquivos
        
        Args:
            arquivo_grafo: Caminho para salvar o grafo
            arquivo_eventos: Caminho para salvar os eventos
        
        Returns:
            tupla (sucesso, mensagem)
        
        Complexidade: O(V + E + n) onde n é o número de eventos
        """
        try:
            # Criar diretório se não existir
            os.makedirs("dados", exist_ok=True)
            
            # Salvar grafo
            with open(arquivo_grafo, 'w', encoding='utf-8') as f:
                # Linha 1: número de vértices
                f.write(f"{len(self.grafo.vertices)}\n")
                
                # Linha 2: lista de vértices
                f.write(" ".join(sorted(self.grafo.vertices)) + "\n")
                
                # Linha 3: número de arestas
                arestas = self.grafo.obter_todas_arestas()
                f.write(f"{len(arestas)}\n")
                
                # Linhas seguintes: arestas (origem destino peso_original)
                for origem, destino, peso in arestas:
                    peso_orig = self.grafo.obter_peso_original(origem, destino)
                    f.write(f"{origem} {destino} {peso_orig}\n")
            
            # Salvar eventos
            with open(arquivo_eventos, 'w', encoding='utf-8') as f:
                eventos = self.avl.listar_todos()
                
                # Linha 1: número de eventos
                f.write(f"{len(eventos)}\n")
                
                # Linhas seguintes: eventos (id timestamp tipo localizacao impacto)
                for evento in eventos:
                    f.write(f"{evento.id} {evento.timestamp} {evento.tipo} ")
                    f.write(f"{evento.localizacao} {evento.impacto}\n")
            
            return True, "Dados salvos com sucesso"
        
        except Exception as e:
            return False, f"Erro ao salvar dados: {str(e)}"
    
    def carregar_dados(self, arquivo_grafo="dados/grafo.txt", arquivo_eventos="dados/eventos.txt"):
        """
        Carrega dados dos arquivos para o sistema
        
        Args:
            arquivo_grafo: Caminho do arquivo do grafo
            arquivo_eventos: Caminho do arquivo dos eventos
        
        Returns:
            tupla (sucesso, mensagem)
        
        Complexidade: O((V + E) + n log n) onde n é o número de eventos
        """
        try:
            # Carregar grafo
            with open(arquivo_grafo, 'r', encoding='utf-8') as f:
                # Ler número de vértices
                n_vertices = int(f.readline().strip())
                
                # Ler vértices
                vertices = f.readline().strip().split()
                for v in vertices:
                    self.grafo.adicionar_vertice(v)
                
                # Ler número de arestas
                n_arestas = int(f.readline().strip())
                
                # Ler arestas
                for _ in range(n_arestas):
                    origem, destino, peso = f.readline().strip().split()
                    self.grafo.adicionar_aresta(origem, destino, float(peso))
            
            # Carregar eventos (se o arquivo existir)
            if os.path.exists(arquivo_eventos):
                with open(arquivo_eventos, 'r', encoding='utf-8') as f:
                    # Ler número de eventos
                    n_eventos = int(f.readline().strip())
                    max_id = 0
                    
                    # Ler eventos
                    for _ in range(n_eventos):
                        partes = f.readline().strip().split()
                        id_ev = int(partes[0])
                        timestamp = int(partes[1])
                        tipo = partes[2]
                        localizacao = partes[3]
                        impacto = float(partes[4])
                        
                        # Inserir na AVL - O(log n)
                        self.avl.inserir(id_ev, timestamp, tipo, localizacao, impacto)
                        
                        # Atualizar peso no grafo - O(1)
                        origem, destino = localizacao.split('-')
                        peso_atual = self.grafo.obter_peso(origem, destino)
                        if peso_atual:
                            self.grafo.atualizar_peso(origem, destino, peso_atual + impacto)
                        
                        max_id = max(max_id, id_ev)
                    
                    # Atualizar próximo ID
                    self.proximo_id_evento = max_id + 1
            
            return True, "Dados carregados com sucesso"
        
        except FileNotFoundError:
            return False, "Arquivo não encontrado"
        except Exception as e:
            return False, f"Erro ao carregar dados: {str(e)}"
    
    def estatisticas(self):
        """
        Retorna estatísticas do sistema
        
        Returns:
            dicionário com estatísticas
        
        Complexidade: O(1)
        """
        return {
            'total_intersecoes': self.grafo.total_vertices(),
            'total_vias': self.grafo.total_arestas(),
            'eventos_ativos': self.avl.total_eventos
        }
    
    def limpar_eventos_expirados(self, tempo_expiracao=3600):
        """
        Remove eventos com mais de tempo_expiracao segundos
        Útil para limpar eventos antigos automaticamente
        
        Args:
            tempo_expiracao: Tempo em segundos (padrão: 1 hora)
        
        Returns:
            número de eventos removidos
        
        Complexidade: O(n log n) onde n é o número de eventos
        """
        tempo_atual = int(time.time())
        eventos = self.avl.listar_todos()
        removidos = 0
        
        for evento in eventos:
            if tempo_atual - evento.timestamp > tempo_expiracao:
                self.remover_evento(evento.id)
                removidos += 1
        
        return removidos


# Teste simples (executar apenas se for o arquivo principal)
if __name__ == "__main__":
    print("Testando Sistema de Trânsito Inteligente...\n")
    
    from avl_tree import ArvoreAVL
    from grafo_ponderado import GrafoPonderado
    
    # Criar instâncias
    grafo = GrafoPonderado()
    avl = ArvoreAVL()
    sistema = SistemaTransito(grafo, avl)
    
    # Criar malha viária simples
    print("1. Criando malha viária...")
    grafo.adicionar_aresta('A', 'B', 5.0)
    grafo.adicionar_aresta('B', 'C', 3.0)
    grafo.adicionar_aresta('A', 'C', 10.0)
    print("   ✓ 3 vértices, 3 arestas")
    
    # Calcular rota sem eventos
    print("\n2. Rota ótima sem eventos:")
    caminho, dist, status = sistema.calcular_rota_otima('A', 'C')
    print(f"   {' → '.join(caminho)}: {dist:.1f} km")
    
    # Registrar evento
    print("\n3. Registrando acidente em A-B (+10 km)...")
    sucesso, msg = sistema.registrar_evento('acidente', 'A', 'B', 10.0)
    print(f"   ✓ {msg}")
    
    # Calcular nova rota
    print("\n4. Rota ótima com evento:")
    caminho2, dist2, status = sistema.calcular_rota_otima('A', 'C')
    print(f"   {' → '.join(caminho2)}: {dist2:.1f} km")
    
    if caminho2 != caminho:
        print("   ✓ Sistema encontrou rota alternativa!")
    
    # Comparar rotas
    print("\n5. Comparação de rotas:")
    comp = sistema.comparar_rotas('A', 'C')
    print(f"   Ideal: {comp['rota_ideal'][1]:.1f} km")
    print(f"   Atual: {comp['rota_atual'][1]:.1f} km")
    print(f"   Impacto: +{comp['impacto']:.1f} km")
    
    print("\n✓ Teste concluído!")
