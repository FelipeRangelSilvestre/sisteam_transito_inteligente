#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Gráfica MELHORADA para o Sistema de Trânsito Inteligente
NOVA VERSÃO: Estilo Google Maps
- Mostra distância em KM
- Mostra tempo em minutos
- Mostra velocidade atual
- Eventos reduzem velocidade
- Prioriza menor tempo (pode escolher rota mais longa!)
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import math
from datetime import datetime

# Importar os módulos do sistema
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Tentar importar os módulos necessários
try:
    # Tentar importar do diretório atual ou src/
    try:
        from avl_tree import ArvoreAVL
    except ImportError:
        from src.avl_tree import ArvoreAVL
    
    try:
        from grafo_ponderado import GrafoPonderado
    except ImportError:
        from src.grafo_ponderado import GrafoPonderado
    
    # Importar o sistema (versão melhorada)
    try:
        from sistema_transito_melhorado import SistemaTransitoMelhorado
    except ImportError:
        try:
            from src.sistema_transito_melhorado import SistemaTransitoMelhorado
        except ImportError:
            # Se não encontrar, usar definição inline
            import time
            
            class SistemaTransitoMelhorado:
                """Sistema de Trânsito Inteligente - Versão Melhorada"""
                
                VELOCIDADE_PADRAO = 60.0
                VELOCIDADES_EVENTO = {
                    'acidente': 10.0,
                    'obra': 20.0,
                    'engarrafamento': 30.0
                }
                
                def __init__(self, grafo, avl):
                    self.grafo = grafo
                    self.avl = avl
                    self.proximo_id_evento = 1
                    self.velocidades = {}
                
                def _calcular_tempo(self, distancia_km, velocidade_kmh):
                    if velocidade_kmh <= 0:
                        return float('inf')
                    return (distancia_km / velocidade_kmh) * 60
                
                def adicionar_via(self, origem, destino, distancia_km, velocidade_kmh=None):
                    if velocidade_kmh is None:
                        velocidade_kmh = self.VELOCIDADE_PADRAO
                    
                    tempo_minutos = self._calcular_tempo(distancia_km, velocidade_kmh)
                    self.grafo.adicionar_aresta(origem, destino, tempo_minutos)
                    
                    self.velocidades[f"{origem}-{destino}"] = velocidade_kmh
                    self.velocidades[f"{destino}-{origem}"] = velocidade_kmh
                    
                    return True
                
                def obter_info_via(self, origem, destino):
                    tempo = self.grafo.obter_peso(origem, destino)
                    velocidade = self.velocidades.get(f"{origem}-{destino}", self.VELOCIDADE_PADRAO)
                    
                    if tempo is None:
                        return None
                    
                    distancia = (tempo / 60) * velocidade
                    
                    return {
                        'distancia_km': distancia,
                        'velocidade_kmh': velocidade,
                        'tempo_min': tempo
                    }
                
                def registrar_evento(self, tipo, origem, destino):
                    if tipo not in ['acidente', 'obra', 'engarrafamento']:
                        return False, "Tipo de evento inválido"
                    
                    info_antes = self.obter_info_via(origem, destino)
                    if info_antes is None:
                        return False, "Via não encontrada"
                    
                    nova_velocidade = self.VELOCIDADES_EVENTO[tipo]
                    velocidade_original = info_antes['velocidade_kmh']
                    distancia = info_antes['distancia_km']
                    
                    novo_tempo = self._calcular_tempo(distancia, nova_velocidade)
                    tempo_original = info_antes['tempo_min']
                    aumento_tempo = novo_tempo - tempo_original
                    
                    timestamp = int(time.time())
                    localizacao = f"{origem}-{destino}"
                    id_evento = self.proximo_id_evento
                    
                    self.avl.inserir(id_evento, timestamp, tipo, localizacao, aumento_tempo)
                    
                    self.velocidades[f"{origem}-{destino}"] = nova_velocidade
                    self.velocidades[f"{destino}-{origem}"] = nova_velocidade
                    
                    self.grafo.atualizar_peso(origem, destino, novo_tempo)
                    
                    self.proximo_id_evento += 1
                    
                    emojis = {
                        'acidente': '🚗💥 ACIDENTE',
                        'obra': '🚧 OBRA',
                        'engarrafamento': '🚦 ENGARRAFAMENTO'
                    }
                    
                    return True, (
                        f"{emojis[tipo]} registrado na via {origem}→{destino}!\n"
                        f"   📏 Distância: {distancia:.1f} km\n"
                        f"   🌀 Velocidade reduzida: {velocidade_original:.0f} → {nova_velocidade:.0f} km/h\n"
                        f"   ⏱️  Tempo: {tempo_original:.1f} → {novo_tempo:.1f} min (+{aumento_tempo:.1f} min)"
                    )
                
                def remover_evento(self, id_evento):
                    evento = self.avl.buscar(id_evento)
                    if not evento:
                        return False, "Evento não encontrado"
                    
                    origem, destino = evento.localizacao.split('-')
                    
                    info = self.obter_info_via(origem, destino)
                    if not info:
                        return False, "Via não encontrada"
                    
                    distancia = info['distancia_km']
                    
                    self.velocidades[f"{origem}-{destino}"] = self.VELOCIDADE_PADRAO
                    self.velocidades[f"{destino}-{origem}"] = self.VELOCIDADE_PADRAO
                    
                    tempo_normal = self._calcular_tempo(distancia, self.VELOCIDADE_PADRAO)
                    self.grafo.atualizar_peso(origem, destino, tempo_normal)
                    
                    self.avl.remover(id_evento)
                    
                    return True, (
                        f"✅ Evento {id_evento} ({evento.tipo}) removido\n"
                        f"   Via {origem}→{destino} normalizada\n"
                        f"   🚗 Velocidade restaurada para {self.VELOCIDADE_PADRAO:.0f} km/h\n"
                        f"   ⏱️  Tempo: {tempo_normal:.1f} min"
                    )
                
                def calcular_rota_rapida(self, origem, destino):
                    caminho, tempo_total = self.grafo.dijkstra(origem, destino)
                    
                    if caminho is None:
                        return None, None, "Não há rota disponível"
                    
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
                    tempos_temp = {}
                    velocidades_temp = {}
                    
                    for o, destinos in self.grafo.arestas.items():
                        for d, tempo in destinos.items():
                            tempos_temp[f"{o}-{d}"] = tempo
                            chave = f"{o}-{d}"
                            if chave in self.velocidades:
                                velocidades_temp[chave] = self.velocidades[chave]
                    
                    for chave in velocidades_temp:
                        self.velocidades[chave] = self.VELOCIDADE_PADRAO
                    
                    if hasattr(self.grafo, 'pesos_originais'):
                        for chave, tempo_orig in self.grafo.pesos_originais.items():
                            o, d = chave.split('-')
                            if o in self.grafo.arestas and d in self.grafo.arestas[o]:
                                self.grafo.arestas[o][d] = tempo_orig
                    
                    caminho_ideal, info_ideal, _ = self.calcular_rota_rapida(origem, destino)
                    
                    for chave, tempo in tempos_temp.items():
                        o, d = chave.split('-')
                        if o in self.grafo.arestas and d in self.grafo.arestas[o]:
                            self.grafo.arestas[o][d] = tempo
                    
                    for chave, vel in velocidades_temp.items():
                        self.velocidades[chave] = vel
                    
                    caminho_atual, info_atual, _ = self.calcular_rota_rapida(origem, destino)
                    
                    rota_mudou = caminho_ideal != caminho_atual
                    
                    if info_ideal and info_atual:
                        diff_tempo = info_atual['tempo_total_min'] - info_ideal['tempo_total_min']
                        diff_distancia = info_atual['distancia_total_km'] - info_ideal['distancia_total_km']
                        
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
                
                def estatisticas(self):
                    eventos = self.avl.listar_todos()
                    
                    por_tipo = {
                        'acidente': 0,
                        'obra': 0,
                        'engarrafamento': 0
                    }
                    
                    for ev in eventos:
                        if ev.tipo in por_tipo:
                            por_tipo[ev.tipo] += 1
                    
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
                
                def salvar_dados(self, arquivo_grafo="dados/grafo.txt", arquivo_eventos="dados/eventos.txt"):
                    try:
                        os.makedirs("dados", exist_ok=True)
                        
                        with open(arquivo_grafo, 'w', encoding='utf-8') as f:
                            f.write(f"{len(self.grafo.vertices)}\n")
                            f.write(" ".join(sorted(self.grafo.vertices)) + "\n")
                            
                            arestas = self.grafo.obter_todas_arestas()
                            f.write(f"{len(arestas)}\n")
                            
                            processadas = set()
                            for origem, destino, tempo in arestas:
                                aresta = tuple(sorted([origem, destino]))
                                if aresta in processadas:
                                    continue
                                processadas.add(aresta)
                                
                                info = self.obter_info_via(origem, destino)
                                if info:
                                    vel_original = self.VELOCIDADE_PADRAO
                                    f.write(f"{origem} {destino} {info['distancia_km']:.2f} {vel_original:.1f}\n")
                        
                        with open(arquivo_eventos, 'w', encoding='utf-8') as f:
                            eventos = self.avl.listar_todos()
                            f.write(f"{len(eventos)}\n")
                            
                            for evento in eventos:
                                f.write(f"{evento.id} {evento.timestamp} {evento.tipo} ")
                                f.write(f"{evento.localizacao} {evento.impacto}\n")
                        
                        return True, "✅ Dados salvos com sucesso!"
                    
                    except Exception as e:
                        return False, f"Erro ao salvar: {str(e)}"
                
                def carregar_dados(self, arquivo_grafo="dados/grafo.txt", arquivo_eventos="dados/eventos.txt"):
                    try:
                        with open(arquivo_grafo, 'r', encoding='utf-8') as f:
                            n_vertices = int(f.readline().strip())
                            vertices = f.readline().strip().split()
                            
                            for v in vertices:
                                self.grafo.adicionar_vertice(v)
                            
                            n_arestas = int(f.readline().strip())
                            
                            for _ in range(n_arestas):
                                partes = f.readline().strip().split()
                                if len(partes) == 4:
                                    origem, destino, dist, vel = partes
                                    self.adicionar_via(origem, destino, float(dist), float(vel))
                                else:
                                    origem, destino, tempo = partes
                                    dist_aprox = (float(tempo) / 60) * self.VELOCIDADE_PADRAO
                                    self.adicionar_via(origem, destino, dist_aprox, self.VELOCIDADE_PADRAO)
                        
                        if os.path.exists(arquivo_eventos):
                            with open(arquivo_eventos, 'r', encoding='utf-8') as f:
                                n_eventos = int(f.readline().strip())
                                max_id = 0
                                
                                for _ in range(n_eventos):
                                    partes = f.readline().strip().split()
                                    id_ev = int(partes[0])
                                    tipo = partes[2]
                                    localizacao = partes[3]
                                    
                                    origem, destino = localizacao.split('-')
                                    
                                    old_id = self.proximo_id_evento
                                    self.proximo_id_evento = id_ev
                                    self.registrar_evento(tipo, origem, destino)
                                    
                                    max_id = max(max_id, id_ev)
                                
                                self.proximo_id_evento = max_id + 1
                        
                        return True, "✅ Dados carregados!"
                    
                    except FileNotFoundError:
                        return False, "❌ Arquivo não encontrado"
                    except Exception as e:
                        return False, f"❌ Erro: {str(e)}"

