# Quality Gate

Use os plugins do SonarQube e do Qodana durante o desenvolvimento para elevar continuamente a qualidade do código. A adoção segue a filosofia **Clean as You Code**: cada alteração deve deixar o código melhor do que estava antes, com foco em corrigir problemas no código novo e alterado.

Este guia centraliza como rodar análise de qualidade com SonarQube e Qodana.

## 1) SonarQube

### Pre-requisitos

- Docker instalado (para subir o SonarQube localmente).
- `sonar-scanner` instalado e disponível no PATH.
- Token de acesso no SonarQube (exemplo: `SONAR_TOKEN`).

### Subir SonarQube local

```powershell
docker run -d --name sonarqube -p 9000:9000 sonarqube:lts-community
```

Acesse: `http://localhost:9000`

### Rodar análise com sonar-scanner

No diretório raiz do projeto:

```powershell
$env:SONAR_TOKEN="SEU_TOKEN"
sonar-scanner -Dsonar.projectKey=sistema-legado -Dsonar.projectName="SistemaLegado" -Dsonar.sources=. -Dsonar.host.url=http://localhost:9000 -Dsonar.login=$env:SONAR_TOKEN
```

## 2) Qodana

O projeto já possui configuração em `qodana.yaml`.

### Rodar via Docker

No diretório raiz do projeto:

```powershell
docker run --rm -it -v "${PWD}:/data/project" -p 8080:8080 jetbrains/qodana-python:2025.3
```

### Rodar via Qodana CLI (opcional)

```powershell
qodana scan --project-dir . --config qodana.yaml
```

## 3) Pipeline recomendada

1. Executar testes automatizados (`pytest`).
2. Rodar SonarQube para métricas e quality gate.
3. Rodar Qodana para inspeções estáticas adicionais.
4. Bloquear merge se houver falha no quality gate.

