# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
npm install
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot.

Exemplos de requisições estão em `api.http`.

## Análise Manual

Problemas identificados por leitura direta do código antes da skill `refactor-arch`. O projeto concentra roteamento, persistência e regras de negócio em poucos arquivos sem separação MVC.

| # | Severidade | Problema | Local | Justificativa |
|---|------------|----------|-------|---------------|
| 1 | **CRITICAL** | Credenciais hardcoded | `src/utils.js:1-7` | `dbPass`, `paymentGatewayKey` e `smtpUser` em literal no repositório. Exposição de segredos de produção e impossibilidade de configuração por ambiente. |
| 2 | **CRITICAL** | Dados de cartão em log | `src/AppManager.js:45` | Checkout faz `console.log` do número do cartão (`cc`) junto com a chave do gateway. Violação grave de PCI e risco de vazamento em logs. |
| 3 | **HIGH** | God Class (rotas + DB + negócio) | `src/AppManager.js:4-138` | Classe única cria schema, seeds, define rotas Express, processa pagamento, matrícula e relatório financeiro. Impossível testar ou evoluir camadas em isolamento. |
| 4 | **MEDIUM** | N+1 queries no relatório financeiro | `src/AppManager.js:89-127` | Para cada curso, enrollment e pagamento dispara callbacks aninhados com queries separadas (`courses` → `enrollments` → `users` → `payments`). Escala mal com volume de dados. |
| 5 | **MEDIUM** | Hash de senha inseguro | `src/utils.js:17-23` | `badCrypto` concatena base64 em loop — não é função de hash criptográfica. Senhas de novos usuários no checkout ficam trivialmente reversíveis/previsíveis. |
