# Funcionalidade de Exportação de Dados

## Resumo
Implementação de sistema de exportação de demandas em formatos **Excel** e **PDF**, com popup de seleção na tela home.

## Requisitos Atendidos

### ✅ Obrigatórios
- **PDF ou CSV ou Excel**: Ambos os formatos (Excel e PDF) estão funcionando
- **Pelo menos um formato funcionando**: Ambos os formatos estão 100% operacionais

### ✅ Detalhes
- **Cabeçalho com nome da empresa**: Cada relatório inclui `SGDI - Sistema de Gestão de Demandas` (configurável via `COMPANY_NAME` env)
- **Data de geração do relatório**: Hora e data precisas em ambos os formatos
- **Filtros aplicados no rodapé**: Os filtros de prioridade são exibidos no rodapé do PDF e no cabeçalho do Excel

## Arquivos Alterados

### Backend (`app.py`)
- Adicionados imports: `BytesIO`, `send_file`, `openpyxl`, `reportlab`
- Novas funções:
  - `get_company_name()` - Retorna o nome da empresa (configurável)
  - `format_priority_filter_label()` - Formata rótulo do filtro
  - `build_export_header()` - Constrói cabeçalho do relatório
  - `build_demandas_data()` - Formata dados para exportação
  - `export_excel()` - Rota POST `/export/excel`
  - `export_pdf()` - Rota POST `/export/pdf`

### Frontend (`templates/index.html`)
- Adicionado botão **📥 Exportar** na toolbar
- Modal com duas opções:
  - Excel (XLSX)
  - PDF
- JavaScript para controlar abertura/fechamento do modal
- Suporte a teclado (Escape para fechar)
- Acessibilidade com `aria-label` e `aria-hidden`

### Estilos (`static/style.css`)
- Estilos do modal com glassmorphism
- Animações (fade-in, slide-up)
- Responsividade para mobile
- Suporte a dark mode
- Botões de exportação com ícones e descrição

### Dependências (`requirements.txt`)
```
openpyxl==3.1.2        # Para exportação em Excel
reportlab==4.0.9       # Para exportação em PDF
```

## Como Usar

### Instalação
```bash
pip install -r requirements.txt
```

### Funcionalidade no navegador
1. Acesse a página inicial (`/`)
2. Clique no botão **📥 Exportar**
3. Escolha o formato desejado (Excel ou PDF)
4. O arquivo será baixado automaticamente

### Configuração
Para personalizar o nome da empresa no relatório, defina a variável de ambiente:
```bash
export COMPANY_NAME="Sua Empresa"
```

Ou no `.env`:
```
COMPANY_NAME=Sua Empresa
```

## Estrutura dos Relatórios

### Excel
```
┌─────────────────────────────────────┐
│  SGDI - Sistema de Gestão de Demandas
│  Gerado em: 27/05/2026 14:30:45
│  Filtro: Prioridade Alta
├─────────────────────────────────────┤
│  ID │ Título │ Solicitante │ ...
├─────────────────────────────────────┤
│  1  │ ...    │ ...         │ ...
│  2  │ ...    │ ...         │ ...
└─────────────────────────────────────┘
```

### PDF
```
┌─────────────────────────────────────────┐
│   SGDI - Sistema de Gestão de Demandas
│   Data de geração: 27/05/2026 14:30:45
│   Filtro: Prioridade Alta
├─────────────────────────────────────────┤
│  Tabela formatada com cores e espaçamento
└─────────────────────────────────────────┘
Rodapé: "Relatório gerado com: Prioridade Alta · May–May 2026"
```

## Filtros Aplicados
- Os filtros de prioridade da tela principal são preservados na exportação
- Se nenhum filtro está ativo, a opção "Todas as prioridades" é registrada
- Prioridades suportadas: Alta, Média, Baixa

## Segurança
- As rotas POST requerem validação do formulário
- Dados são processados apenas a partir da sessão do usuário
- Sem exposição de informações sensíveis

## Testes
```bash
# Testar as rotas de exportação
python -c "
from app import app
with app.test_client() as client:
    excel = client.post('/export/excel', data={'prioridade_filtro': 'todas'})
    pdf = client.post('/export/pdf', data={'prioridade_filtro': 'todas'})
    assert excel.status_code == 200
    assert pdf.status_code == 200
    print('✓ Ambas rotas funcionam!')
"
```

## Melhorias Futuras
- [ ] Adicionar exportação em CSV
- [ ] Permitir seleção de colunas antes de exportar
- [ ] Suporte a relatórios agendados por email
- [ ] Gráficos nos PDFs
- [ ] Compressão de múltiplos relatórios em ZIP

## Notas
- Os arquivos Excel e PDF são gerados em memória (BytesIO) para melhor performance
- Os nomes dos arquivos incluem timestamp para evitar conflitos
- O modal é totalmente acessível para leitores de tela

