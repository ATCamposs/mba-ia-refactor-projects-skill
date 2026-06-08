# Desafio Skills — Refatoração Arquitetural Automatizada

Repositório do desafio MBA IA: análise manual, skill `refactor-arch` e refatoração MVC nos 3 projetos legados do monorepo.

---

## A) Análise Manual

Problemas identificados por leitura direta do código **antes** da skill. Detalhes por projeto também estão nos READMEs locais.

### code-smells-project (Python/Flask — E-commerce)

| # | Severidade | Problema | Local | Justificativa |
|---|------------|----------|-------|---------------|
| 1 | **CRITICAL** | SQL Injection por concatenação | `models.py:28,47-49,110,291` | Queries montadas com `+` e strings interpoladas. Permite execução arbitrária de SQL. |
| 2 | **CRITICAL** | God module monolítico | `models.py:1-315` | CRUD de 4 domínios (produtos, usuários, pedidos, relatórios) em um único arquivo. |
| 3 | **MEDIUM** | N+1 queries em pedidos | `models.py:187-199` | Loop dispara queries extras por pedido para itens e produtos. |
| 4 | **MEDIUM** | Credenciais hardcoded | `app.py:7` | `SECRET_KEY` fixa no código, sem variável de ambiente. |
| 5 | **LOW** | Duplicação de validação | `controllers.py:24-96` | `criar_produto` e `atualizar_produto` repetem as mesmas regras. |
| 6 | **LOW** | Magic numbers em desconto | `models.py:257-262` | Faixas de faturamento e percentuais soltos em `relatorio_vendas`. |

### ecommerce-api-legacy (Node.js/Express — LMS + checkout)

| # | Severidade | Problema | Local | Justificativa |
|---|------------|----------|-------|---------------|
| 1 | **CRITICAL** | Credenciais hardcoded | `src/utils.js:1-7` | `dbPass`, `paymentGatewayKey` e `smtpUser` em literal no repositório. |
| 2 | **CRITICAL** | Dados de cartão em log | `src/AppManager.js:45` | `console.log` do PAN (`cc`) junto com chave do gateway — violação PCI. |
| 3 | **HIGH** | God Class | `src/AppManager.js:4-138` | Schema, seeds, rotas, checkout, matrícula e relatório no mesmo módulo. |
| 4 | **MEDIUM** | N+1 no relatório financeiro | `src/AppManager.js:89-127` | Callbacks aninhados com queries por curso/enrollment/pagamento. |
| 5 | **MEDIUM** | Hash inseguro (`badCrypto`) | `src/utils.js:17-23` | Concatenação base64 — não é hash criptográfico. |
| 6 | **LOW** | Nomenclatura críptica | `src/AppManager.js:29-33` | Variáveis de uma letra (`u`, `e`, `cc`) em fluxo de pagamento. |

### task-manager-api (Python/Flask — Task Manager)

| # | Severidade | Problema | Local | Justificativa |
|---|------------|----------|-------|---------------|
| 1 | **CRITICAL** | Hash MD5 sem salt | `models/user.py:29-32` | Algoritmo obsoleto, vulnerável a rainbow tables. |
| 2 | **CRITICAL** | SECRET_KEY hardcoded | `app.py:13` | Chave fixa no composition root. |
| 3 | **HIGH** | Rotas gordas | `routes/task_routes.py:11-63` | Validação, regra de negócio e serialização na camada de rota. |
| 4 | **MEDIUM** | N+1 em listagem de tasks | `routes/task_routes.py:41-57` | `User.query.get` e `Category.query.get` por task no loop. |
| 5 | **MEDIUM** | Config inline no app | `app.py:11-13` | DB URI e SECRET_KEY sem módulo `config/`. |
| 6 | **LOW** | `except:` nu | `routes/task_routes.py:62,236` | Engole qualquer exceção sem log. |
| 7 | **LOW** | Overdue duplicado | `routes/task_routes.py:30-39` vs `models/task.py:50-60` | Model tem `is_overdue()` mas rotas reimplementam inline. |

---
