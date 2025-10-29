#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Trânsito Inteligente - VERSÃO MELHORADA
MUDANÇAS PRINCIPAIS:
1. Cada via tem DISTÂNCIA (km) e VELOCIDADE MÉDIA (km/h)
2. Sistema calcula TEMPO automaticamente: tempo = distância / velocidade
3. 3 tipos de eventos que reduzem a velocidade da via:
   - Acidente: reduz velocidade drasticamente (para ~10 km/h)
   - Obra: reduz velocidade moderadamente (para ~20 km/h)
   - Engarrafamento: reduz velocidade levemente (para ~30 km/h)
4. Dijkstra busca caminho de MENOR TEMPO (como Google Maps)
5. Pode escolher rota mais longa em KM se for mais rápida em tempo!
"""

import time
import os


class SistemaTransitoMelhorado:
    """
    Sistema de Trânsito Inteligente - Versão estilo Google Maps
    - Mantém DISTÂNCIA em KM
    - Calcula TEMPO com base na velocidade
    - Prioriza MENOR TEMPO (pode ser caminho mais longo!)
    """
    
    # Velocidades por tipo de via (km/h)
    VELOCIDADE_PADRAO = 60.0  # 60 km/h para vias normais
    
    # Velocidades reduzidas por tipo de evento (km/h)
    VELOCIDADES_EVENTO = {
        'acidente': 10.0,       # Trânsito quase parado
        'obra': 20.0,           # Trânsito muito lento
        'engarrafamento': 30.0  # Trânsito lento
    }
    
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
        
        # Armazenar velocidades de cada via
        # Formato: {"A-B": 60.0, "B-A": 60.0}
        self.velocidades = {}
    
    def _calcular_tempo(self, distancia_km, velocidade_kmh):
        """
        Calcula tempo de percurso
        
        Args:
            distancia_km: Distância em quilômetros
            velocidade_kmh: Velocidade em km/h
        
        Returns:
            tempo em minutos
        """
        if velocidade_kmh <= 0:
            return float('inf')
        return (distancia_km / velocidade_kmh) * 60  # converter para minutos
    
    def adicionar_via(self, origem, destino, distancia_km, velocidade_kmh=None):
        """
        Adiciona uma via bidirecional ao sistema
        
        Args:
            origem: Vértice de origem
            destino: Vértice de destino
            distancia_km: Distância em quilômetros
            velocidade_kmh: Velocidade média (padrão: 60 km/h)
        
        Returns:
            bool: Sucesso da operação
        """
        if velocidade_kmh is None:
            velocidade_kmh = self.VELOCIDADE_PADRAO
        
        # Calcular tempo inicial
        tempo_minutos = self._calcular_tempo(distancia_km, velocidade_kmh)
        
        # Adicionar ao grafo (usando TEMPO como peso)
        self.grafo.adicionar_aresta(origem, destino, tempo_minutos)
        
        # Armazenar velocidade e distância
        self.velocidades[f"{origem}-{destino}"] = velocidade_kmh
        self.velocidades[f"{destino}-{origem}"] = velocidade_kmh
        
        return True
    
    def obter_info_via(self, origem, destino):
        """
        Obtém informações completas de uma via
        
        Returns:
            dict com distancia, velocidade, tempo
        """
        tempo = self.grafo.obter_peso(origem, destino)
        velocidade = self.velocidades.get(f"{origem}-{destino}", self.VELOCIDADE_PADRAO)
        
        if tempo is None:
            return None
        
        # Calcular distância: distancia = (tempo_min / 60) * velocidade
        distancia = (tempo / 60) * velocidade
        
        return {
            'distancia_km': distancia,
            'velocidade_kmh': velocidade,
            'tempo_min': tempo
        }
    
    def registrar_evento(self, tipo, origem, destino):
        """
        Registra um evento de trânsito e atualiza a velocidade da via
        Integração: AVL + Grafo
        
        Args:
            tipo: Tipo do evento ('acidente', 'obra', 'engarrafamento')
            origem: Vértice de origem da aresta afetada
            destino: Vértice de destino da aresta afetada
        
        Returns:
            tupla (sucesso, mensagem)
        
        Complexidade: O(log n) - dominada pela inserção na AVL
        """
        # Validar tipo de evento
        if tipo not in ['acidente', 'obra', 'engarrafamento']:
            return False, "Tipo de evento inválido. Use: 'acidente', 'obra' ou 'engarrafamento'"
        
        # Validar se a aresta existe
        info_antes = self.obter_info_via(origem, destino)
        if info_antes is None:
            return False, "Via não encontrada no mapa"
        
        # Obter velocidade reduzida para este tipo de evento
        nova_velocidade = self.VELOCIDADES_EVENTO[tipo]
        velocidade_original = info_antes['velocidade_kmh']
        distancia = info_antes['distancia_km']
        
        # Calcular novo tempo
        novo_tempo = self._calcular_tempo(distancia, nova_velocidade)
        tempo_original = info_antes['tempo_min']
        aumento_tempo = novo_tempo - tempo_original
        
        # Criar evento
        timestamp = int(time.time())
        localizacao = f"{origem}-{destino}"
        id_evento = self.proximo_id_evento
        
        # Inserir na AVL - O(log n)
        # Armazenamos o aumento de tempo como "impacto"
        self.avl.inserir(id_evento, timestamp, tipo, localizacao, aumento_tempo)
        
        # Atualizar velocidade da via
        self.velocidades[f"{origem}-{destino}"] = nova_velocidade
        self.velocidades[f"{destino}-{origem}"] = nova_velocidade
        
        # Atualizar tempo no grafo - O(1)
        self.grafo.atualizar_peso(origem, destino, novo_tempo)
        
        self.proximo_id_evento += 1
        
        # Mensagens descritivas
        emojis = {
            'acidente': '🚗💥 ACIDENTE',
            'obra': '🚧 OBRA',
            'engarrafamento': '🚦 ENGARRAFAMENTO'
        }
        
        return True, (
            f"{emojis[tipo]} registrado na via {origem}→{destino}!\n"
            f"   📏 Distância: {distancia:.1f} km\n"
            f"   🐌 Velocidade reduzida: {velocidade_original:.0f} → {nova_velocidade:.0f} km/h\n"
            f"   ⏱️  Tempo: {tempo_original:.1f} → {novo_tempo:.1f} min (+{aumento_tempo:.1f} min)"
        )
    
    def remover_evento(self, id_evento):
        """
        Remove um evento e restaura a velocidade normal da via
        
        Args:
            id_evento: ID do evento a ser removido
        
        Returns:
            tupla (sucesso, mensagem)
        
        Complexidade: O(log n)
        """
        # Buscar evento na AVL
        evento = self.avl.buscar(id_evento)
        if not evento:
            return False, "Evento não encontrado"
        
        origem, destino = evento.localizacao.split('-')
        
        # Obter informações atuais
        info = self.obter_info_via(origem, destino)
        if not info:
            return False, "Via não encontrada"
        
        distancia = info['distancia_km']
        
        # Restaurar velocidade original
        self.velocidades[f"{origem}-{destino}"] = self.VELOCIDADE_PADRAO
        self.velocidades[f"{destino}-{origem}"] = self.VELOCIDADE_PADRAO
        
        # Calcular novo tempo com velocidade normal
        tempo_normal = self._calcular_tempo(distancia, self.VELOCIDADE_PADRAO)
        
        # Atualizar grafo
        self.grafo.atualizar_peso(origem, destino, tempo_normal)
        
        # Remover da AVL
        self.avl.remover(id_evento)
        
        return True, (
            f"✅ Evento {id_evento} ({evento.tipo}) removido\n"
            f"   Via {origem}→{destino} normalizada\n"
            f"   🚗 Velocidade restaurada para {self.VELOCIDADE_PADRAO:.0f} km/h\n"
            f"   ⏱️  Tempo: {tempo_normal:.1f} min"
        )
    
    def calcular_rota_rapida(self, origem, destino):
        """
        Calcula a rota de MENOR TEMPO (como Google Maps)
        PODE escolher caminho mais longo em KM se for mais rápido!
        
        Args:
            origem: Vértice de origem
            destino: Vértice de destino
        
        Returns:
            tupla (caminho, info_completa, status)
            info_completa: dict com tempo_total, distancia_total, velocidade_media
        
        Complexidade: O((V + E) log V) - Dijkstra
        """
        caminho, tempo_total = self.grafo.dijkstra(origem, destino)
        
        if caminho is None:
            return None, None, "Não há rota disponível"
        
        # Calcular distância total e outras informações
        distancia_total = 0.0
        segmentos = []
        
        for i in range(len(caminho) - 1):
            o, d = caminho[i], caminho[i + 1]
            info = self.obter_info_via(o, d)
            if info:
                distancia_total += info['distancia_km']
                segmentos.append({
                    'de': o,
                    'para': d,
                    'distancia': info['distancia_km'],
                    'tempo': info['tempo_min'],
                    'velocidade': info['velocidade_kmh']
                })
        
        velocidade_media = (distancia_total / (tempo_total / 60)) if tempo_total > 0 else 0
        
        info_completa = {
            'tempo_total_min': tempo_total,
            'distancia_total_km': distancia_total,
            'velocidade_media_kmh': velocidade_media,
            'segmentos': segmentos
        }
        
        return caminho, info_completa, "OK"
    
    def comparar_rotas(self, origem, destino):
        """
        Compara rota atual (com eventos) vs rota ideal (sem eventos)
        Mostra como eventos podem fazer você escolher caminho MAIS LONGO mas MAIS RÁPIDO!
        
        Args:
            origem: Vértice de origem
            destino: Vértice de destino
        
        Returns:
            dicionário com comparação completa
        """
        # Salvar estado atual
        tempos_temp = {}
        velocidades_temp = {}
        
        for o, destinos in self.grafo.arestas.items():
            for d, tempo in destinos.items():
                tempos_temp[f"{o}-{d}"] = tempo
                chave = f"{o}-{d}"
                if chave in self.velocidades:
                    velocidades_temp[chave] = self.velocidades[chave]
        
        # Restaurar estado sem eventos
        for chave, vel_orig in velocidades_temp.items():
            self.velocidades[chave] = self.VELOCIDADE_PADRAO
        
        for chave, tempo_orig in self.grafo.pesos_originais.items():
            o, d = chave.split('-')
            if o in self.grafo.arestas and d in self.grafo.arestas[o]:
                self.grafo.arestas[o][d] = tempo_orig
        
        # Calcular rota ideal
        caminho_ideal, info_ideal, _ = self.calcular_rota_rapida(origem, destino)
        
        # Restaurar estado com eventos
        for chave, tempo in tempos_temp.items():
            o, d = chave.split('-')
            if o in self.grafo.arestas and d in self.grafo.arestas[o]:
                self.grafo.arestas[o][d] = tempo
        
        for chave, vel in velocidades_temp.items():
            self.velocidades[chave] = vel
        
        # Calcular rota atual
        caminho_atual, info_atual, _ = self.calcular_rota_rapida(origem, destino)
        
        # Análise
        rota_mudou = caminho_ideal != caminho_atual
        
        if info_ideal and info_atual:
            diff_tempo = info_atual['tempo_total_min'] - info_ideal['tempo_total_min']
            diff_distancia = info_atual['distancia_total_km'] - info_ideal['distancia_total_km']
            
            # Descobrir se escolheu rota mais longa por ser mais rápida
            rota_mais_longa_mas_rapida = (diff_distancia > 0 and rota_mudou)
            
            return {
                'rota_ideal': {
                    'caminho': caminho_ideal,
                    'distancia_km': info_ideal['distancia_total_km'],
                    'tempo_min': info_ideal['tempo_total_min'],
                    'velocidade_media': info_ideal['velocidade_media_kmh']
                },
                'rota_atual': {
                    'caminho': caminho_atual,
                    'distancia_km': info_atual['distancia_total_km'],
                    'tempo_min': info_atual['tempo_total_min'],
                    'velocidade_media': info_atual['velocidade_media_kmh']
                },
                'rota_mudou': rota_mudou,
                'rota_mais_longa_mas_rapida': rota_mais_longa_mas_rapida,
                'diferenca_tempo_min': diff_tempo,
                'diferenca_distancia_km': diff_distancia,
                'percentual_atraso': (diff_tempo / info_ideal['tempo_total_min'] * 100) if info_ideal['tempo_total_min'] > 0 else 0
            }
        
        return None
    
    def eventos_na_rota(self, caminho):
        """
        Identifica eventos que afetam uma rota específica
        
        Args:
            caminho: Lista de vértices representando o caminho
        
        Returns:
            lista de eventos que afetam a rota
        """
        if not caminho or len(caminho) < 2:
            return []
        
        eventos_afetando = []
        
        for i in range(len(caminho) - 1):
            origem = caminho[i]
            destino = caminho[i + 1]
            localizacao = f"{origem}-{destino}"
            
            eventos = self.avl.buscar_por_localizacao(localizacao)
            eventos_afetando.extend(eventos)
        
        return eventos_afetando
    
    def analise_detalhada_rota(self, caminho):
        """
        Fornece análise detalhada de uma rota
        Mostra distância, velocidade e tempo de cada segmento
        
        Args:
            caminho: Lista de vértices representando o caminho
        
        Returns:
            dicionário com análise completa
        """
        if not caminho or len(caminho) < 2:
            return None
        
        segmentos = []
        distancia_total = 0.0
        tempo_total = 0.0
        
        for i in range(len(caminho) - 1):
            origem = caminho[i]
            destino = caminho[i + 1]
            
            info = self.obter_info_via(origem, destino)
            if not info:
                continue
            
            # Verificar eventos neste segmento
            eventos = self.avl.buscar_por_localizacao(f"{origem}-{destino}")
            tem_evento = len(eventos) > 0
            
            # Calcular tempo e distância sem evento
            tempo_normal = self._calcular_tempo(info['distancia_km'], self.VELOCIDADE_PADRAO)
            atraso = info['tempo_min'] - tempo_normal
            
            segmento = {
                'de': origem,
                'para': destino,
                'distancia_km': info['distancia_km'],
                'velocidade_kmh': info['velocidade_kmh'],
                'tempo_min': info['tempo_min'],
                'tempo_normal_min': tempo_normal,
                'atraso_min': atraso,
                'eventos': eventos,
                'tem_evento': tem_evento
            }
            
            segmentos.append(segmento)
            distancia_total += info['distancia_km']
            tempo_total += info['tempo_min']
        
        # Calcular tempo sem eventos
        tempo_sem_eventos = sum(s['tempo_normal_min'] for s in segmentos)
        
        # Velocidade média geral
        velocidade_media = (distancia_total / (tempo_total / 60)) if tempo_total > 0 else 0
        
        return {
            'segmentos': segmentos,
            'distancia_total_km': distancia_total,
            'tempo_total_min': tempo_total,
            'tempo_sem_eventos_min': tempo_sem_eventos,
            'atraso_total_min': tempo_total - tempo_sem_eventos,
            'velocidade_media_kmh': velocidade_media,
            'num_segmentos_afetados': sum(1 for s in segmentos if s['tem_evento'])
        }    
    def salvar_dados(self, arquivo_grafo="dados/grafo.txt", arquivo_eventos="dados/eventos.txt"):
        """
        Salva o estado atual do sistema em arquivos
        FORMATO: Salva distâncias e velocidades
        
        Args:
            arquivo_grafo: Caminho para salvar o grafo
            arquivo_eventos: Caminho para salvar os eventos
        
        Returns:
            tupla (sucesso, mensagem)
        """
        try:
            os.makedirs("dados", exist_ok=True)
            
            # Salvar grafo com distâncias e velocidades
            with open(arquivo_grafo, 'w', encoding='utf-8') as f:
                # Linha 1: número de vértices
                f.write(f"{len(self.grafo.vertices)}\n")
                
                # Linha 2: lista de vértices
                f.write(" ".join(sorted(self.grafo.vertices)) + "\n")
                
                # Linha 3: número de arestas
                arestas = self.grafo.obter_todas_arestas()
                f.write(f"{len(arestas)}\n")
                
                # Linhas seguintes: origem destino distancia_km velocidade_kmh
                processadas = set()
                for origem, destino, tempo in arestas:
                    aresta = tuple(sorted([origem, destino]))
                    if aresta in processadas:
                        continue
                    processadas.add(aresta)
                    
                    info = self.obter_info_via(origem, destino)
                    if info:
                        # Pegar velocidade original (sem eventos)
                        vel_original = self.VELOCIDADE_PADRAO
                        f.write(f"{origem} {destino} {info['distancia_km']:.2f} {vel_original:.1f}\n")
            
            # Salvar eventos
            with open(arquivo_eventos, 'w', encoding='utf-8') as f:
                eventos = self.avl.listar_todos()
                f.write(f"{len(eventos)}\n")
                
                for evento in eventos:
                    f.write(f"{evento.id} {evento.timestamp} {evento.tipo} ")
                    f.write(f"{evento.localizacao} {evento.impacto}\n")
            
            return True, "✅ Dados salvos (distâncias em km, velocidades em km/h)"
        
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
        """
        try:
            # Carregar grafo
            with open(arquivo_grafo, 'r', encoding='utf-8') as f:
                n_vertices = int(f.readline().strip())
                vertices = f.readline().strip().split()
                
                for v in vertices:
                    self.grafo.adicionar_vertice(v)
                
                n_arestas = int(f.readline().strip())
                
                for _ in range(n_arestas):
                    partes = f.readline().strip().split()
                    if len(partes) == 4:
                        # Novo formato: origem destino distancia velocidade
                        origem, destino, dist, vel = partes
                        self.adicionar_via(origem, destino, float(dist), float(vel))
                    else:
                        # Formato antigo: origem destino tempo
                        origem, destino, tempo = partes
                        # Assumir velocidade padrão e calcular distância aproximada
                        dist_aprox = (float(tempo) / 60) * self.VELOCIDADE_PADRAO
                        self.adicionar_via(origem, destino, dist_aprox, self.VELOCIDADE_PADRAO)
            
            # Carregar eventos
            if os.path.exists(arquivo_eventos):
                with open(arquivo_eventos, 'r', encoding='utf-8') as f:
                    n_eventos = int(f.readline().strip())
                    max_id = 0
                    
                    for _ in range(n_eventos):
                        partes = f.readline().strip().split()
                        id_ev = int(partes[0])
                        timestamp = int(partes[1])
                        tipo = partes[2]
                        localizacao = partes[3]
                        impacto = float(partes[4])
                        
                        origem, destino = localizacao.split('-')
                        
                        # Registrar evento (isso já atualiza velocidade e tempo)
                        # Mas precisamos manter o ID original
                        old_id = self.proximo_id_evento
                        self.proximo_id_evento = id_ev
                        self.registrar_evento(tipo, origem, destino)
                        
                        max_id = max(max_id, id_ev)
                    
                    self.proximo_id_evento = max_id + 1
            
            return True, "✅ Dados carregados (sistema pronto para uso)"
        
        except FileNotFoundError:
            return False, "❌ Arquivo não encontrado"
        except Exception as e:
            return False, f"❌ Erro ao carregar dados: {str(e)}"
    
    def estatisticas(self):
        """
        Retorna estatísticas do sistema
        
        Returns:
            dicionário com estatísticas
        """
        eventos = self.avl.listar_todos()
        
        por_tipo = {
            'acidente': 0,
            'obra': 0,
            'engarrafamento': 0
        }
        
        for ev in eventos:
            if ev.tipo in por_tipo:
                por_tipo[ev.tipo] += 1
        
        # Calcular total de km da malha
        distancia_total = 0.0
        arestas = self.grafo.obter_todas_arestas()
        processadas = set()
        
        for origem, destino, _ in arestas:
            aresta = tuple(sorted([origem, destino]))
            if aresta not in processadas:
                processadas.add(aresta)
                info = self.obter_info_via(origem, destino)
                if info:
                    distancia_total += info['distancia_km']
        
        return {
            'total_intersecoes': self.grafo.total_vertices(),
            'total_vias': self.grafo.total_arestas(),
            'distancia_total_km': distancia_total,
            'eventos_ativos': self.avl.total_eventos,
            'eventos_por_tipo': por_tipo
        }


