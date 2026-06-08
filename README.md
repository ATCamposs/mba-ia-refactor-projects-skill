# Desafio Skills — Refatoração Arquitetural Automatizada

Skill `refactor-arch` para analisar, auditar e refatorar APIs legadas para o padrão MVC. Implementada com **Claude Code** (`.claude/skills/refactor-arch/`) e testada nos 3 projetos do monorepo.

## Estrutura do repositório

```
mba-ia-refactor-projects-skill/
├── README.md
├── code-smells-project/          # Projeto 1 — Python/Flask (E-commerce)
│   └── .claude/skills/refactor-arch/
├── ecommerce-api-legacy/         # Projeto 2 — Node.js/Express (LMS + checkout)
│   └── .claude/skills/refactor-arch/
├── task-manager-api/             # Projeto 3 — Python/Flask (Task Manager)
│   └── .claude/skills/refactor-arch/
└── reports/
    ├── audit-project-1.md
    ├── audit-project-2.md
    └── audit-project-3.md
```

> A skill vive **dentro de cada projeto** (não na raiz do monorepo). Copie `.claude/skills/refactor-arch/` ao migrar para outro repositório.

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

### Resumo dos relatórios de auditoria

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---------|----------|------|--------|-----|-------|
| code-smells-project | 4 | 2 | 3 | 1 | **10** |
| ecommerce-api-legacy | 3 | 2 | 5 | 1 | **11** |
| task-manager-api | 3 | 3 | 6 | 3 | **15** |

Relatórios completos: [`reports/audit-project-1.md`](reports/audit-project-1.md), [`reports/audit-project-2.md`](reports/audit-project-2.md), [`reports/audit-project-3.md`](reports/audit-project-3.md).

### Comparação antes/depois

**code-smells-project**

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

**ecommerce-api-legacy**

```
Antes: src/app.js, AppManager.js, utils.js
Depois:
  src/app.js (composition root)
  config/settings.js
  models/{db,user,course,enrollment,payment,report,audit_log}_model.js
  controllers/{checkout,admin,user}_controller.js
  views/{checkout,admin,user}_routes.js
  services/{cache,payment}_service.js
  middlewares/error_handler.js
```

**task-manager-api**

```
Antes: app.py + routes/ (handlers gordos) + models/ + services/
Depois:
  app.py + config/settings.py
  controllers/{task,user,report}_controller.py
  services/task_service.py (N+1 resolvido com joinedload)
  routes/ (blueprints finos — só delegam)
  middlewares/error_handler.py
```

### Logs de validação (smoke tests)

```
# code-smells-project (porta 5000 — desative AirPlay Receiver no macOS se ocupada)
GET /health → 200 {"status":"ok","database":"connected",...}
GET /produtos → 200 (lista de produtos)

# task-manager-api (porta 5000, após seed.py — não rode junto com projeto 1)
GET /health → 200 {"status":"ok","timestamp":"..."}
GET /tasks → 200 (10 tasks)

# ecommerce-api-legacy (porta 3000)
Boot → "Frankenstein LMS rodando na porta 3000..."
POST /api/checkout → contrato preservado (api.http)
```

### Checklist de validação

#### Projeto 1 — code-smells-project

| Item | Status |
|------|--------|
| Fase 1 — stack correta (Python/Flask) | ✅ |
| Fase 2 — ≥5 findings, CRITICAL/HIGH | ✅ (10 findings, 4 CRITICAL) |
| Fase 2 — pausa antes da Fase 3 | ✅ |
| Fase 3 — estrutura MVC | ✅ |
| Fase 3 — app inicia e endpoints respondem | ✅ |

#### Projeto 2 — ecommerce-api-legacy

| Item | Status |
|------|--------|
| Fase 1 — stack correta (Node/Express) | ✅ |
| Fase 2 — ≥5 findings, CRITICAL/HIGH | ✅ (11 findings, 3 CRITICAL) |
| Fase 2 — pausa antes da Fase 3 | ✅ |
| Fase 3 — estrutura MVC | ✅ |
| Fase 3 — app inicia e checkout funciona | ✅ |

#### Projeto 3 — task-manager-api

| Item | Status |
|------|--------|
| Fase 1 — Python/Flask + domínio Task Manager | ✅ |
| Fase 2 — ≥5 findings em projeto parcial | ✅ (15 findings) |
| Fase 2 — pausa antes da Fase 3 | ✅ |
| Fase 3 — melhora estrutura sem quebrar API | ✅ |
| Fase 3 — endpoints respondem após refatoração | ✅ |

### Critérios de aceite

| Critério | P1 | P2 | P3 |
|----------|----|----|-----|
| Fase 1 detecta stack | ✅ | ✅ | ✅ |
| Fase 2 ≥ 5 findings | ✅ | ✅ | ✅ |
| Fase 2 ≥ 1 CRITICAL/HIGH | ✅ | ✅ | ✅ |
| Fase 3 app funciona | ✅ | ✅ | ✅ |

---

## D) Como Executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) instalado e autenticado
- Python 3.10+ (`python3`, `pip`)
- Node.js 18+ (`node`, `npm`)

### Projeto 1 — code-smells-project

```bash
cd code-smells-project
pip install -r requirements.txt
claude "/refactor-arch"
# Após Fase 2, confirmar com y para refatorar
python3 app.py
# Validar com api.http ou curl http://localhost:5000/health
```

### Projeto 2 — ecommerce-api-legacy

```bash
cd ecommerce-api-legacy
npm install
claude "/refactor-arch"
npm start
# Validar com api.http (porta 3000)
```

### Projeto 3 — task-manager-api

```bash
cd task-manager-api
pip install -r requirements.txt
python3 seed.py          # obrigatório no primeiro boot
claude "/refactor-arch"
python3 app.py
# Validar com api.http (porta 5000 — não rode junto com projeto 1)
```

### Salvar relatório de auditoria

Após a Fase 2, copie a saída do relatório para:

- `reports/audit-project-1.md` (code-smells-project)
- `reports/audit-project-2.md` (ecommerce-api-legacy)
- `reports/audit-project-3.md` (task-manager-api)

### Validar refatoração

1. Aplicação inicia sem traceback
2. `GET /health` (ou equivalente) retorna 200
3. Endpoints principais do `api.http` respondem com o mesmo contrato JSON
4. Estrutura de pastas segue `mvc-target-guidelines.md` da skill

---

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills)
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills)
