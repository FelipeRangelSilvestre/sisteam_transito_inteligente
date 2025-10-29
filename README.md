# Sistema de Trânsito Inteligente 🚦

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Academic-green.svg)](LICENSE)

## Descrição
Sistema desenvolvido para a disciplina de **Algoritmos e Estruturas de Dados II** que implementa um gerenciador inteligente de tráfego urbano utilizando **Grafo Ponderado** e **Árvore AVL**. O sistema oferece duas interfaces: **terminal interativo** e **interface gráfica** com Tkinter.

## 🎯 Objetivos
- Implementar estruturas de dados balanceadas (AVL) e grafos de forma funcional
- Aplicar algoritmos de busca, inserção, remoção e caminho mínimo
- Demonstrar integração entre duas estruturas de dados distintas
- Simular um sistema real de gerenciamento de tráfego
- Fornecer visualização gráfica interativa da malha viária

## 🏗️ Estruturas de Dados

### Grafo Ponderado
- **Vértices**: Representam interseções/pontos da cidade
- **Arestas**: Representam vias/ruas com pesos (distância em km)
- **Implementação**: Lista de adjacências com dicionários
- **Algoritmo**: Dijkstra para cálculo de caminho mínimo

### Árvore AVL
- **Nós**: Armazenam eventos de trânsito (acidentes, obras, congestionamentos)
- **Chave**: Timestamp do evento para ordenação temporal
- **Balanceamento**: Rotações simples e duplas mantêm altura O(log n)
- **Operações**: Inserção, remoção e busca em O(log n)

## 🔗 Integração das Estruturas

A integração entre Grafo e AVL ocorre da seguinte forma:

1. **Registro de Evento**: 
   - Evento é inserido na AVL (O(log n))
   - Peso da aresta correspondente no grafo é atualizado (O(1))

2. **Remoção de Evento**:
   - Evento é removido da AVL (O(log n))
   - Peso original da aresta é restaurado no grafo (O(1))

3. **Cálculo de Rota**:
   - Dijkstra considera os pesos atualizados pelos eventos ativos
   - Complexidade: O((V + E) log V)

## 📂 Estrutura do Projeto

```
sistema-transito-inteligente/
│
├── src/
│   ├── avl_tree.py              # Implementação da Árvore AVL
│   ├── grafo_ponderado.py       # Implementação do Grafo
│   ├── sistema_transito.py      # Integração das estruturas
│   ├── main.py                  # Interface de terminal
│   ├── test_sistema.py          # Testes unitários
│   └── criar_dados_exemplo.py   # Script para dados de teste
│
├── gui_sistema.py               # Interface gráfica (Tkinter)
│
├── dados/                       # Criado automaticamente
│   ├── grafo.txt               # Persistência da malha viária
│   └── eventos.txt             # Persistência dos eventos
│
├── docs/
│   └── relatorio.pdf           # Relatório técnico final
│
├── README.md
└── requirements.txt
```

## 🚀 Como Executar

### Requisitos
- Python 3.8 ou superior
- Tkinter (geralmente já vem instalado com Python)
- Nenhuma biblioteca externa adicional

### Instalação

```bash
# Clone o repositório
git clone https://github.com/FelipeRangelSilvestre/Sistema-de-Transito-Inteligente.git
cd Sistema-de-Transito-Inteligente
```

### Opções de Execução

#### 1️⃣ Interface Gráfica (Recomendado)

```bash
python gui_sistema.py
```

**Funcionalidades da GUI:**
- 🖱️ Visualização gráfica interativa da malha viária
- 🎨 Canvas com destaque visual de rotas
- 📊 Abas organizadas (Rotas, Eventos, Estatísticas)
- ➕ Adição de interseções e vias com cliques
- 🔴 Destaque de vias com eventos (vermelho)
- 🟢 Destaque de rotas calculadas (verde)
- 💾 Salvar e carregar dados

