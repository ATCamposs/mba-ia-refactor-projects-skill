================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express 4.18.2 / SQLite (in-memory)
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 3 | HIGH: 2 | MEDIUM: 5 | LOW: 1

## Findings

### [CRITICAL] Credenciais hardcoded
File: src/utils.js:1-7
Description: Objeto `config` expõe `dbPass`, `paymentGatewayKey` e `smtpUser` como literais string no repositório, sem leitura de variáveis de ambiente.
Impact: Vazamento via repositório; impossível rotação por ambiente (anti-pattern: Credenciais hardcoded).
Recommendation: Extrair para `config/` com `process.env` e fallback dev documentado conforme playbook "Mover SECRET_KEY e credenciais para config/env".

### [CRITICAL] Dados de cartão e chave de gateway em log
File: src/AppManager.js:45
Description: Checkout faz `console.log` do número completo do cartão (`cc`) junto com `config.paymentGatewayKey` durante processamento de pagamento.
Impact: Violação grave de PCI; risco de vazamento de PAN e credenciais de gateway em logs de aplicação e agregadores.
Recommendation: Remover log de dados sensíveis; registrar apenas identificadores de transação mascarados; manter lógica `startsWith("4")` como contrato intencional de smoke.

### [CRITICAL] God Class monolítica
File: src/AppManager.js:4-138
Description: Classe única `AppManager` cria schema SQLite, seeds, define rotas Express (`setupRoutes`), processa checkout, matrícula, pagamento e relatório financeiro no mesmo módulo (~135 LOC de responsabilidades mistas).
Impact: Impossível testar camadas em isolamento; mudança local quebra múltiplos fluxos (anti-pattern: God Class / God Module).
Recommendation: Separar `models/`, `controllers/`, `views/routes/` por domínio; composition root `app.js` só faz wiring (playbook "Extrair God module").

### [HIGH] Estado global mutável
File: src/utils.js:9-15
Description: `globalCache` e `totalRevenue` são variáveis de módulo mutadas em runtime via `logAndCache`; `totalRevenue` é exportado mas nunca atualizado no fluxo atual.
Impact: Acoplamento entre requisições; testes flaky; estado compartilhado imprevisível sob concorrência (anti-pattern: Estado global mutável).
Recommendation: Encapsular cache em factory ou contexto de aplicação; injetar dependência no composition root; remover ou usar `totalRevenue` de forma explícita.

### [HIGH] Fat routes / lógica pesada em handlers HTTP
File: src/AppManager.js:28-78
Description: Handler `POST /api/checkout` concentra validação de body, lookup de curso/usuário, hash de senha, simulação de gateway, inserts encadeados e resposta HTTP em um único callback sem camada `controllers/`.
Impact: Viola MVC; regras de negócio indissociáveis do transporte HTTP (anti-pattern: Fat routes).
Recommendation: Extrair `CheckoutController` com métodos testáveis; rotas apenas delegam (playbook "Fat route → controller").

### [MEDIUM] Callback hell no checkout
File: src/AppManager.js:37-76
Description: Fluxo de checkout aninha 4+ níveis de `db.get`/`db.run` com callbacks, incluindo função interna `processPaymentAndEnroll` e closures sobre `self`.
Impact: Fluxo ilegível; tratamento de erro inconsistente entre níveis (anti-pattern: Callback hell).
Recommendation: Promisificar acesso SQLite (`util.promisify` ou `sqlite` async) e usar `async/await`, ou extrair funções nomeadas por etapa.

### [MEDIUM] N+1 queries no relatório financeiro
File: src/AppManager.js:89-127
Description: Para cada curso, o handler dispara `db.all` de enrollments; para cada enrollment, `db.get` de user e payment — padrão O(cursos × matrículas) de round-trips ao banco.
Impact: Performance degrada linearmente com volume de dados (anti-pattern: N+1 queries).
Recommendation: Consolidar em JOINs ou queries agregadas únicas por relatório.

### [MEDIUM] Callback hell no relatório financeiro
File: src/AppManager.js:89-128
Description: Relatório `GET /api/admin/financial-report` usa contadores manuais (`coursesPending`, `enrPending`) e callbacks aninhados em `forEach` para montar resposta JSON.
Impact: Race conditions sutis e fluxo difícil de auditar; erros parciais podem responder antes da conclusão (anti-pattern: Callback hell).
Recommendation: Reescrever com `async/await` e agregação SQL única, ou Promise.all com etapas nomeadas.

### [MEDIUM] Erro engolido no delete de usuário
File: src/AppManager.js:131-136
Description: Handler `DELETE /api/users/:id` ignora `err` do `db.run` e sempre responde 200 com mensagem fixa sobre matrículas/pagamentos órfãos.
Impact: Falhas de DB silenciosas; diagnóstico operacional impossível (anti-pattern: Bare except / erro engolido).
Recommendation: Verificar `err` e retornar status adequado; middleware de erro centralizado; preservar mensagem de contrato intencional sobre dados órfãos.

### [MEDIUM] Hash de senha inseguro (badCrypto)
File: src/utils.js:17-23
Description: `badCrypto` concatena fragmentos base64 em loop — não é função de hash criptográfica; usada ao criar usuário no checkout (`AppManager.js:68`).
Impact: Senhas triviais de reverter/prever; não atende requisitos mínimos de segurança (API deprecated: hash DIY).
Recommendation: Migrar para `bcrypt` ou `scrypt` em código novo; documentar se compatibilidade de smoke exigir preservar algoritmo legado.

### [LOW] Nomenclatura críptica no checkout
File: src/AppManager.js:29-33
Description: Variáveis de uma letra (`u`, `e`, `p`, `cid`, `cc`) e chaves de body abreviadas (`usr`, `eml`, `pwd`, `c_id`) em fluxo crítico de pagamento.
Impact: Legibilidade e revisão de código prejudicadas (anti-pattern: Nomenclatura críptica / magic values).
Recommendation: Renomear para nomes de domínio (`userName`, `email`, `courseId`, `cardNumber`); manter chaves JSON do contrato `api.http` inalteradas.

================================
Total: 11 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
