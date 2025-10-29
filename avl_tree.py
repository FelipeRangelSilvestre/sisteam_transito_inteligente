#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementação da Árvore AVL para Eventos de Trânsito
"""

class NoAVL:
    """Nó da Árvore AVL para armazenar eventos de trânsito"""
    def __init__(self, id_evento, timestamp, tipo, localizacao, impacto):
        self.id = id_evento
        self.timestamp = timestamp  # Chave para ordenação
        self.tipo = tipo  # 'acidente', 'obra', 'congestionamento'
        self.localizacao = localizacao  # Ex: "A-B" (aresta afetada)
        self.impacto = impacto  # Acréscimo no peso da aresta
        self.altura = 1
        self.esquerda = None
        self.direita = None
    
    def __str__(self):
        return f"[ID:{self.id}] {self.tipo} em {self.localizacao} (impacto: +{self.impacto})"


class ArvoreAVL:
    """Árvore AVL para gerenciar eventos de trânsito ordenados por timestamp"""
    
    def __init__(self):
        self.raiz = None
        self.total_eventos = 0
    
    def altura(self, no):
        """Retorna a altura do nó"""
        if not no:
            return 0
        return no.altura
    
    def balanceamento(self, no):
        """Calcula o fator de balanceamento do nó"""
        if not no:
            return 0
        return self.altura(no.esquerda) - self.altura(no.direita)
    
    def atualizar_altura(self, no):
        """Atualiza a altura do nó"""
        if no:
            no.altura = 1 + max(self.altura(no.esquerda), self.altura(no.direita))
    
    def rotacao_direita(self, y):
        """Rotação simples à direita"""
        x = y.esquerda
        T2 = x.direita
        
        x.direita = y
        y.esquerda = T2
        
        self.atualizar_altura(y)
        self.atualizar_altura(x)
        
        return x
    
    def rotacao_esquerda(self, x):
        """Rotação simples à esquerda"""
        y = x.direita
        T2 = y.esquerda
        
        y.esquerda = x
        x.direita = T2
        
        self.atualizar_altura(x)
        self.atualizar_altura(y)
        
        return y
    
    def inserir(self, id_evento, timestamp, tipo, localizacao, impacto):
        """Insere um novo evento na árvore - Complexidade: O(log n)"""
        self.raiz = self._inserir_recursivo(self.raiz, id_evento, timestamp, tipo, localizacao, impacto)
        self.total_eventos += 1
        return True
    
    def _inserir_recursivo(self, no, id_evento, timestamp, tipo, localizacao, impacto):
        # Inserção BST padrão
        if not no:
            return NoAVL(id_evento, timestamp, tipo, localizacao, impacto)
        
        if timestamp < no.timestamp:
            no.esquerda = self._inserir_recursivo(no.esquerda, id_evento, timestamp, tipo, localizacao, impacto)
        else:
            no.direita = self._inserir_recursivo(no.direita, id_evento, timestamp, tipo, localizacao, impacto)
        
        # Atualizar altura
        self.atualizar_altura(no)
        
        # Balancear a árvore
        return self._balancear(no)
    
    def _balancear(self, no):
        """Balanceia o nó após inserção ou remoção"""
        bal = self.balanceamento(no)
        
        # Caso Esquerda-Esquerda
        if bal > 1 and self.balanceamento(no.esquerda) >= 0:
            return self.rotacao_direita(no)
        
        # Caso Direita-Direita
        if bal < -1 and self.balanceamento(no.direita) <= 0:
            return self.rotacao_esquerda(no)
        
        # Caso Esquerda-Direita
        if bal > 1 and self.balanceamento(no.esquerda) < 0:
            no.esquerda = self.rotacao_esquerda(no.esquerda)
            return self.rotacao_direita(no)
        
        # Caso Direita-Esquerda
        if bal < -1 and self.balanceamento(no.direita) > 0:
            no.direita = self.rotacao_direita(no.direita)
            return self.rotacao_esquerda(no)
        
        return no
    
    def remover(self, id_evento):
        """Remove um evento da árvore - Complexidade: O(log n)"""
        self.raiz, removido = self._remover_recursivo(self.raiz, id_evento)
        if removido:
            self.total_eventos -= 1
        return removido
    
    def _remover_recursivo(self, no, id_evento):
        if not no:
            return no, False
        
        removido = False
        
        # Buscar o nó
        if id_evento == no.id:
            removido = True
            # Caso 1: Nó folha ou com um filho
            if not no.esquerda:
                return no.direita, True
            elif not no.direita:
                return no.esquerda, True
            
            # Caso 2: Nó com dois filhos
            temp = self._minimo(no.direita)
            no.id = temp.id
            no.timestamp = temp.timestamp
            no.tipo = temp.tipo
            no.localizacao = temp.localizacao
            no.impacto = temp.impacto
            no.direita, _ = self._remover_recursivo(no.direita, temp.id)
        
        elif id_evento < no.id:
            no.esquerda, removido = self._remover_recursivo(no.esquerda, id_evento)
        else:
            no.direita, removido = self._remover_recursivo(no.direita, id_evento)
        
        if not removido:
            return no, False
        
        # Atualizar altura e balancear
        self.atualizar_altura(no)
        return self._balancear(no), True
    
    def _minimo(self, no):
        """Encontra o nó com menor valor"""
        while no.esquerda:
            no = no.esquerda
        return no
    
    def buscar(self, id_evento):
        """Busca um evento por ID - Complexidade: O(log n)"""
        return self._buscar_recursivo(self.raiz, id_evento)
    
    def _buscar_recursivo(self, no, id_evento):
        if not no or no.id == id_evento:
            return no
        
        if id_evento < no.id:
            return self._buscar_recursivo(no.esquerda, id_evento)
        return self._buscar_recursivo(no.direita, id_evento)
    
    def listar_todos(self):
        """Lista todos os eventos em ordem (in-order) - Complexidade: O(n)"""
        eventos = []
        self._inorder(self.raiz, eventos)
        return eventos
    
    def _inorder(self, no, eventos):
        if no:
            self._inorder(no.esquerda, eventos)
            eventos.append(no)
            self._inorder(no.direita, eventos)
    
    def buscar_por_localizacao(self, localizacao):
        """Busca todos os eventos em uma localização específica"""
        eventos = []
        self._buscar_localizacao(self.raiz, localizacao, eventos)
        return eventos
    
    def _buscar_localizacao(self, no, localizacao, eventos):
        if no:
            self._buscar_localizacao(no.esquerda, localizacao, eventos)
            if no.localizacao == localizacao:
                eventos.append(no)
            self._buscar_localizacao(no.direita, localizacao, eventos)
    
    def esta_vazia(self):
        """Verifica se a árvore está vazia"""
        return self.raiz is None