#### 2️⃣ Interface de Terminal

```bash
python src/main.py
```

**Funcionalidades do Terminal:**
- 📝 Menu interativo colorido
- 🗺️ Visualização textual da malha
- 📋 Listagens detalhadas de eventos
- 🧮 Cálculos de rotas com análises
- 💾 Persistência de dados

#### 3️⃣ Testes Automatizados

```bash
python src/test_sistema.py
```

Executa bateria completa de testes:
- ✅ Teste de AVL (inserção, remoção, balanceamento)
- ✅ Teste de Grafo (Dijkstra, operações)
- ✅ Teste de Integração
- ✅ Teste de Persistência
- ✅ Teste de Performance

## 📋 Funcionalidades Completas

### 1. Gerenciar Malha Viária
- ✅ Adicionar interseções (GUI: clique no canvas)
- ✅ Adicionar vias bidirecionais com distâncias
- ✅ Remover vias
- ✅ Visualizar mapa completo (texto ou gráfico)

### 2. Gerenciar Eventos de Trânsito
- ✅ Registrar eventos (acidente, obra, congestionamento)
- ✅ Remover eventos
- ✅ Listar eventos ativos ordenados por timestamp
- ✅ Buscar evento por ID
- ✅ Visualização em tempo real no canvas

### 3. Cálculo de Rotas
- ✅ Calcular rota ótima com algoritmo de Dijkstra
- ✅ Comparar rotas com e sem eventos
- ✅ Identificar eventos que afetam uma rota
- ✅ Destaque visual do caminho no canvas

### 4. Análise e Estatísticas
- ✅ Total de interseções e vias
- ✅ Eventos ativos
- ✅ Distribuição por tipo de evento
- ✅ Cards visuais com métricas

### 5. Persistência
- ✅ Salvar dados em arquivos texto
- ✅ Carregar dados salvos
- ✅ Dados de exemplo incluídos

## 🧪 Exemplos de Uso

### Exemplo 1: Criar Malha Viária (GUI)
1. Abra a interface gráfica: `python gui_sistema.py`
2. Menu "Malha Viária" → "Adicionar Interseção"
3. Digite o nome (ex: "CENTRO") e clique no canvas
4. Menu "Malha Viária" → "Adicionar Via"
5. Clique em duas interseções sequencialmente
6. Digite a distância quando solicitado

### Exemplo 2: Registrar Evento
```
Terminal:
  Menu → 2. Gerenciar Eventos → 1. Registrar novo evento
  Tipo: acidente
  Via: A-B
  Impacto: +3.0 km
  ✓ Via A-B passa de 5.0 km para 8.0 km

GUI:
  Menu "Eventos" → "Registrar Evento"
  Selecione tipo, via e impacto
  ✓ Via destacada em vermelho no canvas
```

### Exemplo 3: Calcular Rota com Visualização
```
GUI:
1. Aba "Rotas"
2. Selecione Origem: A
3. Selecione Destino: F
4. Clique "Calcular Rota Ótima"
5. O caminho é destacado em verde no canvas
6. Resultado mostra distância e eventos afetando a rota

Sem eventos:
  Caminho: A → C → E → F
  Distância: 13.0 km

Com evento (acidente A-B, +5km):
  Caminho: A → D → F (rota alternativa)
  Distância: 15.0 km
  ⚠ Sistema escolhe automaticamente a rota mais rápida!
```

## 📊 Complexidade das Operações

| Operação | Complexidade | Estrutura | Justificativa |
|----------|-------------|-----------|---------------|
| Inserir evento | O(log n) | AVL | Árvore balanceada |
| Remover evento | O(log n) | AVL | Árvore balanceada |
| Buscar evento | O(log n) | AVL | Árvore balanceada |
| Adicionar via | O(1) | Grafo | Lista de adjacências |
| Atualizar peso | O(1) | Grafo | Acesso direto |
| Dijkstra | O((V+E) log V) | Grafo | Com heap binário |
| Registrar evento (completo) | O(log n) | Sistema | AVL domina |
| Calcular rota com eventos | O((V+E) log V) | Sistema | Dijkstra domina |

