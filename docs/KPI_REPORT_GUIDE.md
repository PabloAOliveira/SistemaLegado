# 📊 KPIs nos Relatórios - Guia Completo

## Resumo das Adições

Agora os relatórios Excel e PDF incluem **4 seções de KPI** para análise rápida:

1. **📊 Total de Demandas** - Número em grande destaque
2. **📌 Demandas por Prioridade** - Abertas (Alta), Média, Baixa com percentuais
3. **⚠️ Demandas Críticas** - Flagged com alerta quando houver
4. **👥 Demandas por Responsável** - Quantas cada pessoa tem

---

## 1️⃣ Total de Demandas (KPI)

### No Excel
```
┌──────────────────────┐
│ 📊 TOTAL DE DEMANDAS │
│ [NÚMERO GRANDE]      │
└──────────────────────┘
```
- Exibido em célula destacada
- Fácil leitura de longe
- Baseline para análise

### No PDF
```
┌─────────────────────────────────────┐
│ 📊 TOTAL DE DEMANDAS                │
│                                     │
│         [NÚMERO GIGANTE]            │
│                                     │
└─────────────────────────────────────┘
```
- Fonte grande (28pt)
- Cor azul (#2563eb)
- Centralizado e destacado

---

## 2️⃣ Demandas por Prioridade (KPI)

### No Excel
```
┌──────────────────────────────────────┐
│ Demandas por Prioridade              │
├──────────────────────────────────────┤
│ Alta (Crítica)  │ 5  │ 35.7%        │
│ Média           │ 6  │ 42.8%        │
│ Baixa           │ 3  │ 21.4%        │
└──────────────────────────────────────┘
```

### No PDF
```
┌─────────────────────────────────────────┐
│ 📌 DEMANDAS POR PRIORIDADE              │
├────────────────────┬────────┬──────────┤
│ Críticas (Alta)    │   5    │  35.7%   │
│ Média              │   6    │  42.8%   │
│ Baixa              │   3    │  21.4%   │
└────────────────────┴────────┴──────────┘
```
- Tabela formatada com cores
- Fundo amarelo no header (Atenção)
- Percentuais calculados automaticamente

---

## 3️⃣ Demandas Críticas (ATENÇÃO)

### Quando há demandas "Alta"

#### No PDF (com Alerta)
```
┌─────────────────────────────────────┐
│ ⚠️ DEMANDAS CRÍTICAS                 │
│                                     │
│ 5 demanda(s) com prioridade Alta    │
│ requer(em) atenção imediata         │
└─────────────────────────────────────┘
```
- Título em vermelho (#dc2626)
- Ícone de alerta ⚠️
- Mensagem clara e direta

#### No Excel
```
Seção de aviso integrada na análise
```

### Quando não há demandas críticas
- Seção não aparece no PDF
- No Excel, mostra "0"

---

## 4️⃣ Por Responsável (KPI)

### No Excel
```
┌──────────────────────────────┐
│ Demandas por Responsável     │
├──────────────────────────────┤
│ Joao Silva          │ 5      │
│ Maria Santos        │ 4      │
│ Tech Team           │ 3      │
│ Equipe Suporte      │ 2      │
└──────────────────────────────┘
```
- Lista ordenada (maior para menor)
- Sem limite

### No PDF
```
┌────────────────────────────────┐
│ 👥 DEMANDAS POR RESPONSÁVEL    │
├─────────────────┬─────────────┤
│ Responsável     │  Demandas   │
├─────────────────┼─────────────┤
│ Joao Silva      │      5      │
│ Maria Santos    │      4      │
│ Tech Team       │      3      │
│ Equipe Suporte  │      2      │
└─────────────────┴─────────────┘
```
- Tabela formatada (azul claro)
- Limitado aos 10 primeiros (por espaço)
- Ordenado por quantidade

---

## Exemplo Completo de Relatório PDF

```
═══════════════════════════════════════════════════════════════════════════════
                    SGDI - Sistema de Gestão de Demandas
                    
                Data de geração: 27/05/2026 14:30:45
                Filtro: Todas as prioridades

═══════════════════════════════════════════════════════════════════════════════

                       📊 TOTAL DE DEMANDAS
                              14
                              
───────────────────────────────────────────────────────────────────────────────

📌 DEMANDAS POR PRIORIDADE
┌──────────────────┬──────┬────────┐
│ Críticas (Alta)  │  5   │ 35.7%  │
│ Média            │  6   │ 42.8%  │
│ Baixa            │  3   │ 21.4%  │
└──────────────────┴──────┴────────┘

⚠️ DEMANDAS CRÍTICAS
5 demanda(s) com prioridade Alta requer(em) atenção imediata

───────────────────────────────────────────────────────────────────────────────

👥 DEMANDAS POR RESPONSÁVEL
┌─────────────────────────┬──────────┐
│ Responsável             │ Demandas │
├─────────────────────────┼──────────┤
│ Joao Silva              │    5     │
│ Maria Santos            │    4     │
│ Tech Team               │    3     │
│ Equipe Suporte          │    2     │
└─────────────────────────┴──────────┘

───────────────────────────────────────────────────────────────────────────────

📋 DETALHES DAS DEMANDAS
┌─────┬──────────────────────────┬──────────────┬────────────┬──────────────┐
│ ID  │ Título                   │ Solicitante  │ Prioridade │ Data Criação │
├─────┼──────────────────────────┼──────────────┼────────────┼──────────────┤
│  1  │ Implementar autenticação │ Joao Silva   │ Alta       │ 27/05 10:15  │
│  2  │ Corrigir bug validação   │ Maria Santos │ Média      │ 26/05 09:30  │
│  3  │ Melhorar documentação    │ Tech Team    │ Baixa      │ 25/05 14:20  │
│ ... │ ...                      │ ...          │ ...        │ ...          │
└─────┴──────────────────────────┴──────────────┴────────────┴──────────────┘

Relatório gerado com: Todas as prioridades · May–May 2026
```

---

## Exemplo Completo de Relatório Excel

```
╔═══════════════════════════════════════════════════════════════════════════╗
║ SGDI - Sistema de Gestão de Demandas                                      ║
║ Gerado em: 27/05/2026 14:30:45                                            ║
║ Filtro: Todas as prioridades                                              ║
╚═══════════════════════════════════════════════════════════════════════════╝

📊 TOTAL DE DEMANDAS
14

Demandas por Prioridade
Alta (Crítica)          5        35.7%
Média                   6        42.8%
Baixa                   3        21.4%

Demandas por Responsável
Joao Silva              5
Maria Santos            4
Tech Team               3
Equipe Suporte          2

DETALHES DAS DEMANDAS
┌─────┬──────────────────────────┬──────────────┬────────────┬──────────────┐
│ ID  │ Título                   │ Solicitante  │ Prioridade │ Data Criação │
├─────┼──────────────────────────┼──────────────┼────────────┼──────────────┤
│  1  │ Implementar autenticação │ Joao Silva   │ Alta       │ 27/05 10:15  │
│  2  │ Corrigir bug validação   │ Maria Santos │ Média      │ 26/05 09:30  │
│  3  │ Melhorar documentação    │ Tech Team    │ Baixa      │ 25/05 14:20  │
│ ... │ ...                      │ ...          │ ...        │ ...          │
└─────┴──────────────────────────┴──────────────┴────────────┴──────────────┘
```

---

## Funcionalidades dos KPIs

### ✅ Cálculos Automatizados
- Total: Contagem simples de demandas
- Percentuais: Calculados por prioridade
- Responsável: Agrupamento por solicitante

### ✅ Filtros Preservados
- Se filtrar por "Alta", só mostra demandas Alta
- KPIs refletem apenas dados filtrados
- Informação clara no cabeçalho

### ✅ Formatação Visual
- Cores diferentes para cada seção
- Ícones para fácil identificação
- Tabelas com bordas e espaçamento

### ✅ Responsividade
- Excel: Larguras ajustadas automaticamente
- PDF: Layout adaptável a diferentes tamanhos

---

## Como Interpretar os Dados

### 📊 Total de Demandas
- **Alto**: Muita carga de trabalho
- **Baixo**: Situação controlada
- **Referência**: Compare com período anterior

### 📌 Por Prioridade
- **Alta > 40%**: Situação crítica, requer ação
- **Alta 20-40%**: Situação normal
- **Alta < 20%**: Excelente, bem controlado

### ⚠️ Demandas Críticas
- **Qualquer valor > 0**: Verifique imediatamente
- **Indicador**: Use para reuniões executivas

### 👥 Por Responsável
- **Desbalanceamento**: Se alguém tem muito mais
- **Subutilização**: Se alguém tem muito menos
- **Base para rebalanceamento**: Redistribua carga

---

## Novos Códigos do Relatório

### Função para Calcular KPIs
```python
def calculate_kpis(demandas):
    """Calcula total, por prioridade e por responsável"""
    # Retorna dicionário com:
    # - total: número total
    # - criticas, media, baixa: contagem por prioridade
    # - pct_criticas, pct_media, pct_baixa: percentuais
    # - por_responsavel: lista ordenada (pessoa, qtd)
```

### Uso nos Relatórios
```python
kpis = calculate_kpis(demandas)
# Então usar: kpis['total'], kpis['criticas'], etc.
```

---

## Testes de Validação

✅ Excel com filtro "Todas" - Funciona  
✅ Excel com filtro "Alta" - Funciona  
✅ Excel com filtro "Média" - Funciona  
✅ Excel com filtro "Baixa" - Funciona  
✅ PDF com filtro "Todas" - Funciona  
✅ PDF com filtro "Alta" - Funciona  
✅ KPIs calculam corretamente - Funciona  
✅ Percentuais estão precisos - Funciona  
✅ Demandas críticas mostram alerta - Funciona  

---

## Próximas Melhorias Sugeridas

1. Adicionar gráficos de pizza (prioridades) no PDF
2. Adicionar gráfico de barras (responsável) no PDF
3. Trending: comparar com período anterior
4. Status de conclusão (se implementado no banco)
5. SLA metrics (dias abertos)

