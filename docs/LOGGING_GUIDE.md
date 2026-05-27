# Logging com Loki e Grafana

Este documento descreve como usar o sistema de logging centralizado com **Loki** e **Grafana** no projeto SGDI.

## 📋 Componentes

- **Loki**: Agregador de logs (time-series database para logs)
- **Grafana**: Visualização e dashboards
- **Prometheus**: Métricas e monitoramento (opcional)

## 🚀 Quick Start

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Iniciar stack (Docker)
```bash
docker-compose up -d
```

Serviços iniciados:
- **Loki**: http://localhost:3100
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000

### 3. Acessar Grafana
- URL: http://localhost:3000
- Usuário: `admin`
- Senha: `admin`

O datasource **Loki** e o dashboard **SGDI Application Logs** já estão configurados automaticamente.

## 📊 Dashboards Disponíveis

### SGDI Application Logs
Localização: **Home > Dashboards > SGDI > SGDI Application Logs**

**Painéis inclusos**:
1. **Application Logs** - Todos os logs em tempo real com filtros
2. **Log Levels Distribution** - Pizza com distribuição de níveis (last 5min)
3. **Log Rate** - Gráfico de taxa de logs/seg
4. **Error Logs** - Contador de erros (last 15min)

## 🔍 Queries Loki Úteis

### Todos os logs da aplicação
```
{app="sgdi-sistema-legado"}
```

### Apenas erros
```
{app="sgdi-sistema-legado"} | json level="error"
```

### Logs de autenticação
```
{app="sgdi-sistema-legado"} | json msg=~".*[Aa]uthent.*"
```

### Logs com request_id específico
```
{app="sgdi-sistema-legado"} | json request_id="<uuid>"
```

### Taxa de logs por segundo
```
rate(count_over_time({app="sgdi-sistema-legado"}[1m])[1m:10s])
```

### Erros por serviço
```
sum by (service) (count_over_time({app="sgdi-sistema-legado", level="error"}[5m]))
```

## 🐍 Usando Logs no Código Python

### Setup (automático na API)
```python
from services.logging import setup_logging, get_logger

# Inicializa logging com Loki
app = Flask(__name__)
setup_logging(app, loki_enabled=True)
logger = get_logger('sgdi.routes')
```

### Logging simples
```python
logger.info('Usuário autenticado')
logger.warning('Rate limit próximo')
logger.error('Erro ao conectar ao banco')
logger.debug('Debug info para desenvolvimento')
```

### Logging com contexto (recomendado)
```python
from services.logging import log_with_context

log_with_context(
    logger, 
    'info',
    'Demanda criada',
    demanda_id=123,
    usuario='joao.silva',
    request_id=request.request_id
)
```

### Request Tracking
Cada requisição recebe um `request_id` único automaticamente para rastreamento:

```python
@app.route('/api/demandas')
def listar_demandas():
    request_id = request.request_id  # UUID gerado automaticamente
    logger.info('Listando demandas', extra={'request_id': request_id})
```

## 📈 Variáveis de Ambiente

Criar arquivo `.env` na raiz do projeto:

```env
# Habilitar Loki
LOKI_ENABLED=true

# URL do Loki (padrão: http://localhost:3100)
LOKI_URL=http://localhost:3100

# Ambiente (development, staging, production)
ENVIRONMENT=development

# Nome do serviço
SERVICE_NAME=sgdi-main
```

## 🔧 Configuração Avançada

### Customizar o dashboard
1. Editar em Grafana: **Home > Dashboards > SGDI Application Logs**
2. Adicionar novos painéis conforme necessário
3. Exportar e salvar em `docker/grafana/provisioning/dashboards/dashboards/`

### Alterar retenção de logs
Editar `docker/loki-config.yaml`:
```yaml
limits_config:
  retention_period: 720h  # 30 dias (padrão)
```

### Aumentar limite de logs por minuto
```yaml
limits_config:
  ingestion_rate_mb: 10  # MB por minuto
```

## 🛑 Parar e Limpar

```bash
# Parar containers
docker-compose down

# Parar e remover volumes (cuidado: apaga dados)
docker-compose down -v
```

## 🐛 Troubleshooting

### Grafana não conecta a Loki
```bash
docker-compose logs loki
docker-compose logs grafana
```

### Logs não aparecem no Grafana
1. Verificar se `LOKI_ENABLED=true` no `.env`
2. Confirmar que a aplicação está rodando: `curl http://localhost:5000/`
3. Restart da aplicação

### Dashboard não carrega
1. Verificar se arquivo existe: `docker/grafana/provisioning/dashboards/dashboards/sgdi-logs.json`
2. Reiniciar Grafana: `docker-compose restart grafana`

## 📚 Recursos

- [Loki Documentation](https://grafana.com/docs/loki/latest/)
- [Grafana Dashboards](https://grafana.com/docs/grafana/latest/dashboards/)
- [LogQL Query Syntax](https://grafana.com/docs/loki/latest/logql/)
- [Python Logging Best Practices](https://docs.python.org/3/howto/logging-cookbook.html)

---

**Última atualização**: 2026-05-26