## 🎨 Interface Gráfica - Características

### Design Moderno
- 🌙 Tema dark profissional (tons de azul escuro)
- 🎯 Layout responsivo com divisão canvas/controles
- 🔵 Cores vibrantes para destaque (#00d4ff, #00ff88, #ff4444)
- 📱 Interface intuitiva com menus contextuais

### Canvas Interativo
- 🖱️ Clique para adicionar elementos
- 📍 Layout circular automático dos vértices
- 🔴 Vias com eventos em vermelho (largura 3px)
- 🟢 Rotas calculadas em verde (largura 4px)
- ⚪ Vias normais em cinza (largura 2px)
- 🏷️ Labels com distâncias nas arestas

### Sistema de Abas
- **🚗 Rotas**: Cálculo e comparação de rotas
- **⚠️ Eventos**: Gerenciamento completo de eventos
- **📊 Stats**: Estatísticas em tempo real com cards visuais

## 👥 Equipe

- **Felipe Rangel Silvestre** - Desenvolvedor Principal
- [Nome do Integrante 2] - [Função]
- [Nome do Integrante 3] - [Função]
- [Nome do Integrante 4] - [Função]
- [Nome do Integrante 5] - [Função]

## 📝 Relatório Técnico

O relatório completo está disponível em `docs/relatorio.pdf` e contém:
- ✅ Fundamentação teórica detalhada
- ✅ Análise de complexidade com provas
- ✅ Capturas de tela do sistema
- ✅ Testes e resultados experimentais
- ✅ Dificuldades encontradas e soluções
- ✅ Conclusões e trabalhos futuros

## 🔗 Links Importantes

- **GitHub**: https://github.com/FelipeRangelSilvestre/Sistema-de-Transito-Inteligente
- **Relatório (Overleaf)**: [Link será adicionado]
- **Vídeo Demonstração**: [Link será adicionado]

## 🎓 Disciplina

**ITI275 - Algoritmos e Estruturas de Dados II**  
Prof. Alternei Brito  
Universidade Federal do Amazonas (UFAM)  
Instituto de Ciências Exatas e Tecnologia (ICET)  
Itacoatiara - AM

## 📅 Entrega

**Data Limite**: 25 de novembro de 2025

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos como parte do curso de Engenharia de Software da UFAM.

## 🆘 Suporte

Para dúvidas ou problemas:
1. Consulte a documentação no código (docstrings)
2. Execute os testes: `python src/test_sistema.py`
3. Verifique os exemplos em `EXEMPLO_EXECUCAO.md`
4. Entre em contato com a equipe

---

## 🎉 Destaques do Projeto

### ✨ Diferenciais
- ✅ **Interface Dupla**: Terminal colorido + GUI moderna
- ✅ **Visualização Gráfica**: Canvas interativo com Tkinter
- ✅ **Código Limpo**: Sem bibliotecas externas, apenas Python puro
- ✅ **Testes Completos**: 5 baterias de testes automatizados
- ✅ **Performance**: Otimizado com estruturas eficientes
- ✅ **Persistência**: Salva e carrega dados automaticamente
- ✅ **Documentação**: Código comentado + README completo + Relatório técnico

### 🏆 Bônus de Integração
O projeto demonstra **integração excepcional** entre Grafo e AVL:
- Atualização bidirecional (evento ↔ peso)
- Sincronização em tempo real
- Restauração automática de pesos originais
- Comparação de rotas ideal vs. atual

---

**Nota**: Este sistema demonstra a aplicação prática de estruturas de dados avançadas em um problema real de otimização de rotas urbanas considerando eventos dinâmicos de trânsito. O código é 100% Python puro, sem dependências externas além da biblioteca padrão.
