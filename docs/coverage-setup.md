# Coverage com Pytest e SonarQube

### Passo 1: Rodar testes com coverage
```powershell
pytest --cov=. --cov-report=xml --cov-report=term-missing
```

Isso gera:
- `coverage.xml` (para SonarQube ler)
- Relatório no terminal (mostra linhas não cobertas)


### Passo 2: Subir SonarQube (se não estiver)
```powershell
docker run -d --name sonarqube -p 9000:9000 sonarqube:lts-community
```
Acesse: http://localhost:9000

### Passo 3: Rodar scanner
```powershell
$env:SONAR_TOKEN="SEU_TOKEN_AQUI"
sonar-scanner -Dsonar.host.url=http://localhost:9000 -Dsonar.login=$env:SONAR_TOKEN
```

SonarQube agora mostrará:
- Cobertura geral do projeto
- Cobertura por arquivo
- Linhas não cobertas

## 📊 Observações

- **Coverage exclui automaticamente:** migrations, testes, __pycache__, venv
- **Exclusões do Sonar:** migrations/versions/**, **/__pycache__/**, .sonar/**

