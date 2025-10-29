#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Gráfica para o Sistema de Trânsito Inteligente
Desenvolvido com Tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import math
from datetime import datetime

# Importar os módulos do sistema
import sys
import os

# Adicionar pasta src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from avl_tree import ArvoreAVL
    from grafo_ponderado import GrafoPonderado
    from sistema_transito import SistemaTransito
except ImportError as e:
    import tkinter.messagebox as mb
    mb.showerror("Erro de Importação", 
                 f"Não foi possível importar os módulos do sistema.\n\n"
                 f"Erro: {e}\n\n"
                 f"Certifique-se de que os arquivos estão em:\n"
                 f"- src/avl_tree.py\n"
                 f"- src/grafo_ponderado.py\n"
                 f"- src/sistema_transito.py")
    exit()


class InterfaceTransito:
    """Interface gráfica principal do sistema"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Trânsito Inteligente")
        self.root.geometry("1200x700")
        self.root.configure(bg="#1a1a2e")
        
        # Inicializar sistema
        self.grafo = GrafoPonderado()
        self.avl = ArvoreAVL()
        self.sistema = SistemaTransito(self.grafo, self.avl)
        
        # Variáveis de controle
        self.vertices_pos = {}  # Posições dos vértices no canvas
        self.caminho_atual = []  # Caminho destacado
        self.modo_adicionar = None  # 'vertice' ou 'aresta'
        self.aresta_origem = None  # Para criar arestas
        
        # Configurar interface
        self.criar_menu()
        self.criar_interface()
        self.criar_dados_exemplo()
        self.desenhar_grafo()
    
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
        menu_eventos.add_command(label="Registrar Evento", command=self.registrar_evento_dialog)
        menu_eventos.add_command(label="Remover Evento", command=self.remover_evento_dialog)
        
        # Menu Ajuda
        menu_ajuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=menu_ajuda)
        menu_ajuda.add_command(label="Sobre", command=self.mostrar_sobre)
    
    def criar_interface(self):
        """Cria a interface principal"""
        # Frame principal com divisão
        main_frame = tk.Frame(self.root, bg="#1a1a2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ==== PAINEL ESQUERDO: Canvas do Grafo ====
        left_frame = tk.Frame(main_frame, bg="#16213e", relief=tk.RAISED, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Título do canvas
        titulo_canvas = tk.Label(left_frame, text="📍 MALHA VIÁRIA", 
                                 bg="#16213e", fg="#00d4ff", 
                                 font=("Arial", 14, "bold"))
        titulo_canvas.pack(pady=10)
        
        # Canvas para desenhar o grafo
        canvas_frame = tk.Frame(left_frame, bg="#0f3460")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.canvas = tk.Canvas(canvas_frame, bg="#0f3460", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.canvas_click)
        
        # Legenda
        legenda_frame = tk.Frame(left_frame, bg="#16213e")
        legenda_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(legenda_frame, text="● Interseção Normal", 
                bg="#16213e", fg="#00d4ff", font=("Arial", 9)).pack(anchor="w")
        tk.Label(legenda_frame, text="● Interseção na Rota", 
                bg="#16213e", fg="#00ff88", font=("Arial", 9)).pack(anchor="w")
        tk.Label(legenda_frame, text="━ Via Normal", 
                bg="#16213e", fg="#4a5568", font=("Arial", 9)).pack(anchor="w")
        tk.Label(legenda_frame, text="━ Via com Evento", 
                bg="#16213e", fg="#ff4444", font=("Arial", 9)).pack(anchor="w")
        tk.Label(legenda_frame, text="━ Via na Rota", 
                bg="#16213e", fg="#00ff88", font=("Arial", 9)).pack(anchor="w")
        
        # ==== PAINEL DIREITO: Controles ====
        right_frame = tk.Frame(main_frame, bg="#16213e", relief=tk.RAISED, bd=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_frame.config(width=350)
        
        # Notebook (abas)
        notebook = ttk.Notebook(right_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configurar estilo do notebook
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background="#16213e", borderwidth=0)
        style.configure('TNotebook.Tab', background="#0f3460", foreground="white", 
                       padding=[20, 10], font=("Arial", 10, "bold"))
        style.map('TNotebook.Tab', background=[('selected', '#00d4ff')],
                 foreground=[('selected', 'black')])
        
        # Aba 1: Rotas
        self.criar_aba_rotas(notebook)
        
        # Aba 2: Eventos
        self.criar_aba_eventos(notebook)
        
        # Aba 3: Estatísticas
        self.criar_aba_estatisticas(notebook)
    
    def criar_aba_rotas(self, notebook):
        """Cria a aba de cálculo de rotas"""
        frame = tk.Frame(notebook, bg="#16213e")
        notebook.add(frame, text="🚗 Rotas")
        
        # Título
        titulo = tk.Label(frame, text="Cálculo de Rotas", bg="#16213e", 
                         fg="#00d4ff", font=("Arial", 12, "bold"))
        titulo.pack(pady=10)
        
        # Origem
        tk.Label(frame, text="Origem:", bg="#16213e", fg="white", 
                font=("Arial", 10)).pack(anchor="w", padx=20, pady=(10, 0))
        self.combo_origem = ttk.Combobox(frame, state="readonly", font=("Arial", 10))
        self.combo_origem.pack(fill=tk.X, padx=20, pady=5)
        
        # Destino
        tk.Label(frame, text="Destino:", bg="#16213e", fg="white", 
                font=("Arial", 10)).pack(anchor="w", padx=20, pady=(10, 0))
        self.combo_destino = ttk.Combobox(frame, state="readonly", font=("Arial", 10))
        self.combo_destino.pack(fill=tk.X, padx=20, pady=5)
        
        # Botão calcular
        btn_calcular = tk.Button(frame, text="🔍 Calcular Rota Ótima", 
                                bg="#00d4ff", fg="black", font=("Arial", 11, "bold"),
                                relief=tk.FLAT, cursor="hand2", 
                                command=self.calcular_rota)
        btn_calcular.pack(fill=tk.X, padx=20, pady=15)
        
        # Botão comparar
        btn_comparar = tk.Button(frame, text="📊 Comparar Rotas", 
                                bg="#ff9800", fg="black", font=("Arial", 11, "bold"),
                                relief=tk.FLAT, cursor="hand2",
                                command=self.comparar_rotas)
        btn_comparar.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Frame de resultado
        resultado_frame = tk.Frame(frame, bg="#0f3460", relief=tk.RAISED, bd=2)
        resultado_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))
        
        tk.Label(resultado_frame, text="Resultado:", bg="#0f3460", fg="#00d4ff",
                font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=10)
        
        # Text widget para mostrar resultado
        self.text_resultado = tk.Text(resultado_frame, height=12, bg="#1a1a2e", 
                                     fg="white", font=("Courier", 9),
                                     relief=tk.FLAT, padx=10, pady=10)
        self.text_resultado.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.text_resultado.insert("1.0", "Aguardando cálculo...\n\n"
                                          "Selecione origem e destino,\n"
                                          "depois clique em Calcular.")
        self.text_resultado.config(state=tk.DISABLED)
    
    def criar_aba_eventos(self, notebook):
        """Cria a aba de gerenciamento de eventos"""
        frame = tk.Frame(notebook, bg="#16213e")
        notebook.add(frame, text="⚠️ Eventos")
        
        # Título
        titulo = tk.Label(frame, text="Eventos de Trânsito", bg="#16213e",
                         fg="#00d4ff", font=("Arial", 12, "bold"))
        titulo.pack(pady=10)
        
        # Frame de controles
        controles = tk.Frame(frame, bg="#16213e")
        controles.pack(fill=tk.X, padx=20, pady=10)
        
        btn_add = tk.Button(controles, text="➕ Adicionar", bg="#4caf50", 
                           fg="white", font=("Arial", 10, "bold"),
                           relief=tk.FLAT, cursor="hand2",
                           command=self.registrar_evento_dialog)
        btn_add.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        btn_rem = tk.Button(controles, text="➖ Remover", bg="#f44336",
                           fg="white", font=("Arial", 10, "bold"),
                           relief=tk.FLAT, cursor="hand2",
                           command=self.remover_evento_dialog)
        btn_rem.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))
        
        # Lista de eventos
        lista_frame = tk.Frame(frame, bg="#0f3460", relief=tk.RAISED, bd=2)
        lista_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))
        
        tk.Label(lista_frame, text="Eventos Ativos:", bg="#0f3460", fg="#00d4ff",
                font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=10)
        
        # Scrollbar e Listbox
        scroll_frame = tk.Frame(lista_frame, bg="#0f3460")
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.lista_eventos = tk.Listbox(scroll_frame, bg="#1a1a2e", fg="white",
                                        font=("Courier", 9), relief=tk.FLAT,
                                        yscrollcommand=scrollbar.set,
                                        selectmode=tk.SINGLE)
        self.lista_eventos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.lista_eventos.yview)
        
        # Atualizar lista
        self.atualizar_lista_eventos()
    
    def criar_aba_estatisticas(self, notebook):
        """Cria a aba de estatísticas"""
        frame = tk.Frame(notebook, bg="#16213e")
        notebook.add(frame, text="📊 Stats")
        
        # Título
        titulo = tk.Label(frame, text="Estatísticas do Sistema", bg="#16213e",
                         fg="#00d4ff", font=("Arial", 12, "bold"))
        titulo.pack(pady=10)
        
        # Cards de estatísticas
        cards_frame = tk.Frame(frame, bg="#16213e")
        cards_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Card Interseções
        card1 = tk.Frame(cards_frame, bg="#0f3460", relief=tk.RAISED, bd=2)
        card1.pack(fill=tk.X, pady=5)
        tk.Label(card1, text="Interseções", bg="#0f3460", fg="#00d4ff",
                font=("Arial", 10, "bold")).pack(pady=(10, 5))
        self.label_intersecoes = tk.Label(card1, text="0", bg="#0f3460", fg="white",
                                         font=("Arial", 24, "bold"))
        self.label_intersecoes.pack(pady=(0, 10))
        
        # Card Vias
        card2 = tk.Frame(cards_frame, bg="#0f3460", relief=tk.RAISED, bd=2)
        card2.pack(fill=tk.X, pady=5)
        tk.Label(card2, text="Vias", bg="#0f3460", fg="#00d4ff",
                font=("Arial", 10, "bold")).pack(pady=(10, 5))
        self.label_vias = tk.Label(card2, text="0", bg="#0f3460", fg="white",
                                  font=("Arial", 24, "bold"))
        self.label_vias.pack(pady=(0, 10))
        
        # Card Eventos
        card3 = tk.Frame(cards_frame, bg="#0f3460", relief=tk.RAISED, bd=2)
        card3.pack(fill=tk.X, pady=5)
        tk.Label(card3, text="Eventos Ativos", bg="#0f3460", fg="#00d4ff",
                font=("Arial", 10, "bold")).pack(pady=(10, 5))
        self.label_eventos = tk.Label(card3, text="0", bg="#0f3460", fg="#ff4444",
                                      font=("Arial", 24, "bold"))
        self.label_eventos.pack(pady=(0, 10))
        
        # Botão atualizar
        btn_atualizar = tk.Button(frame, text="🔄 Atualizar", bg="#2196f3",
                                 fg="white", font=("Arial", 10, "bold"),
                                 relief=tk.FLAT, cursor="hand2",
                                 command=self.atualizar_estatisticas)
        btn_atualizar.pack(fill=tk.X, padx=20, pady=20)
        
        # Atualizar estatísticas
        self.atualizar_estatisticas()
    
    def desenhar_grafo(self):
        """Desenha o grafo no canvas"""
        self.canvas.delete("all")
        
        if not self.grafo.vertices:
            self.canvas.create_text(400, 300, text="Clique em 'Malha Viária' > 'Adicionar Interseção'\npara começar",
                                   fill="white", font=("Arial", 12), justify=tk.CENTER)
            return
        
        # Se não há posições, calcular layout circular
        if not self.vertices_pos:
            self.calcular_layout_circular()
        
        # Desenhar arestas primeiro (ficam atrás)
        arestas = self.grafo.obter_todas_arestas()
        for origem, destino, peso in arestas:
            if origem in self.vertices_pos and destino in self.vertices_pos:
                x1, y1 = self.vertices_pos[origem]
                x2, y2 = self.vertices_pos[destino]
                
                # Cor da aresta
                cor = "#4a5568"  # Cor padrão
                largura = 2
                
                # Verificar se tem evento
                peso_orig = self.grafo.obter_peso_original(origem, destino)
                if peso != peso_orig:
                    cor = "#ff4444"  # Via com evento
                    largura = 3
                
                # Verificar se está no caminho atual
                if self.caminho_atual and origem in self.caminho_atual and destino in self.caminho_atual:
                    idx_o = self.caminho_atual.index(origem)
                    idx_d = self.caminho_atual.index(destino)
                    if abs(idx_o - idx_d) == 1:
                        cor = "#00ff88"  # Via na rota
                        largura = 4
                
                # Desenhar linha
                self.canvas.create_line(x1, y1, x2, y2, fill=cor, width=largura, tags="aresta")
                
                # Desenhar peso no meio
                mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                texto_peso = f"{peso:.1f}km"
                self.canvas.create_text(mid_x, mid_y - 10, text=texto_peso,
                                       fill="white", font=("Arial", 8, "bold"),
                                       tags="peso")
        
        # Desenhar vértices
        for vertice, (x, y) in self.vertices_pos.items():
            # Cor do vértice
            cor = "#00d4ff"  # Cor padrão
            if self.caminho_atual and vertice in self.caminho_atual:
                cor = "#00ff88"  # Vértice na rota
            
            # Círculo
            raio = 20
            self.canvas.create_oval(x-raio, y-raio, x+raio, y+raio,
                                   fill=cor, outline="white", width=2,
                                   tags=f"vertice_{vertice}")
            
            # Texto
            self.canvas.create_text(x, y, text=vertice, fill="black",
                                   font=("Arial", 11, "bold"),
                                   tags=f"vertice_{vertice}")
    
    def calcular_layout_circular(self):
        """Calcula posições dos vértices em layout circular"""
        vertices = sorted(self.grafo.vertices)
        n = len(vertices)
        
        if n == 0:
            return
        
        # Centro e raio do círculo
        canvas_width = self.canvas.winfo_width() or 800
        canvas_height = self.canvas.winfo_height() or 600
        centro_x = canvas_width / 2
        centro_y = canvas_height / 2
        raio = min(canvas_width, canvas_height) * 0.35
        
        # Calcular posições
        for i, vertice in enumerate(vertices):
            angulo = 2 * math.pi * i / n - math.pi / 2  # Começar do topo
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
                          "Clique na interseção de ORIGEM")
    
    def selecionar_vertice_aresta(self, x, y):
        """Seleciona vértices para criar aresta"""
        # Encontrar vértice mais próximo
        vertice_clicado = None
        dist_min = float('inf')
        
        for vertice, (vx, vy) in self.vertices_pos.items():
            dist = math.sqrt((x - vx)**2 + (y - vy)**2)
            if dist < 30 and dist < dist_min:  # Raio de 30 pixels
                dist_min = dist
                vertice_clicado = vertice
        
        if not vertice_clicado:
            messagebox.showwarning("Aviso", "Clique próximo a uma interseção!")
            return
        
        if self.aresta_origem is None:
            self.aresta_origem = vertice_clicado
            messagebox.showinfo("Adicionar Via",
                              f"Origem: {self.aresta_origem}\nAgora clique no DESTINO")
        else:
            destino = vertice_clicado
            if destino == self.aresta_origem:
                messagebox.showwarning("Aviso", "Origem e destino devem ser diferentes!")
                return
            
            # Pedir distância
            peso = simpledialog.askfloat("Distância da Via",
                                        f"Distância {self.aresta_origem} ↔ {destino} (km):",
                                        minvalue=0.1,
                                        parent=self.root)
            if peso:
                self.grafo.adicionar_aresta(self.aresta_origem, destino, peso)
                self.modo_adicionar = None
                self.aresta_origem = None
                self.atualizar_interface()
    
    def remover_via_dialog(self):
        """Dialog para remover via"""
        if self.grafo.total_arestas() == 0:
            messagebox.showinfo("Info", "Não há vias para remover!")
            return
        
        # Criar janela
        dialog = tk.Toplevel(self.root)
        dialog.title("Remover Via")
        dialog.geometry("300x150")
        dialog.configure(bg="#16213e")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Selecione a via:", bg="#16213e", fg="white",
                font=("Arial", 10)).pack(pady=10)
        
        # Listar arestas
        arestas = self.grafo.obter_todas_arestas()
        opcoes = [f"{o} ↔ {d}" for o, d, _ in arestas]
        
        combo = ttk.Combobox(dialog, values=opcoes, state="readonly")
        combo.pack(padx=20, fill=tk.X)
        if opcoes:
            combo.current(0)
        
        def remover():
            if not combo.get():
                return
            origem, destino = combo.get().split(" ↔ ")
            if self.grafo.remover_aresta(origem, destino):
                messagebox.showinfo("Sucesso", f"Via {origem} ↔ {destino} removida!")
                dialog.destroy()
                self.atualizar_interface()
            else:
                messagebox.showerror("Erro", "Não foi possível remover a via")
        
        tk.Button(dialog, text="Remover", bg="#f44336", fg="white",
                 command=remover).pack(pady=20)
    
    def registrar_evento_dialog(self):
        """Dialog para registrar evento"""
        if self.grafo.total_arestas() == 0:
            messagebox.showinfo("Info", "Não há vias para adicionar eventos!")
            return
        
        # Criar janela
        dialog = tk.Toplevel(self.root)
        dialog.title("Registrar Evento")
        dialog.geometry("350x300")
        dialog.configure(bg="#16213e")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Tipo de Evento:", bg="#16213e", fg="white",
                font=("Arial", 10)).pack(pady=(20, 5))
        
        tipo_combo = ttk.Combobox(dialog, values=["acidente", "obra", "congestionamento"],
                                 state="readonly")
        tipo_combo.pack(padx=20, fill=tk.X)
        tipo_combo.current(0)
        
        tk.Label(dialog, text="Via Afetada:", bg="#16213e", fg="white",
                font=("Arial", 10)).pack(pady=(15, 5))
        
        arestas = self.grafo.obter_todas_arestas()
        opcoes = [f"{o} ↔ {d}" for o, d, _ in arestas]
        
        via_combo = ttk.Combobox(dialog, values=opcoes, state="readonly")
        via_combo.pack(padx=20, fill=tk.X)
        if opcoes:
            via_combo.current(0)
        
        tk.Label(dialog, text="Impacto (km adicional):", bg="#16213e", fg="white",
                font=("Arial", 10)).pack(pady=(15, 5))
        
        impacto_entry = tk.Entry(dialog, font=("Arial", 10))
        impacto_entry.pack(padx=20, fill=tk.X)
        impacto_entry.insert(0, "3.0")
        
        def registrar():
            try:
                tipo = tipo_combo.get()
                origem, destino = via_combo.get().split(" ↔ ")
                impacto = float(impacto_entry.get())
                
                if impacto <= 0:
                    messagebox.showerror("Erro", "Impacto deve ser positivo!")
                    return
                
                sucesso, msg = self.sistema.registrar_evento(tipo, origem, destino, impacto)
                if sucesso:
                    messagebox.showinfo("Sucesso", msg)
                    dialog.destroy()
                    self.atualizar_interface()
                else:
                    messagebox.showerror("Erro", msg)
            except ValueError:
                messagebox.showerror("Erro", "Impacto inválido!")
        
        tk.Button(dialog, text="Registrar", bg="#4caf50", fg="white",
                 font=("Arial", 10, "bold"), command=registrar).pack(pady=20)
    
    def remover_evento_dialog(self):
        """Dialog para remover evento"""
        eventos = self.avl.listar_todos()
        if not eventos:
            messagebox.showinfo("Info", "Não há eventos ativos!")
            return
        
        # Criar janela
        dialog = tk.Toplevel(self.root)
        dialog.title("Remover Evento")
        dialog.geometry("400x200")
        dialog.configure(bg="#16213e")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Selecione o evento:", bg="#16213e", fg="white",
                font=("Arial", 10)).pack(pady=10)
        
        # Listar eventos
        opcoes = [f"ID {ev.id}: {ev.tipo} em {ev.localizacao}" for ev in eventos]
        
        combo = ttk.Combobox(dialog, values=opcoes, state="readonly", width=40)
        combo.pack(padx=20, fill=tk.X)
        if opcoes:
            combo.current(0)
        
        def remover():
            if not combo.get():
                return
            id_evento = int(combo.get().split(":")[0].replace("ID ", ""))
            sucesso, msg = self.sistema.remover_evento(id_evento)
            if sucesso:
                messagebox.showinfo("Sucesso", msg)
                dialog.destroy()
                self.atualizar_interface()
            else:
                messagebox.showerror("Erro", msg)
        
        tk.Button(dialog, text="Remover", bg="#f44336", fg="white",
                 font=("Arial", 10, "bold"), command=remover).pack(pady=20)
    
    def calcular_rota(self):
        """Calcula a rota ótima"""
        origem = self.combo_origem.get()
        destino = self.combo_destino.get()
        
        if not origem or not destino:
            messagebox.showwarning("Aviso", "Selecione origem e destino!")
            return
        
        if origem == destino:
            messagebox.showwarning("Aviso", "Origem e destino devem ser diferentes!")
            return
        
        # Calcular rota
        caminho, distancia, status = self.sistema.calcular_rota_otima(origem, destino)
        
        # Atualizar caminho destacado
        self.caminho_atual = caminho if caminho else []
        self.desenhar_grafo()
        
        # Mostrar resultado
        self.text_resultado.config(state=tk.NORMAL)
        self.text_resultado.delete("1.0", tk.END)
        
        if status == "OK":
            self.text_resultado.insert("1.0", "✓ ROTA ENCONTRADA\n\n", "titulo")
            self.text_resultado.insert(tk.END, f"Origem: {origem}\n")
            self.text_resultado.insert(tk.END, f"Destino: {destino}\n\n")
            self.text_resultado.insert(tk.END, f"Caminho:\n{' → '.join(caminho)}\n\n", "destaque")
            self.text_resultado.insert(tk.END, f"Distância Total: {distancia:.2f} km\n\n", "distancia")
            
            # Verificar eventos na rota
            eventos = self.sistema.eventos_na_rota(caminho)
            if eventos:
                self.text_resultado.insert(tk.END, f"⚠ {len(eventos)} evento(s) afetando:\n", "aviso")
                for ev in eventos:
                    self.text_resultado.insert(tk.END, f"  • {ev.tipo} em {ev.localizacao}\n")
                    self.text_resultado.insert(tk.END, f"    (+{ev.impacto} km)\n")
            else:
                self.text_resultado.insert(tk.END, "✓ Nenhum evento nesta rota\n", "ok")
        else:
            self.text_resultado.insert("1.0", "✗ ROTA NÃO ENCONTRADA\n\n", "erro")
            self.text_resultado.insert(tk.END, f"Status: {status}\n")
        
        # Configurar tags de formatação
        self.text_resultado.tag_config("titulo", foreground="#00ff88", font=("Courier", 10, "bold"))
        self.text_resultado.tag_config("destaque", foreground="#00d4ff", font=("Courier", 9, "bold"))
        self.text_resultado.tag_config("distancia", foreground="#ffeb3b", font=("Courier", 10, "bold"))
        self.text_resultado.tag_config("aviso", foreground="#ff9800", font=("Courier", 9, "bold"))
        self.text_resultado.tag_config("ok", foreground="#4caf50", font=("Courier", 9))
        self.text_resultado.tag_config("erro", foreground="#ff4444", font=("Courier", 10, "bold"))
        
        self.text_resultado.config(state=tk.DISABLED)
    
    def comparar_rotas(self):
        """Compara rotas com e sem eventos"""
        origem = self.combo_origem.get()
        destino = self.combo_destino.get()
        
        if not origem or not destino:
            messagebox.showwarning("Aviso", "Selecione origem e destino!")
            return
        
        if origem == destino:
            messagebox.showwarning("Aviso", "Origem e destino devem ser diferentes!")
            return
        
        # Comparar rotas
        resultado = self.sistema.comparar_rotas(origem, destino)
        caminho_ideal, dist_ideal = resultado['rota_ideal']
        caminho_atual, dist_atual = resultado['rota_atual']
        impacto = resultado['impacto']
        
        # Destacar rota atual
        self.caminho_atual = caminho_atual if caminho_atual else []
        self.desenhar_grafo()
        
        # Mostrar resultado
        self.text_resultado.config(state=tk.NORMAL)
        self.text_resultado.delete("1.0", tk.END)
        
        self.text_resultado.insert("1.0", "📊 COMPARAÇÃO DE ROTAS\n\n", "titulo")
        
        if caminho_ideal:
            self.text_resultado.insert(tk.END, "🟢 Rota Ideal (sem eventos):\n", "ok")
            self.text_resultado.insert(tk.END, f"   {' → '.join(caminho_ideal)}\n")
            self.text_resultado.insert(tk.END, f"   Distância: {dist_ideal:.2f} km\n\n")
        
        if caminho_atual:
            self.text_resultado.insert(tk.END, "🔴 Rota Atual (com eventos):\n", "aviso")
            self.text_resultado.insert(tk.END, f"   {' → '.join(caminho_atual)}\n")
            self.text_resultado.insert(tk.END, f"   Distância: {dist_atual:.2f} km\n\n")
        
        if impacto > 0:
            percentual = (impacto / dist_ideal * 100) if dist_ideal > 0 else 0
            self.text_resultado.insert(tk.END, f"⚠ Impacto dos Eventos:\n", "erro")
            self.text_resultado.insert(tk.END, f"   +{impacto:.2f} km ({percentual:.1f}%)\n")
        elif impacto == 0:
            self.text_resultado.insert(tk.END, "✓ Rotas idênticas\n", "ok")
            self.text_resultado.insert(tk.END, "  Nenhum impacto\n")
        
        self.text_resultado.tag_config("titulo", foreground="#00d4ff", font=("Courier", 10, "bold"))
        self.text_resultado.tag_config("ok", foreground="#4caf50", font=("Courier", 9))
        self.text_resultado.tag_config("aviso", foreground="#ff9800", font=("Courier", 9))
        self.text_resultado.tag_config("erro", foreground="#ff4444", font=("Courier", 9, "bold"))
        
        self.text_resultado.config(state=tk.DISABLED)
    
    def atualizar_lista_eventos(self):
        """Atualiza a lista de eventos"""
        self.lista_eventos.delete(0, tk.END)
        eventos = self.avl.listar_todos()
        
        if not eventos:
            self.lista_eventos.insert(tk.END, "  Nenhum evento ativo")
        else:
            for ev in eventos:
                data_hora = datetime.fromtimestamp(ev.timestamp).strftime('%d/%m %H:%M')
                texto = f"ID {ev.id}: {ev.tipo.upper()}"
                self.lista_eventos.insert(tk.END, texto)
                texto2 = f"   Via: {ev.localizacao} (+{ev.impacto}km)"
                self.lista_eventos.insert(tk.END, texto2)
                texto3 = f"   {data_hora}"
                self.lista_eventos.insert(tk.END, texto3)
                self.lista_eventos.insert(tk.END, "")  # Linha em branco
    
    def atualizar_estatisticas(self):
        """Atualiza as estatísticas"""
        stats = self.sistema.estatisticas()
        self.label_intersecoes.config(text=str(stats['total_intersecoes']))
        self.label_vias.config(text=str(stats['total_vias']))
        self.label_eventos.config(text=str(stats['eventos_ativos']))
    
    def atualizar_combos(self):
        """Atualiza os comboboxes de origem e destino"""
        vertices = sorted(self.grafo.vertices)
        self.combo_origem['values'] = vertices
        self.combo_destino['values'] = vertices
    
    def atualizar_interface(self):
        """Atualiza toda a interface"""
        self.desenhar_grafo()
        self.atualizar_combos()
        self.atualizar_lista_eventos()
        self.atualizar_estatisticas()
    
    def criar_dados_exemplo(self):
        """Cria dados de exemplo"""
        # Interseções
        intersecoes = ['A', 'B', 'C', 'D', 'E', 'F']
        for i in intersecoes:
            self.grafo.adicionar_vertice(i)
        
        # Posições pré-definidas para layout bonito
        canvas_w = 800
        canvas_h = 600
        self.vertices_pos = {
            'A': (150, 150),
            'B': (400, 100),
            'C': (250, 300),
            'D': (550, 250),
            'E': (400, 450),
            'F': (650, 400)
        }
        
        # Vias
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
            self.grafo.adicionar_aresta(origem, destino, peso)
        
        # Eventos
        self.sistema.registrar_evento('acidente', 'A', 'B', 3.0)
        self.sistema.registrar_evento('obra', 'C', 'D', 5.0)
        
        self.atualizar_interface()
    
    def novo_sistema(self):
        """Reinicia o sistema"""
        resposta = messagebox.askyesno("Confirmar", 
                                       "Deseja criar um novo sistema?\n"
                                       "Todos os dados não salvos serão perdidos!")
        if resposta:
            self.grafo = GrafoPonderado()
            self.avl = ArvoreAVL()
            self.sistema = SistemaTransito(self.grafo, self.avl)
            self.vertices_pos = {}
            self.caminho_atual = []
            self.atualizar_interface()
    
    def salvar_dados(self):
        """Salva os dados do sistema"""
        sucesso, msg = self.sistema.salvar_dados()
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
        else:
            messagebox.showerror("Erro", msg)
    
    def carregar_dados(self):
        """Carrega dados salvos"""
        sucesso, msg = self.sistema.carregar_dados()
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self.vertices_pos = {}  # Recalcular posições
            self.atualizar_interface()
        else:
            messagebox.showerror("Erro", msg)
    
    def mostrar_sobre(self):
        """Mostra informações sobre o sistema"""
        sobre = tk.Toplevel(self.root)
        sobre.title("Sobre")
        sobre.geometry("400x300")
        sobre.configure(bg="#16213e")
        sobre.transient(self.root)
        sobre.grab_set()
        
        texto = """
        SISTEMA DE TRÂNSITO INTELIGENTE
        
        Versão 1.0
        
        Estruturas de Dados:
        • Grafo Ponderado (Dijkstra)
        • Árvore AVL (Eventos ordenados)
        
        Funcionalidades:
        ✓ Gerenciamento de malha viária
        ✓ Registro de eventos de trânsito
        ✓ Cálculo de rotas ótimas
        ✓ Comparação de rotas
        ✓ Visualização gráfica
        ✓ Persistência de dados
        
        Desenvolvido com Python e Tkinter
        """
        
        tk.Label(sobre, text=texto, bg="#16213e", fg="white",
                font=("Arial", 10), justify=tk.LEFT).pack(padx=20, pady=20)
        
        tk.Button(sobre, text="Fechar", bg="#00d4ff", fg="black",
                 font=("Arial", 10, "bold"), command=sobre.destroy).pack(pady=10)


def main():
    """Função principal"""
    root = tk.Tk()
    app = InterfaceTransito(root)
    root.mainloop()


if __name__ == "__main__":
    main()