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

## B) Construção da Skill

### Decisões de design

- **SKILL.md** como orquestrador com **Invocation Matrix**: cada fase carrega apenas os arquivos de referência necessários (análise → catálogo/template → guidelines/playbook/validação).
- **6 arquivos de referência** em `references/`, cobrindo as 5 áreas obrigatórias:
  - `analysis-heuristics.md` — detecção de stack e mapeamento arquitetural
  - `anti-patterns-catalog.md` — 12 anti-patterns com severidade e sinais grep-acionáveis
  - `audit-report-template.md` — formato padronizado da Fase 2
  - `mvc-target-guidelines.md` — regras MVC alvo por stack
  - `refactoring-playbook.md` — 10 transformações com exemplos antes/depois
  - `phase3-validation.md` — smoke tests, portas, `seed.py`, checklist

### Anti-patterns no catálogo (amostra)

| Anti-pattern | Severidade | Por quê |
|---|---|---|
| SQL Injection por concatenação | CRITICAL | Presente no monolito Flask (`models.py`) |
| Endpoint de SQL arbitrário | CRITICAL | Rota admin intencional — documentar, não remover às cegas |
| Credenciais hardcoded | CRITICAL | Comum nos 3 projetos |
| God Class / God Module | CRITICAL | `models.py` e `AppManager.js` |
| Vazamento de segredos em HTTP | HIGH | Health check e `to_dict()` com senha |
| Fat routes | HIGH | Express checkout e Flask task routes |
| Estado global mutável | HIGH | `globalCache` no Express |
| N+1 queries | MEDIUM | Pedidos, relatórios, tasks |
| Callback hell | MEDIUM | Checkout Express com sqlite3 callbacks |
| APIs deprecated (SQLAlchemy `Model.query.get`, hash DIY) | MEDIUM | task-manager e ecommerce |
| Bare except | MEDIUM | task routes |
| Duplicação / magic numbers | LOW | Validações e regras de desconto |

### Agnosticismo de tecnologia

- Heurísticas separadas por **markers de stack** (`requirements.txt` vs `package.json`, `Blueprint` vs `express.Router`).
- Playbook com ramificações **Flask** e **Express** para o mesmo smell (ex.: God module → `models/` + `controllers/` + `views/`).
- Fase 3 **stack-aware**: monolito vira MVC completo; projeto parcial (task-manager) ganha `controllers/` e `config/` sem reescrever models existentes.
- Contratos de smoke preservados (`api.http`, campos JSON legados como `usr`/`eml`, MD5 no login do task-manager).

### Desafios e soluções

| Desafio | Solução |
|---|---|
| Smells intencionais de contrato (admin SQL, MD5, campos `password` no JSON) | Catálogo marca como CRITICAL/HIGH mas playbook diz **preservar** se `api.http`/seed dependem |
| Dois Flask na porta 5000 | `phase3-validation.md` documenta testar um por vez |
| Projeto 3 já organizado | Fase 3 extrai controllers/services em vez de recriar monolito |
| Fase 2 obrigatória com pausa | SKILL.md proíbe mutação até confirmação humana `[y/n]` |

---

## C) Resultados

### Projeto 1 — code-smells-project

**Relatório:** [`reports/audit-project-1.md`](reports/audit-project-1.md) — 10 findings (4 CRITICAL, 2 HIGH, 3 MEDIUM, 1 LOW)

**Antes → depois:**

```
Antes: app.py, controllers.py, models.py, database.py (monolito)
Depois:
  app.py (composition root)
  config/settings.py
  models/{produto,usuario,pedido}_model.py
  controllers/{produto,usuario,pedido,admin,health}_controller.py
  views/routes.py
  middlewares/error_handler.py
  validators/produto_validator.py
```

| Item | Status |
|------|--------|
| Fase 1 — stack correta (Python/Flask) | ✅ |
| Fase 2 — ≥5 findings, CRITICAL/HIGH | ✅ |
| Fase 2 — pausa antes da Fase 3 | ✅ |
| Fase 3 — estrutura MVC | ✅ |
| Fase 3 — app inicia e endpoints respondem | ✅ |

---
