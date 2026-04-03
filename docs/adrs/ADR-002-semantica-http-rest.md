# ADR-002: Alinhar rotas com semantica HTTP/REST

## Data
03/04/2026

## Status
Aceito

## Contexto
No changelog e commits (`6675f5c`) foram feitas mudancas de rotas para tipagem explicita (`<int:demanda_id>`) e uso de verbo `DELETE` para exclusao. O frontend em `templates/index.html` passou a chamar `fetch` para deletar demanda.

## Decisao
Adotar semantica HTTP explicita nas rotas criticas:
- `GET` para leitura/listagem/busca.
- `POST` para criacao e atualizacao por formulario.
- `DELETE` para exclusao.

## Alternativas Consideradas
- Opcao 1: manter exclusao por `GET` com link direto.
- Opcao 2: migrar todas as rotas para API JSON pura.

## Consequencias

### Positivas
- Pros: reduz risco de acao destrutiva acidental por link GET.
- Pros: melhora previsibilidade para frontend e testes.
- Pros: prepara evolucao futura para API sem quebrar semantica.

### Negativas (trade-offs)
- Custo: exige JavaScript no frontend para acionar `DELETE`.
- Custo: precisa reforcar protecoes de seguranca para metodos unsafe (CSRF).