# Teste completo demonstrando comportamento tipo Google Maps
if __name__ == "__main__":
    print("=" * 70)
    print("  SISTEMA DE TRÂNSITO INTELIGENTE - ESTILO GOOGLE MAPS 🗺️")
    print("=" * 70)
    print("\n🎯 DEMONSTRAÇÃO: Rota mais longa mas mais rápida!\n")
    
    from avl_tree import ArvoreAVL
    from grafo_ponderado import GrafoPonderado
    
    # Criar sistema
    grafo = GrafoPonderado()
    avl = ArvoreAVL()
    sistema = SistemaTransitoMelhorado(grafo, avl)
    
    # Criar cenário: 2 rotas possíveis
    print("📍 Criando malha viária...\n")
    
    # Rota 1 (curta): A -> B -> C (10 km total)
    sistema.adicionar_via('A', 'B', 5.0, 60.0)   # 5 km a 60 km/h = 5 min
    sistema.adicionar_via('B', 'C', 5.0, 60.0)   # 5 km a 60 km/h = 5 min
    
    # Rota 2 (longa): A -> D -> C (15 km total)
    sistema.adicionar_via('A', 'D', 8.0, 60.0)   # 8 km a 60 km/h = 8 min
    sistema.adicionar_via('D', 'C', 7.0, 60.0)   # 7 km a 60 km/h = 7 min
    
    print("Rotas disponíveis:")
    print("  • Rota 1 (curta): A → B → C = 10 km")
    print("  • Rota 2 (longa): A → D → C = 15 km")
    
    # Calcular rota sem eventos
    print("\n" + "─" * 70)
    print("🚗 SITUAÇÃO NORMAL (sem eventos)")
    print("─" * 70)
    
    caminho1, info1, _ = sistema.calcular_rota_rapida('A', 'C')
    print(f"\n✅ Melhor rota: {' → '.join(caminho1)}")
    print(f"   📏 Distância: {info1['distancia_total_km']:.1f} km")
    print(f"   ⏱️  Tempo: {info1['tempo_total_min']:.1f} minutos")
    print(f"   🚗 Velocidade média: {info1['velocidade_media_kmh']:.0f} km/h")
    
    # Registrar ACIDENTE na rota curta
    print("\n" + "─" * 70)
    print("🚨 REGISTRANDO ACIDENTE NA ROTA CURTA (A-B)")
    print("─" * 70)
    
    sucesso, msg = sistema.registrar_evento('acidente', 'A', 'B')
    print(f"\n{msg}")
    
    # Recalcular rota
    print("\n" + "─" * 70)
    print("🚗 NOVA ROTA CALCULADA (com acidente)")
    print("─" * 70)
    
    caminho2, info2, _ = sistema.calcular_rota_rapida('A', 'C')
    print(f"\n✅ Melhor rota: {' → '.join(caminho2)}")
    print(f"   📏 Distância: {info2['distancia_total_km']:.1f} km")
    print(f"   ⏱️  Tempo: {info2['tempo_total_min']:.1f} minutos")
    print(f"   🚗 Velocidade média: {info2['velocidade_media_kmh']:.0f} km/h")
    
    # Análise da mudança
    print("\n" + "═" * 70)
    print("📊 ANÁLISE DA DECISÃO")
    print("═" * 70)
    
    comp = sistema.comparar_rotas('A', 'C')
    
    if comp['rota_mais_longa_mas_rapida']:
        print("\n🎯 DECISÃO INTELIGENTE!")
        print(f"   O sistema escolheu a rota MAIS LONGA (+{comp['diferenca_distancia_km']:.1f} km)")
        print(f"   porque é MAIS RÁPIDA (-{-comp['diferenca_tempo_min']:.1f} min de economia)")
        print("\n   Exatamente como o Google Maps faria! 🗺️✨")
    else:
        print("\n   Rota mantida (ainda é a mais rápida)")
    
    print("\n" + "─" * 70)
    print("🆚 COMPARAÇÃO DETALHADA")
    print("─" * 70)
    
    print(f"\n📍 Rota Ideal (sem eventos):")
    print(f"   Caminho: {' → '.join(comp['rota_ideal']['caminho'])}")
    print(f"   📏 {comp['rota_ideal']['distancia_km']:.1f} km")
    print(f"   ⏱️  {comp['rota_ideal']['tempo_min']:.1f} min")
    
    print(f"\n📍 Rota Atual (com eventos):")
    print(f"   Caminho: {' → '.join(comp['rota_atual']['caminho'])}")
    print(f"   📏 {comp['rota_atual']['distancia_km']:.1f} km")
    print(f"   ⏱️  {comp['rota_atual']['tempo_min']:.1f} min")
    
    if comp['diferenca_distancia_km'] > 0:
        print(f"\n   📏 {comp['diferenca_distancia_km']:+.1f} km de distância")
    if comp['diferenca_tempo_min'] < 0:
        print(f"   ⏱️  {-comp['diferenca_tempo_min']:.1f} min mais rápida!")
    
    # Análise detalhada
    print("\n" + "─" * 70)
    print("🔍 ANÁLISE DETALHADA DA ROTA ESCOLHIDA")
    print("─" * 70)
    
    analise = sistema.analise_detalhada_rota(caminho2)
    
    print(f"\nResumo:")
    print(f"  • Distância total: {analise['distancia_total_km']:.1f} km")
    print(f"  • Tempo total: {analise['tempo_total_min']:.1f} min")
    print(f"  • Velocidade média: {analise['velocidade_media_kmh']:.0f} km/h")
    print(f"  • Segmentos afetados: {analise['num_segmentos_afetados']}")
    
    print("\nSegmentos:")
    for i, seg in enumerate(analise['segmentos'], 1):
        print(f"\n  {i}. {seg['de']} → {seg['para']}")
        print(f"     📏 {seg['distancia_km']:.1f} km")
        print(f"     🚗 {seg['velocidade_kmh']:.0f} km/h")
        print(f"     ⏱️  {seg['tempo_min']:.1f} min", end="")
        
        if seg['tem_evento']:
            print(f" (+{seg['atraso_min']:.1f} min de atraso)")
            for ev in seg['eventos']:
                print(f"        ⚠️  {ev.tipo.upper()}")
        else:
            print(" ✓")
    
    print("\n" + "═" * 70)
    print("✅ Demonstração concluída!")
    print("═" * 70)
    
    # Estatísticas
    stats = sistema.estatisticas()
    print(f"\n📊 Estatísticas do Sistema:")
    print(f"   • Interseções: {stats['total_intersecoes']}")
    print(f"   • Vias: {stats['total_vias']}")
    print(f"   • Extensão total: {stats['distancia_total_km']:.1f} km")
    print(f"   • Eventos ativos: {stats['eventos_ativos']}")
    print(f"     - Acidentes: {stats['eventos_por_tipo']['acidente']}")
    print(f"     - Obras: {stats['eventos_por_tipo']['obra']}")
    print(f"     - Engarrafamentos: {stats['eventos_por_tipo']['engarrafamento']}")
    
    print("\n" + "=" * 70)

    
    def salvar_dados(self, arquivo_grafo="dados/grafo.txt", arquivo_eventos="dados/eventos.txt"):
        """
        Salva o estado atual do sistema em arquivos
        OBSERVAÇÃO: Agora salva TEMPOS ao invés de distâncias
        
        Args:
            arquivo_grafo: Caminho para salvar o grafo
            arquivo_eventos: Caminho para salvar os eventos
        
        Returns:
            tupla (sucesso, mensagem)
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
                
                # Linhas seguintes: arestas (origem destino tempo_original)
                for origem, destino, tempo in arestas:
                    tempo_orig = self.grafo.obter_peso_original(origem, destino)
                    f.write(f"{origem} {destino} {tempo_orig}\n")
            
            # Salvar eventos
            with open(arquivo_eventos, 'w', encoding='utf-8') as f:
                eventos = self.avl.listar_todos()
                
                # Linha 1: número de eventos
                f.write(f"{len(eventos)}\n")
                
                # Linhas seguintes: eventos (id timestamp tipo localizacao impacto)
                for evento in eventos:
                    f.write(f"{evento.id} {evento.timestamp} {evento.tipo} ")
                    f.write(f"{evento.localizacao} {evento.impacto}\n")
            
            return True, "Dados salvos com sucesso (tempos em minutos)"
        
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
                    origem, destino, tempo = f.readline().strip().split()
                    self.grafo.adicionar_aresta(origem, destino, float(tempo))
            
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
                        
                        # Atualizar tempo no grafo - O(1)
                        origem, destino = localizacao.split('-')
                        tempo_atual = self.grafo.obter_peso(origem, destino)
                        if tempo_atual:
                            self.grafo.atualizar_peso(origem, destino, tempo_atual + impacto)
                        
                        max_id = max(max_id, id_ev)
                    
                    # Atualizar próximo ID
                    self.proximo_id_evento = max_id + 1
            
            return True, "Dados carregados com sucesso (tempos em minutos)"
        
        except FileNotFoundError:
            return False, "Arquivo não encontrado"
        except Exception as e:
            return False, f"Erro ao carregar dados: {str(e)}"
    
    def estatisticas(self):
        """
        Retorna estatísticas do sistema
        
        Returns:
            dicionário com estatísticas
        """
        eventos = self.avl.listar_todos()
        
        # Contar por tipo
        por_tipo = {
            'acidente': 0,
            'obra': 0,
            'engarrafamento': 0
        }
        
        for ev in eventos:
            if ev.tipo in por_tipo:
                por_tipo[ev.tipo] += 1
        
        return {
            'total_intersecoes': self.grafo.total_vertices(),
            'total_vias': self.grafo.total_arestas(),
            'eventos_ativos': self.avl.total_eventos,
            'eventos_por_tipo': por_tipo
        }


# Teste simples
if __name__ == "__main__":
    print("Testando Sistema de Trânsito Melhorado...\n")
    print("AGORA COM FOCO EM TEMPO! ⏱️\n")
    
    from avl_tree import ArvoreAVL
    from grafo_ponderado import GrafoPonderado
    
    # Criar instâncias
    grafo = GrafoPonderado()
    avl = ArvoreAVL()
    sistema = SistemaTransitoMelhorado(grafo, avl)
    
    # Criar malha viária (TEMPOS em minutos)
    print("1. Criando malha viária (tempos em minutos)...")
    grafo.adicionar_aresta('A', 'B', 15.0)  # 15 min
    grafo.adicionar_aresta('B', 'C', 10.0)  # 10 min
    grafo.adicionar_aresta('A', 'C', 30.0)  # 30 min
    print("   ✓ 3 vértices, 3 vias")
    
    # Calcular rota sem eventos
    print("\n2. Rota mais rápida SEM eventos:")
    caminho, tempo, status = sistema.calcular_rota_rapida('A', 'C')
    print(f"   {' → '.join(caminho)}: {tempo:.1f} minutos")
    
    # Registrar diferentes tipos de eventos
    print("\n3. Registrando ACIDENTE em A-B...")
    sucesso, msg = sistema.registrar_evento('acidente', 'A', 'B')
    print(f"   ✓ {msg}")
    
    # Calcular nova rota
    print("\n4. Rota mais rápida COM acidente:")
    caminho2, tempo2, status = sistema.calcular_rota_rapida('A', 'C')
    print(f"   {' → '.join(caminho2)}: {tempo2:.1f} minutos")
    
    if caminho2 != caminho:
        print("   ✓ Sistema encontrou rota alternativa!")
    
    # Comparar rotas
    print("\n5. Comparação de rotas:")
    comp = sistema.comparar_rotas('A', 'C')
    print(f"   Tempo ideal: {comp['rota_ideal'][1]:.1f} min")
    print(f"   Tempo atual: {comp['rota_atual'][1]:.1f} min")
    print(f"   Atraso: +{comp['atraso']:.1f} min ({comp['percentual_atraso']:.1f}%)")
    
    # Testar engarrafamento
    print("\n6. Adicionando ENGARRAFAMENTO em B-C...")
    sistema.registrar_evento('engarrafamento', 'B', 'C')
    
    print("\n7. Nova rota considerando ambos eventos:")
    caminho3, tempo3, status = sistema.calcular_rota_rapida('A', 'C')
    print(f"   {' → '.join(caminho3)}: {tempo3:.1f} minutos")
    
    print("\n✓ Teste concluído!")
    print("\n📊 Estatísticas:")
    stats = sistema.estatisticas()
    print(f"   • Acidentes: {stats['eventos_por_tipo']['acidente']}")
    print(f"   • Obras: {stats['eventos_por_tipo']['obra']}")
    print(f"   • Engarrafamentos: {stats['eventos_por_tipo']['engarrafamento']}")