except ImportError as e:
    import tkinter.messagebox as mb
    mb.showerror("Erro de Importação", 
                 f"Não foi possível importar os módulos necessários.\n\n"
                 f"Verifique se os arquivos existem:\n"
                 f"- avl_tree.py\n"
                 f"- grafo_ponderado.py\n\n"
                 f"Erro: {e}")
    exit()


class InterfaceTransitoMelhorada:
    """Interface gráfica melhorada - Estilo Google Maps"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Trânsito Inteligente - Estilo Google Maps 🗺️")
        self.root.geometry("1400x800")
        self.root.configure(bg="#1a1a2e")
        
        # Inicializar sistema
        self.grafo = GrafoPonderado()
        self.avl = ArvoreAVL()
        self.sistema = SistemaTransitoMelhorado(self.grafo, self.avl)
        
        # Variáveis de controle
        self.vertices_pos = {}
        self.caminho_atual = []
        self.modo_adicionar = None
        self.aresta_origem = None
        
        # Configurar interface
        self.criar_menu()
        self.criar_interface()
        self.criar_dados_exemplo()
        
        # Desenhar após a janela estar visível
        self.root.after(100, self.desenhar_grafo)
    
    def criar_menu(self):
        """Cria a barra de menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        menu_arquivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=menu_arquivo)
        menu_arquivo.add_command(label="Novo", command=self.novo_sistema)
        menu_arquivo.add_command(label="Carregar Dados", command=self.carregar_dados)
        menu_arquivo.add_command(label="Salvar Dados", command=self.salvar_dados)
        menu_arquivo.add_separator()
        menu_arquivo.add_command(label="Sair", command=self.root.quit)
        
        # Menu Malha Viária
        menu_malha = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Malha Viária", menu=menu_malha)
        menu_malha.add_command(label="Adicionar Interseção", command=self.modo_add_vertice)
        menu_malha.add_command(label="Adicionar Via", command=self.modo_add_aresta)
        menu_malha.add_command(label="Remover Via", command=self.remover_via_dialog)
        
        # Menu Eventos
        menu_eventos = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Eventos", menu=menu_eventos)
        menu_eventos.add_command(label="🚗💥 Registrar Acidente", 
                                command=lambda: self.registrar_evento_dialog('acidente'))
        menu_eventos.add_command(label="🚧 Registrar Obra", 
                                command=lambda: self.registrar_evento_dialog('obra'))
        menu_eventos.add_command(label="🚦 Registrar Engarrafamento", 
                                command=lambda: self.registrar_evento_dialog('engarrafamento'))
        menu_eventos.add_separator()
        menu_eventos.add_command(label="Remover Evento", command=self.remover_evento_dialog)
        
        # Menu Ajuda
        menu_ajuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=menu_ajuda)
        menu_ajuda.add_command(label="Como Funciona", command=self.mostrar_como_funciona)
        menu_ajuda.add_command(label="Sobre", command=self.mostrar_sobre)
    
    def criar_interface(self):
        """Cria a interface principal"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#1a1a2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ==== PAINEL ESQUERDO: Canvas do Grafo ====
        left_frame = tk.Frame(main_frame, bg="#16213e", relief=tk.RAISED, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Título
        titulo_canvas = tk.Label(left_frame, text="🗺️ MALHA VIÁRIA", 
                                bg="#16213e", fg="#00d4ff", 
                                font=("Arial", 16, "bold"))
        titulo_canvas.pack(pady=10)
        
        # Canvas
        canvas_frame = tk.Frame(left_frame, bg="#0f3460")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.canvas = tk.Canvas(canvas_frame, bg="#0f3460", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.canvas_click)
        
        # Legenda melhorada
        legenda_frame = tk.Frame(left_frame, bg="#16213e")
        legenda_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(legenda_frame, text="🔵 Interseção Normal | 🟢 Na Rota Escolhida", 
                bg="#16213e", fg="white", font=("Arial", 9)).pack(anchor="w")
        tk.Label(legenda_frame, text="━ Via Normal | ━ Via com Evento | ━ Via na Rota", 
                bg="#16213e", fg="white", font=("Arial", 9)).pack(anchor="w")
        tk.Label(legenda_frame, text="⚠️ Sistema prioriza MENOR TEMPO (pode escolher rota mais longa!)", 
                bg="#16213e", fg="#ff9800", font=("Arial", 9, "bold")).pack(anchor="w", pady=(5,0))
        
        # Botão para redesenhar (debug)
        btn_redesenhar = tk.Button(legenda_frame, text="🔄 Redesenhar Mapa", 
                                   bg="#2196f3", fg="white", font=("Arial", 8, "bold"),
                                   relief=tk.FLAT, cursor="hand2",
                                   command=lambda: self.root.after(10, self.desenhar_grafo))
        btn_redesenhar.pack(pady=(5, 0))
        
        # ==== PAINEL DIREITO: Controles ====
        right_frame = tk.Frame(main_frame, bg="#16213e", relief=tk.RAISED, bd=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_frame.config(width=400)
        
        # Notebook (abas)
        notebook = ttk.Notebook(right_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background="#16213e", borderwidth=0)
        style.configure('TNotebook.Tab', background="#0f3460", foreground="white", 
                       padding=[15, 8], font=("Arial", 10, "bold"))
        style.map('TNotebook.Tab', background=[('selected', '#00d4ff')],
                 foreground=[('selected', 'black')])
        
        # Abas
        self.criar_aba_rotas(notebook)
        self.criar_aba_eventos(notebook)
        self.criar_aba_estatisticas(notebook)
    
    def criar_aba_rotas(self, notebook):
        """Cria a aba de cálculo de rotas"""
        frame = tk.Frame(notebook, bg="#16213e")
        notebook.add(frame, text="🗺️ Rotas")
        
        # Título
        titulo = tk.Label(frame, text="Cálculo de Rotas Inteligente", bg="#16213e", 
                         fg="#00d4ff", font=("Arial", 13, "bold"))
        titulo.pack(pady=15)
        
        # Origem
        tk.Label(frame, text="📍 Origem:", bg="#16213e", fg="white", 
                font=("Arial", 11, "bold")).pack(anchor="w", padx=20, pady=(10, 0))
        self.combo_origem = ttk.Combobox(frame, state="readonly", font=("Arial", 11))
        self.combo_origem.pack(fill=tk.X, padx=20, pady=5)
        
        # Destino
        tk.Label(frame, text="📍 Destino:", bg="#16213e", fg="white", 
                font=("Arial", 11, "bold")).pack(anchor="w", padx=20, pady=(10, 0))
        self.combo_destino = ttk.Combobox(frame, state="readonly", font=("Arial", 11))
        self.combo_destino.pack(fill=tk.X, padx=20, pady=5)
        
        # Botões
        btn_calcular = tk.Button(frame, text="🚗 Calcular Rota Mais Rápida", 
                                bg="#00d4ff", fg="black", font=("Arial", 11, "bold"),
                                relief=tk.FLAT, cursor="hand2", 
                                command=self.calcular_rota, height=2)
        btn_calcular.pack(fill=tk.X, padx=20, pady=15)
        
        btn_comparar = tk.Button(frame, text="📊 Comparar com Rota Ideal", 
                                bg="#ff9800", fg="black", font=("Arial", 11, "bold"),
                                relief=tk.FLAT, cursor="hand2",
                                command=self.comparar_rotas, height=2)
        btn_comparar.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Frame de resultado
        resultado_frame = tk.Frame(frame, bg="#0f3460", relief=tk.RAISED, bd=2)
        resultado_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))
        
        tk.Label(resultado_frame, text="📋 Resultado:", bg="#0f3460", fg="#00d4ff",
                font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=10)
        
        # Text widget com scroll
        text_frame = tk.Frame(resultado_frame, bg="#0f3460")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_resultado = tk.Text(text_frame, height=10, bg="#1a1a2e", 
                                     fg="white", font=("Consolas", 9),
                                     relief=tk.FLAT, padx=10, pady=10,
                                     yscrollcommand=scrollbar.set, wrap=tk.WORD)
        self.text_resultado.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_resultado.yview)
        
        self.text_resultado.insert("1.0", 
            "🎯 Sistema de Rotas Inteligente\n\n"
            "Selecione origem e destino.\n\n"
            "O sistema calcula a rota de MENOR TEMPO,\n"
            "considerando:\n"
            "  • Distância de cada via (km)\n"
            "  • Velocidade atual (km/h)\n"
            "  • Eventos que reduzem velocidade\n\n"
            "Pode escolher rota mais longa se for\n"
            "mais rápida! Igual ao Google Maps! 🗺️")
        self.text_resultado.config(state=tk.DISABLED)
    
    def criar_aba_eventos(self, notebook):
        """Cria a aba de gerenciamento de eventos"""
        frame = tk.Frame(notebook, bg="#16213e")
        notebook.add(frame, text="⚠️ Eventos")
        
        # Título
        titulo = tk.Label(frame, text="Eventos de Trânsito", bg="#16213e",
                         fg="#00d4ff", font=("Arial", 13, "bold"))
        titulo.pack(pady=15)
        
        # Info sobre eventos
        info_frame = tk.Frame(frame, bg="#0f3460", relief=tk.RAISED, bd=2)
        info_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        tk.Label(info_frame, text="💡 Como funcionam os eventos:", 
                bg="#0f3460", fg="#00d4ff", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        tk.Label(info_frame, text="🚗💥 Acidente: Reduz velocidade para 10 km/h", 
                bg="#0f3460", fg="#ff4444", font=("Arial", 9)).pack(anchor="w", padx=10)
        tk.Label(info_frame, text="🚧 Obra: Reduz velocidade para 20 km/h", 
                bg="#0f3460", fg="#ff9800", font=("Arial", 9)).pack(anchor="w", padx=10)
        tk.Label(info_frame, text="🚦 Engarrafamento: Reduz velocidade para 30 km/h", 
                bg="#0f3460", fg="#ffeb3b", font=("Arial", 9)).pack(anchor="w", padx=10, pady=(0, 10))
        
        # Botões de adicionar
        btn_frame = tk.Frame(frame, bg="#16213e")
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        btn_acidente = tk.Button(btn_frame, text="🚗💥\nAcidente", bg="#ff4444", 
                                fg="white", font=("Arial", 10, "bold"),
                                relief=tk.FLAT, cursor="hand2", height=3,
                                command=lambda: self.registrar_evento_dialog('acidente'))
        btn_acidente.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 5))
        
        btn_obra = tk.Button(btn_frame, text="🚧\nObra", bg="#ff9800",
                            fg="white", font=("Arial", 10, "bold"),
                            relief=tk.FLAT, cursor="hand2", height=3,
                            command=lambda: self.registrar_evento_dialog('obra'))
        btn_obra.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        
        btn_engarra = tk.Button(btn_frame, text="🚦\nEngarrafamento", bg="#ffeb3b",
                               fg="black", font=("Arial", 10, "bold"),
                               relief=tk.FLAT, cursor="hand2", height=3,
                               command=lambda: self.registrar_evento_dialog('engarrafamento'))
        btn_engarra.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(5, 0))
        
        # Botão remover
        btn_remover = tk.Button(frame, text="🗑️ Remover Evento", bg="#f44336",
                               fg="white", font=("Arial", 10, "bold"),
                               relief=tk.FLAT, cursor="hand2",
                               command=self.remover_evento_dialog)
        btn_remover.pack(fill=tk.X, padx=20, pady=(10, 15))
        
        # Lista de eventos
        lista_frame = tk.Frame(frame, bg="#0f3460", relief=tk.RAISED, bd=2)
        lista_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        tk.Label(lista_frame, text="📋 Eventos Ativos:", bg="#0f3460", fg="#00d4ff",
                font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=10)
        
        # Scrollbar e Listbox
        scroll_frame = tk.Frame(lista_frame, bg="#0f3460")
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.lista_eventos = tk.Listbox(scroll_frame, bg="#1a1a2e", fg="white",
                                        font=("Consolas", 9), relief=tk.FLAT,
                                        yscrollcommand=scrollbar.set,
                                        selectmode=tk.SINGLE)
        self.lista_eventos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.lista_eventos.yview)
        
        self.atualizar_lista_eventos()
    
    def criar_aba_estatisticas(self, notebook):
        """Cria a aba de estatísticas"""
        frame = tk.Frame(notebook, bg="#16213e")
        notebook.add(frame, text="📊 Stats")
        
        # Título
        titulo = tk.Label(frame, text="Estatísticas do Sistema", bg="#16213e",
                         fg="#00d4ff", font=("Arial", 13, "bold"))
        titulo.pack(pady=15)
        
        # Cards de estatísticas
        cards_frame = tk.Frame(frame, bg="#16213e")
        cards_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Card Interseções
        card1 = tk.Frame(cards_frame, bg="#0f3460", relief=tk.RAISED, bd=2)
        card1.pack(fill=tk.X, pady=5)
        tk.Label(card1, text="📍 Interseções", bg="#0f3460", fg="#00d4ff",
                font=("Arial", 11, "bold")).pack(pady=(15, 5))
        self.label_intersecoes = tk.Label(card1, text="0", bg="#0f3460", fg="white",
                                         font=("Arial", 28, "bold"))
        self.label_intersecoes.pack(pady=(0, 15))
        
        # Card Vias
        card2 = tk.Frame(cards_frame, bg="#0f3460", relief=tk.RAISED, bd=2)
        card2.pack(fill=tk.X, pady=5)
        tk.Label(card2, text="🛣️ Vias", bg="#0f3460", fg="#00d4ff",
                font=("Arial", 11, "bold")).pack(pady=(15, 5))
        self.label_vias = tk.Label(card2, text="0", bg="#0f3460", fg="white",
                                  font=("Arial", 28, "bold"))
        self.label_vias.pack(pady=(0, 15))
        
        # Card Distância Total
        card3 = tk.Frame(cards_frame, bg="#0f3460", relief=tk.RAISED, bd=2)
        card3.pack(fill=tk.X, pady=5)
        tk.Label(card3, text="📏 Extensão Total", bg="#0f3460", fg="#00d4ff",
                font=("Arial", 11, "bold")).pack(pady=(15, 5))
        self.label_distancia = tk.Label(card3, text="0.0 km", bg="#0f3460", fg="white",
                                        font=("Arial", 24, "bold"))
        self.label_distancia.pack(pady=(0, 15))
        
        # Card Eventos
        card4 = tk.Frame(cards_frame, bg="#0f3460", relief=tk.RAISED, bd=2)
        card4.pack(fill=tk.X, pady=5)
        tk.Label(card4, text="⚠️ Eventos Ativos", bg="#0f3460", fg="#00d4ff",
                font=("Arial", 11, "bold")).pack(pady=(15, 5))
        self.label_eventos = tk.Label(card4, text="0", bg="#0f3460", fg="#ff4444",
                                      font=("Arial", 28, "bold"))
        self.label_eventos.pack(pady=(0, 15))
        
        # Detalhes dos eventos
        detalhes_frame = tk.Frame(cards_frame, bg="#0f3460", relief=tk.RAISED, bd=2)
        detalhes_frame.pack(fill=tk.X, pady=5)
        tk.Label(detalhes_frame, text="🔍 Detalhes:", bg="#0f3460", fg="#00d4ff",
                font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.label_acidentes = tk.Label(detalhes_frame, text="  🚗💥 Acidentes: 0", 
                                        bg="#0f3460", fg="#ff4444", font=("Arial", 10))
        self.label_acidentes.pack(anchor="w", padx=10)
        
        self.label_obras = tk.Label(detalhes_frame, text="  🚧 Obras: 0", 
                                    bg="#0f3460", fg="#ff9800", font=("Arial", 10))
        self.label_obras.pack(anchor="w", padx=10)
        
        self.label_engarraf = tk.Label(detalhes_frame, text="  🚦 Engarrafamentos: 0", 
                                       bg="#0f3460", fg="#ffeb3b", font=("Arial", 10))
        self.label_engarraf.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Botão atualizar
        btn_atualizar = tk.Button(frame, text="🔄 Atualizar Estatísticas", bg="#2196f3",
                                 fg="white", font=("Arial", 11, "bold"),
                                 relief=tk.FLAT, cursor="hand2",
                                 command=self.atualizar_estatisticas)
        btn_atualizar.pack(fill=tk.X, padx=20, pady=20)
        
        self.atualizar_estatisticas()
    
    def desenhar_grafo(self):
        """Desenha o grafo no canvas"""
        self.canvas.delete("all")
        
        if not self.grafo.vertices:
            # Pegar dimensões do canvas
            canvas_width = self.canvas.winfo_width() or 800
            canvas_height = self.canvas.winfo_height() or 600
            
            self.canvas.create_text(canvas_width/2, canvas_height/2, 
                text="Clique em 'Malha Viária' > 'Adicionar Interseção'\npara começar",
                fill="white", font=("Arial", 14), justify=tk.CENTER)
            return
        
        if not self.vertices_pos:
            self.calcular_layout_circular()
        
        # Forçar recálculo se canvas foi redimensionado
        canvas_width = self.canvas.winfo_width()
        if canvas_width > 1:  # Canvas já foi renderizado
            self.calcular_layout_circular()
        
        # Desenhar arestas
        arestas = self.grafo.obter_todas_arestas()
        for origem, destino, _ in arestas:
            if origem in self.vertices_pos and destino in self.vertices_pos:
                x1, y1 = self.vertices_pos[origem]
                x2, y2 = self.vertices_pos[destino]
                
                # Obter informações da via
                info = self.sistema.obter_info_via(origem, destino)
                if not info:
                    continue
                
                # Cor e largura
                cor = "#4a5568"
                largura = 2
                
                # Verificar se tem evento
                if info['velocidade_kmh'] < self.sistema.VELOCIDADE_PADRAO:
                    cor = "#ff4444"
                    largura = 3
                
                # Verificar se está na rota
                if self.caminho_atual and origem in self.caminho_atual and destino in self.caminho_atual:
                    idx_o = self.caminho_atual.index(origem)
                    idx_d = self.caminho_atual.index(destino)
                    if abs(idx_o - idx_d) == 1:
                        cor = "#00ff88"
                        largura = 4
                
                # Desenhar linha
                self.canvas.create_line(x1, y1, x2, y2, fill=cor, width=largura, tags="aresta")
                
                # Labels no meio da aresta
                mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                
                # Distância
                self.canvas.create_text(mid_x, mid_y - 15, 
                    text=f"📏 {info['distancia_km']:.1f} km",
                    fill="white", font=("Arial", 8, "bold"), tags="info")
                
                # Velocidade
                vel_cor = "#00ff88" if info['velocidade_kmh'] >= self.sistema.VELOCIDADE_PADRAO else "#ff4444"
                self.canvas.create_text(mid_x, mid_y, 
                    text=f"🚗 {info['velocidade_kmh']:.0f} km/h",
                    fill=vel_cor, font=("Arial", 8, "bold"), tags="info")
                
                # Tempo
                self.canvas.create_text(mid_x, mid_y + 15, 
                    text=f"⏱️ {info['tempo_min']:.1f} min",
                    fill="#00d4ff", font=("Arial", 8, "bold"), tags="info")
        
        # Desenhar vértices
        for vertice, (x, y) in self.vertices_pos.items():
            cor = "#00d4ff"
            if self.caminho_atual and vertice in self.caminho_atual:
                cor = "#00ff88"
            
            raio = 25
            self.canvas.create_oval(x-raio, y-raio, x+raio, y+raio,
                                   fill=cor, outline="white", width=2,
                                   tags=f"vertice_{vertice}")
            
            self.canvas.create_text(x, y, text=vertice, fill="black",
                                   font=("Arial", 12, "bold"),
                                   tags=f"vertice_{vertice}")
    
    def calcular_layout_circular(self):
        """Calcula posições dos vértices em layout circular"""
        vertices = sorted(self.grafo.vertices)
        n = len(vertices)
        
        if n == 0:
            return
        
        canvas_width = self.canvas.winfo_width() or 900
        canvas_height = self.canvas.winfo_height() or 700
        centro_x = canvas_width / 2
        centro_y = canvas_height / 2
        raio = min(canvas_width, canvas_height) * 0.35
        
        for i, vertice in enumerate(vertices):
            angulo = 2 * math.pi * i / n - math.pi / 2
            x = centro_x + raio * math.cos(angulo)
            y = centro_y + raio * math.sin(angulo)
            self.vertices_pos[vertice] = (x, y)
    
    def canvas_click(self, event):
        """Manipula clique no canvas"""
        if self.modo_adicionar == 'vertice':
            self.adicionar_vertice_pos(event.x, event.y)
        elif self.modo_adicionar == 'aresta':
            self.selecionar_vertice_aresta(event.x, event.y)
    
    def modo_add_vertice(self):
        """Ativa modo de adicionar vértice"""
        nome = simpledialog.askstring("Nova Interseção", 
                                      "Nome da interseção:",
                                      parent=self.root)
        if nome:
            nome = nome.strip().upper()
            if nome in self.grafo.vertices:
                messagebox.showwarning("Aviso", f"Interseção '{nome}' já existe!")
                return
            
            self.modo_adicionar = 'vertice'
            self.vertice_temp = nome
            messagebox.showinfo("Adicionar Interseção",
                              f"Clique no canvas para posicionar '{nome}'")
    
    def adicionar_vertice_pos(self, x, y):
        """Adiciona vértice na posição clicada"""
        if hasattr(self, 'vertice_temp'):
            self.grafo.adicionar_vertice(self.vertice_temp)
            self.vertices_pos[self.vertice_temp] = (x, y)
            self.modo_adicionar = None
            delattr(self, 'vertice_temp')
            self.atualizar_interface()
    
    def modo_add_aresta(self):
        """Ativa modo de adicionar aresta"""
        if len(self.grafo.vertices) < 2:
            messagebox.showwarning("Aviso", "É necessário ter pelo menos 2 interseções!")
            return
        
        self.modo_adicionar = 'aresta'
        self.aresta_origem = None
        messagebox.showinfo("Adicionar Via",
                          "Clique na interseção de ORIGEM da via")
    
    def selecionar_vertice_aresta(self, x, y):
        """Seleciona vértices para criar aresta"""
        # Encontrar vértice clicado
        vertice_clicado = None
        for vertice, (vx, vy) in self.vertices_pos.items():
            distancia = math.sqrt((x - vx)**2 + (y - vy)**2)
            if distancia <= 25:
                vertice_clicado = vertice
                break
        
        if not vertice_clicado:
            return
        
        if self.aresta_origem is None:
            self.aresta_origem = vertice_clicado
            messagebox.showinfo("Via", 
                              f"Origem: {vertice_clicado}\n\nAgora clique na interseção de DESTINO")
        else:
            if vertice_clicado == self.aresta_origem:
                messagebox.showwarning("Aviso", "Selecione uma interseção diferente!")
                return
            
            # Verificar se aresta já existe
            if self.grafo.obter_peso(self.aresta_origem, vertice_clicado):
                messagebox.showwarning("Aviso", "Esta via já existe!")
                self.aresta_origem = None
                self.modo_adicionar = None
                return
            
            # Solicitar distância e velocidade
            self.adicionar_aresta_dialog(self.aresta_origem, vertice_clicado)
            self.aresta_origem = None
            self.modo_adicionar = None
    
    def adicionar_aresta_dialog(self, origem, destino):
        """Dialog para adicionar aresta com distância e velocidade"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Nova Via")
        dialog.geometry("400x300")
        dialog.configure(bg="#16213e")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        tk.Label(dialog, text=f"Nova Via: {origem} ↔ {destino}", 
                bg="#16213e", fg="#00d4ff", font=("Arial", 12, "bold")).pack(pady=20)
        
        # Distância
        frame_dist = tk.Frame(dialog, bg="#16213e")
        frame_dist.pack(pady=10)
        tk.Label(frame_dist, text="📏 Distância (km):", bg="#16213e", 
                fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
        entry_dist = tk.Entry(frame_dist, font=("Arial", 10), width=15)
        entry_dist.pack(side=tk.LEFT)
        entry_dist.insert(0, "5.0")
        
        # Velocidade
        frame_vel = tk.Frame(dialog, bg="#16213e")
        frame_vel.pack(pady=10)
        tk.Label(frame_vel, text="🚗 Velocidade (km/h):", bg="#16213e", 
                fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
        entry_vel = tk.Entry(frame_vel, font=("Arial", 10), width=15)
        entry_vel.pack(side=tk.LEFT)
        entry_vel.insert(0, "60")
        
        def confirmar():
            try:
                dist = float(entry_dist.get())
                vel = float(entry_vel.get())
                
                if dist <= 0 or vel <= 0:
                    messagebox.showerror("Erro", "Valores devem ser positivos!")
                    return
                
                self.sistema.adicionar_via(origem, destino, dist, vel)
                dialog.destroy()
                self.atualizar_interface()
                messagebox.showinfo("Sucesso", 
                    f"Via adicionada!\n📏 {dist} km\n🚗 {vel} km/h\n⏱️ {(dist/vel)*60:.1f} min")
            except ValueError:
                messagebox.showerror("Erro", "Valores inválidos!")
        
        btn_frame = tk.Frame(dialog, bg="#16213e")
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="✓ Adicionar", bg="#00d4ff", fg="black",
                 font=("Arial", 10, "bold"), command=confirmar, 
                 width=12, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="✗ Cancelar", bg="#f44336", fg="white",
                 font=("Arial", 10, "bold"), command=dialog.destroy,
                 width=12, cursor="hand2").pack(side=tk.LEFT, padx=5)
    
    def remover_via_dialog(self):
        """Dialog para remover via"""
        if not self.grafo.vertices:
            messagebox.showwarning("Aviso", "Não há vias no sistema!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Remover Via")
        dialog.geometry("400x300")
        dialog.configure(bg="#16213e")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Selecione a via para remover", 
                bg="#16213e", fg="#00d4ff", font=("Arial", 12, "bold")).pack(pady=20)
        
        # Lista de vias
        frame_lista = tk.Frame(dialog, bg="#16213e")
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        lista = tk.Listbox(frame_lista, bg="#1a1a2e", fg="white", 
                          font=("Consolas", 10), yscrollcommand=scrollbar.set)
        lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=lista.yview)
        
        # Preencher lista
        vias = []
        processadas = set()
        for origem, destino, _ in self.grafo.obter_todas_arestas():
            par = tuple(sorted([origem, destino]))
            if par not in processadas:
                processadas.add(par)
                info = self.sistema.obter_info_via(origem, destino)
                if info:
                    vias.append((origem, destino))
                    lista.insert(tk.END, f"{origem} ↔ {destino} ({info['distancia_km']:.1f} km)")
        
        def remover():
            sel = lista.curselection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecione uma via!")
                return
            
            origem, destino = vias[sel[0]]
            self.grafo.remover_aresta(origem, destino)
            dialog.destroy()
            self.atualizar_interface()
            messagebox.showinfo("Sucesso", f"Via {origem} ↔ {destino} removida!")
        
        tk.Button(dialog, text="🗑️ Remover Via", bg="#f44336", fg="white",
                 font=("Arial", 10, "bold"), command=remover).pack(pady=10)
    
    def registrar_evento_dialog(self, tipo):
        """Dialog para registrar evento"""
        if not self.grafo.vertices:
            messagebox.showwarning("Aviso", "Não há vias no sistema!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Registrar {tipo.title()}")
        dialog.geometry("400x300")
        dialog.configure(bg="#16213e")
        dialog.transient(self.root)
        dialog.grab_set()
        
        emojis = {'acidente': '🚗💥', 'obra': '🚧', 'engarrafamento': '🚦'}
        
        tk.Label(dialog, text=f"{emojis[tipo]} Registrar {tipo.title()}", 
                bg="#16213e", fg="#00d4ff", font=("Arial", 12, "bold")).pack(pady=20)
        
        tk.Label(dialog, text="Selecione a via afetada:", bg="#16213e", 
                fg="white", font=("Arial", 10)).pack(pady=5)
        
        # Lista de vias
        frame_lista = tk.Frame(dialog, bg="#16213e")
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        lista = tk.Listbox(frame_lista, bg="#1a1a2e", fg="white", 
                          font=("Consolas", 10), yscrollcommand=scrollbar.set)
        lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=lista.yview)
        
        # Preencher lista
        vias = []
        processadas = set()
        for origem, destino, _ in self.grafo.obter_todas_arestas():
            par = tuple(sorted([origem, destino]))
            if par not in processadas:
                processadas.add(par)
                info = self.sistema.obter_info_via(origem, destino)
                if info:
                    vias.append((origem, destino))
                    lista.insert(tk.END, f"{origem} → {destino} ({info['distancia_km']:.1f} km)")
        
        def registrar():
            sel = lista.curselection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecione uma via!")
                return
            
            origem, destino = vias[sel[0]]
            sucesso, msg = self.sistema.registrar_evento(tipo, origem, destino)
            
            if sucesso:
                dialog.destroy()
                self.atualizar_interface()
                messagebox.showinfo("Evento Registrado", msg)
            else:
                messagebox.showerror("Erro", msg)
        
        tk.Button(dialog, text=f"{emojis[tipo]} Registrar", bg="#ff9800", fg="white",
                 font=("Arial", 10, "bold"), command=registrar).pack(pady=10)
    
    def remover_evento_dialog(self):
        """Dialog para remover evento"""
        eventos = self.avl.listar_todos()
        
        if not eventos:
            messagebox.showinfo("Info", "Não há eventos ativos!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Remover Evento")
        dialog.geometry("450x350")
        dialog.configure(bg="#16213e")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Selecione o evento para remover", 
                bg="#16213e", fg="#00d4ff", font=("Arial", 12, "bold")).pack(pady=20)
        
        # Lista de eventos
        frame_lista = tk.Frame(dialog, bg="#16213e")
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        lista = tk.Listbox(frame_lista, bg="#1a1a2e", fg="white", 
                          font=("Consolas", 9), yscrollcommand=scrollbar.set)
        lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=lista.yview)
        
        # Preencher lista
        emojis = {'acidente': '🚗💥', 'obra': '🚧', 'engarrafamento': '🚦'}
        for ev in eventos:
            emoji = emojis.get(ev.tipo, '⚠️')
            lista.insert(tk.END, f"#{ev.id} {emoji} {ev.tipo.upper()} - {ev.localizacao}")
        
        def remover():
            sel = lista.curselection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecione um evento!")
                return
            
            evento = eventos[sel[0]]
            sucesso, msg = self.sistema.remover_evento(evento.id)
            
            if sucesso:
                dialog.destroy()
                self.atualizar_interface()
                messagebox.showinfo("Evento Removido", msg)
            else:
                messagebox.showerror("Erro", msg)
        
        tk.Button(dialog, text="🗑️ Remover Evento", bg="#f44336", fg="white",
                 font=("Arial", 10, "bold"), command=remover).pack(pady=10)
    
    def calcular_rota(self):
        """Calcula rota mais rápida"""
        origem = self.combo_origem.get()
        destino = self.combo_destino.get()
        
        if not origem or not destino:
            messagebox.showwarning("Aviso", "Selecione origem e destino!")
            return
        
        if origem == destino:
            messagebox.showwarning("Aviso", "Origem e destino devem ser diferentes!")
            return
        
        caminho, info, status = self.sistema.calcular_rota_rapida(origem, destino)
        
        self.text_resultado.config(state=tk.NORMAL)
        self.text_resultado.delete("1.0", tk.END)
        
        if caminho is None:
            self.text_resultado.insert("1.0", f"❌ {status}\n\nNão há rota disponível.")
            self.caminho_atual = []
        else:
            self.caminho_atual = caminho
            
            resultado = f"🎯 ROTA MAIS RÁPIDA ENCONTRADA!\n\n"
            resultado += f"📍 {origem} → {destino}\n"
            resultado += f"{'═' * 35}\n\n"
            resultado += f"🛣️  Caminho: {' → '.join(caminho)}\n\n"
            resultado += f"📏 Distância Total: {info['distancia_total_km']:.1f} km\n"
            resultado += f"⏱️  Tempo Total: {info['tempo_total_min']:.1f} min\n"
            resultado += f"🚗 Velocidade Média: {info['velocidade_media_kmh']:.0f} km/h\n\n"
            resultado += f"{'─' * 35}\n"
            resultado += f"SEGMENTOS DA ROTA:\n"
            resultado += f"{'─' * 35}\n\n"
            
            for i, seg in enumerate(info['segmentos'], 1):
                resultado += f"{i}. {seg['de']} → {seg['para']}\n"
                resultado += f"   📏 {seg['distancia']:.1f} km\n"
                resultado += f"   🚗 {seg['velocidade']:.0f} km/h\n"
                resultado += f"   ⏱️  {seg['tempo']:.1f} min\n\n"
            
            self.text_resultado.insert("1.0", resultado)
        
        self.text_resultado.config(state=tk.DISABLED)
        self.desenhar_grafo()
    
    def comparar_rotas(self):
        """Compara rota atual com rota ideal"""
        origem = self.combo_origem.get()
        destino = self.combo_destino.get()
        
        if not origem or not destino:
            messagebox.showwarning("Aviso", "Selecione origem e destino!")
            return
        
        if origem == destino:
            messagebox.showwarning("Aviso", "Origem e destino devem ser diferentes!")
            return
        
        comp = self.sistema.comparar_rotas(origem, destino)
        
        if not comp:
            messagebox.showerror("Erro", "Não foi possível comparar rotas!")
            return
        
        self.text_resultado.config(state=tk.NORMAL)
        self.text_resultado.delete("1.0", tk.END)
        
        resultado = f"📊 COMPARAÇÃO DE ROTAS\n\n"
        resultado += f"📍 {origem} → {destino}\n"
        resultado += f"{'═' * 35}\n\n"
        
        resultado += f"🌟 ROTA IDEAL (sem eventos):\n"
        resultado += f"   Caminho: {' → '.join(comp['rota_ideal']['caminho'])}\n"
        resultado += f"   📏 {comp['rota_ideal']['distancia_km']:.1f} km\n"
        resultado += f"   ⏱️  {comp['rota_ideal']['tempo_min']:.1f} min\n\n"
        
        resultado += f"🚗 ROTA ATUAL (com eventos):\n"
        resultado += f"   Caminho: {' → '.join(comp['rota_atual']['caminho'])}\n"
        resultado += f"   📏 {comp['rota_atual']['distancia_km']:.1f} km\n"
        resultado += f"   ⏱️  {comp['rota_atual']['tempo_min']:.1f} min\n\n"
        
        resultado += f"{'─' * 35}\n"
        resultado += f"ANÁLISE:\n"
        resultado += f"{'─' * 35}\n\n"
        
        if comp['rota_mudou']:
            resultado += f"⚠️  ROTA ALTERADA!\n\n"
            
            if comp['rota_mais_longa_mas_rapida']:
                resultado += f"🎯 DECISÃO INTELIGENTE:\n"
                resultado += f"Sistema escolheu rota mais LONGA\n"
                resultado += f"(+{comp['diferenca_distancia_km']:.1f} km)\n"
                resultado += f"porque é mais RÁPIDA!\n"
                resultado += f"({-comp['diferenca_tempo_min']:.1f} min economizados)\n\n"
                resultado += f"Igual ao Google Maps! 🗺️✨\n\n"
            else:
                resultado += f"Diferença de distância:\n"
                resultado += f"{comp['diferenca_distancia_km']:+.1f} km\n\n"
        else:
            resultado += f"✓ Mesma rota mantida\n\n"
        
        if comp['diferenca_tempo_min'] > 0:
            resultado += f"⏱️  Atraso: +{comp['diferenca_tempo_min']:.1f} min\n"
            resultado += f"📊 Aumento: {comp['percentual_atraso']:.1f}%\n"
        elif comp['diferenca_tempo_min'] < 0:
            resultado += f"⏱️  Economia: {-comp['diferenca_tempo_min']:.1f} min\n"
        
        self.text_resultado.insert("1.0", resultado)
        self.text_resultado.config(state=tk.DISABLED)
        
        self.caminho_atual = comp['rota_atual']['caminho']
        self.desenhar_grafo()
    
    def atualizar_lista_eventos(self):
        """Atualiza lista de eventos ativos"""
        self.lista_eventos.delete(0, tk.END)
        
        eventos = self.avl.listar_todos()
        if not eventos:
            self.lista_eventos.insert(tk.END, "  Nenhum evento ativo")
            return
        
        emojis = {'acidente': '🚗💥', 'obra': '🚧', 'engarrafamento': '🚦'}
        
        for ev in eventos:
            emoji = emojis.get(ev.tipo, '⚠️')
            texto = f"#{ev.id} {emoji} {ev.tipo.upper()}"
            self.lista_eventos.insert(tk.END, texto)
            self.lista_eventos.insert(tk.END, f"     Via: {ev.localizacao}")
            self.lista_eventos.insert(tk.END, "")
    
    def atualizar_estatisticas(self):
        """Atualiza estatísticas do sistema"""
        stats = self.sistema.estatisticas()
        
        self.label_intersecoes.config(text=str(stats['total_intersecoes']))
        self.label_vias.config(text=str(stats['total_vias']))
        self.label_distancia.config(text=f"{stats['distancia_total_km']:.1f} km")
        self.label_eventos.config(text=str(stats['eventos_ativos']))
        
        self.label_acidentes.config(text=f"  🚗💥 Acidentes: {stats['eventos_por_tipo']['acidente']}")
        self.label_obras.config(text=f"  🚧 Obras: {stats['eventos_por_tipo']['obra']}")
        self.label_engarraf.config(text=f"  🚦 Engarrafamentos: {stats['eventos_por_tipo']['engarrafamento']}")
    
    def atualizar_interface(self):
        """Atualiza toda a interface"""
        # Atualizar combos
        vertices = sorted(self.grafo.vertices)
        self.combo_origem['values'] = vertices
        self.combo_destino['values'] = vertices
        
        # Atualizar desenho
        self.desenhar_grafo()
        
        # Atualizar listas
        self.atualizar_lista_eventos()
        self.atualizar_estatisticas()
    
    def criar_dados_exemplo(self):
        """Cria dados de exemplo"""
        # Adicionar interseções
        intersecoes = ['A', 'B', 'C', 'D', 'E']
        for i in intersecoes:
            self.grafo.adicionar_vertice(i)
        
        # Adicionar vias
        self.sistema.adicionar_via('A', 'B', 5.0, 60.0)
        self.sistema.adicionar_via('B', 'C', 3.0, 60.0)
        self.sistema.adicionar_via('C', 'D', 4.0, 60.0)
        self.sistema.adicionar_via('D', 'E', 6.0, 60.0)
        self.sistema.adicionar_via('A', 'D', 8.0, 60.0)
        self.sistema.adicionar_via('B', 'E', 10.0, 60.0)
        
        # Forçar atualização após criar dados
        self.root.update_idletasks()
        self.calcular_layout_circular()
        self.atualizar_interface()
    
    def novo_sistema(self):
        """Cria novo sistema vazio"""
        if messagebox.askyesno("Confirmar", "Deseja criar um novo sistema? Dados atuais serão perdidos."):
            self.grafo = GrafoPonderado()
            self.avl = ArvoreAVL()
            self.sistema = SistemaTransitoMelhorado(self.grafo, self.avl)
            self.vertices_pos = {}
            self.caminho_atual = []
            self.atualizar_interface()
            messagebox.showinfo("Sucesso", "Novo sistema criado!")
    
    def salvar_dados(self):
        """Salva dados do sistema"""
        sucesso, msg = self.sistema.salvar_dados()
        if sucesso:
            messagebox.showinfo("Salvar", msg)
        else:
            messagebox.showerror("Erro", msg)
    
    def carregar_dados(self):
        """Carrega dados do sistema"""
        sucesso, msg = self.sistema.carregar_dados()
        if sucesso:
            self.vertices_pos = {}
            self.atualizar_interface()
            messagebox.showinfo("Carregar", msg)
        else:
            messagebox.showerror("Erro", msg)
    
    def mostrar_como_funciona(self):
        """Mostra informações sobre como funciona o sistema"""
        info = """
🗺️ SISTEMA DE TRÂNSITO INTELIGENTE

Como Funciona:

1️⃣ MALHA VIÁRIA:
   • Cada via tem distância (km) e velocidade (km/h)
   • Sistema calcula tempo automaticamente
   
2️⃣ EVENTOS DE TRÂNSITO:
   🚗💥 Acidente: reduz para 10 km/h
   🚧 Obra: reduz para 20 km/h
   🚦 Engarrafamento: reduz para 30 km/h
   
3️⃣ CÁLCULO DE ROTAS:
   • Usa algoritmo de Dijkstra
   • Prioriza MENOR TEMPO (não menor distância!)
   • Pode escolher rota mais longa se for mais rápida
   • Igual ao Google Maps! 🎯

4️⃣ ESTRUTURAS DE DADOS:
   • Grafo Ponderado: malha viária
   • Árvore AVL: eventos organizados por ID
   
Dica: Experimente adicionar eventos e veja
como o sistema recalcula rotas inteligentemente!
        """
        messagebox.showinfo("Como Funciona", info)
    
    def mostrar_sobre(self):
        """Mostra informações sobre o sistema"""
        sobre = """
🗺️ SISTEMA DE TRÂNSITO INTELIGENTE
Versão 2.0 - Estilo Google Maps

Desenvolvido com:
• Python 3
• Tkinter (Interface Gráfica)
• Estruturas de Dados Avançadas

Estruturas Utilizadas:
• Grafo Ponderado com Dijkstra
• Árvore AVL para eventos
• Interface moderna e intuitiva

Funcionalidades:
✓ Gerenciamento de malha viária
✓ Registro de eventos de trânsito
✓ Cálculo de rotas inteligentes
✓ Comparação de rotas
✓ Estatísticas em tempo real

© 2024 - Sistema Acadêmico
        """
        messagebox.showinfo("Sobre", sobre)


def main():
    """Função principal"""
    root = tk.Tk()
    app = InterfaceTransitoMelhorada(root)
    root.mainloop()


if __name__ == "__main__":
    main()