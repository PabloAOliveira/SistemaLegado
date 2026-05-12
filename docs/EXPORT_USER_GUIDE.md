# 🚀 Guia de Uso - Exportação de Dados

## Fluxo de Uso

### 1. Acessar a Tela Home
- Navegue até: `http://localhost:5000`
- Você verá a lista de demandas com dois botões na toolbar:
  - **Filtrar por Prioridade** (esquerda)
  - **📥 Exportar** (direita) ← **Novo!**
  - **+ Nova Demanda** (extrema direita)

### 2. Aplicar Filtros (Opcional)
- Selecione a prioridade desejada no dropdown:
  - Todas
  - Alta
  - Média
  - Baixa
- A lista se atualiza automaticamente

### 3. Clicar em "Exportar"
- Clique no botão **📥 Exportar**
- Um modal com glassmorphism aparecerá com duas opções

### 4. Escolher Formato

#### Opção 1: 📊 Excel
```
┌─────────────────────────────────────┐
│  📊 Excel                            │
│  Formato XLSX                        │
│  [Clique para baixar]                │
└─────────────────────────────────────┘
```
- Arquivo baixa como: `Demandas_20260527_143045.xlsx`
- Contém:
  - Cabeçalho com nome da empresa
  - Data de geração
  - Filtro aplicado
  - Tabela com dados

#### Opção 2: 📄 PDF
```
┌─────────────────────────────────────┐
│  📄 PDF                              │
│  Relatório formatado                 │
│  [Clique para baixar]                │
└─────────────────────────────────────┘
```
- Arquivo baixa como: `Demandas_20260527_143045.pdf`
- Contém:
  - Cabeçalho formatado
  - Tabela com linhas alternadas
  - Rodapé com informações do filtro

### 5. Fechar o Modal (Opcional)
- Clique no **X** no canto superior direito
- Clique fora do modal
- Pressione **ESC**

## Exemplos de Relatórios

### Relatório Excel (Filtro: Todas)
```
═══════════════════════════════════════════════════════════════════════════════
SGDI - Sistema de Gestão de Demandas
Gerado em: 27/05/2026 14:30:45
Filtro: Todas as prioridades

ID  Título                          Solicitante         Prioridade  Data Criação
1   Implementar autenticação        Joao Silva          Alta        27/05/2026 10:15
2   Corrigir bug de validação       Maria Santos        Média       26/05/2026 09:30
3   Melhorar documentação           Tech Team           Baixa       25/05/2026 14:20
```

### Relatório PDF (Filtro: Alta)
```
┌───────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│           SGDI - Sistema de Gestão de Demandas                            │
│                                                                             │
│           Data de geração: 27/05/2026 14:30:45                            │
│           Filtro: Prioridade Alta                                         │
│                                                                             │
├───┬─────────────────────────┬──────────────┬──────────┬──────────────────┤
│ID │ Título                  │ Solicitante  │Prioridade│ Data Criação     │
├───┼─────────────────────────┼──────────────┼──────────┼──────────────────┤
│1  │ Implementar             │ Joao Silva   │ Alta     │ 27/05/2026 10:15 │
│   │ autenticação            │              │          │                  │
├───┼─────────────────────────┼──────────────┼──────────┼──────────────────┤
│4  │ Migrar banco de dados   │ Tech Team    │ Alta     │ 27/05/2026 11:00 │
└───┴─────────────────────────┴──────────────┴──────────┴──────────────────┘

Relatório gerado com: Prioridade Alta · May–May 2026
```

## Dicas Úteis

### 💡 Excel é melhor para:
- Dados brutos e análise
- Importar em ferramentas externas
- Manipulação em massa
- Cálculos adicionais

### 💡 PDF é melhor para:
- Visualização e impressão
- Compartilhar relatórios formais
- Arquivar documentos
- Enviar por email

### 🔄 Preservação de Filtros
- Se você filtrou por "Prioridade Alta" e exporta
- O relatório mostrará **apenas** demandas com prioridade Alta
- O filtro aplicado aparece no cabeçalho/rodapé do relatório

### ⏰ Nomes de Arquivo
- Todos os arquivos incluem timestamp
- Evita sobrescrita acidental
- Facilita rastreabilidade

**Exemplo:**
- Arquivo 1: `Demandas_20260527_143045.xlsx` (2026-05-27 às 14:30:45)
- Arquivo 2: `Demandas_20260527_143055.xlsx` (2026-05-27 às 14:30:55)

## Acessibilidade

### ⌨️ Atalhos de Teclado
- **Tab**: Navegar entre elementos do modal
- **Enter**: Confirmar botões e selecções
- **ESC**: Fechar modal

### 🔊 Leitores de Tela
- Todos os elementos têm labels apropriados
- Modal tem `aria-hidden` para melhor leitura
- Botões descrevem sua ação claramente

## Troubleshooting

### ❌ Problema: Botão não aparece
**Solução:** Atualize a página (F5 ou Ctrl+R)

### ❌ Problema: Modal não abre
**Solução:** Verifique se JavaScript está habilitado no navegador

### ❌ Problema: Download não inicia
**Solução:** Verifique as configurações de popup/download do navegador

### ❌ Problema: Arquivo PDF/Excel corrompido
**Solução:** Tente novamente ou use o outro formato

## Configuração Avançada

### Personalizar Nome da Empresa
Edite o arquivo `.env`:
```bash
COMPANY_NAME="Minha Empresa"
```

### Mudar Formato de Data
Edite `app.py` na função `build_export_header()`:
```python
data_geracao = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
```

## Suporte
Para dúvidas ou problemas, consulte:
- Documentação: `docs/EXPORT_FEATURE.md`
- Código: `app.py` - funções `export_excel()` e `export_pdf()`

