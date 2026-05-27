# 🚀 Quick Start - Logging com Loki & Grafana

## Comece em 3 minutos!

### 1️⃣ Instalar dependências
```bash
pip install -r requirements.txt
```

### 2️⃣ Iniciar Stack (Docker)
```bash
docker-compose up -d
```

Acompanhe:
```bash
docker-compose logs -f
```

### 3️⃣ Acessar Consoles

| Serviço | URL | Login |
|---------|-----|-------|
| **Grafana** | http://localhost:3000 | admin / admin |
| **Loki** | http://localhost:3100 | N/A |
| **Prometheus** | http://localhost:9090 | N/A |

### 4️⃣ Visualizar Dashboard

1. Acesse Grafana: http://localhost:3000
2. Menu > Dashboards > SGDI Application Logs
3. Veja logs em tempo real! 📊

---

## 🔍 Queries Úteis no Grafana

### Todos os logs
```
{app="sgdi-sistema-legado"}
```

### Erros apenas
```
{app="sgdi-sistema-legado"} | json | level="error"
```

### Por request_id
```
{app="sgdi-sistema-legado"} | json | request_id="<uuid>"
```

---

## 🛑 Parar Tudo
```bash
docker-compose down
```

---

Para documentação completa: ver `docs/LOGGING_GUIDE.md`

