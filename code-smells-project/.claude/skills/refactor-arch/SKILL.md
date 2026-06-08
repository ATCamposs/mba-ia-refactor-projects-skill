---
name: refactor-arch
description: >-
  Auditoria arquitetural e refatoração MVC em projetos Flask (Python) e Express
  (Node.js). Executa 3 fases sequenciais — análise de stack, auditoria com
  relatório estruturado e refatoração para MVC — de forma agnóstica de linguagem.
---

# Refactor Architecture (refactor-arch)

Skill agnóstica de stack para analisar, auditar e refatorar APIs legadas para o
padrão MVC. Funciona em monolitos Flask e Express com diferentes níveis de
organização — do código totalmente desestruturado ao projeto com `routes/` mas
sem controllers dedicados.

## Objetivo

1. **Fase 1 — Análise:** mapear stack, domínio e arquitetura atual (somente leitura).
2. **Fase 2 — Auditoria:** cruzar código com catálogo de anti-patterns; emitir relatório; **pausar** para confirmação humana.
3. **Fase 3 — Refatoração:** aplicar playbook MVC stack-aware; validar boot e endpoints.

## Protocolo de invocação

1. Identificar a fase solicitada (padrão: executar 1 → 2 → 3 em sequência).
2. Consultar a **Invocation Matrix** abaixo e carregar **todos** os arquivos MUST da fase antes de agir.
3. Carregar arquivos SHOULD apenas quando o gatilho da coluna se aplicar.
4. **Fase 1:** proibido mutar arquivos do projeto — apenas leitura e impressão do resumo.
5. **Fase 2:** proibido mutar arquivos até o humano confirmar após o relatório.
6. **Fase 3:** mutar somente após confirmação; validar aplicação ao final.

## Invocation Matrix

| Reference file | MUST load when | SHOULD load when |
|---|---|---|
| `references/analysis-heuristics.md` | **Fase 1** — detectar linguagem, framework, dependências, domínio, arquitetura, arquivos fonte e tabelas DB | Re-análise após refatoração parcial |
| `references/anti-patterns-catalog.md` | **Fase 2** — cruzar código contra catálogo de smells e severidades | Fase 1 quando arquitetura já revela God Class ou SQLi óbvio |
| `references/audit-report-template.md` | **Fase 2** — formatar relatório de auditoria com arquivo:linha e recomendação | — |
| `references/mvc-target-guidelines.md` | **Fase 3** — definir estrutura MVC alvo (config, models, views, controllers, middlewares) | Fase 2 ao classificar violações de camada |
| `references/refactoring-playbook.md` | **Fase 3** — aplicar transformações concretas por anti-pattern | Fase 2 ao redigir recomendações acionáveis |
| `references/phase3-validation.md` | **Fase 3** — validação boot+endpoints (portas, `seed.py`, curls, checklist smoke) | Smoke falha após refatoração |

## Fase 1 — Análise

**Pré-requisito:** carregar `references/analysis-heuristics.md` (MUST).

**Restrição:** esta fase é **read-only** — não criar, editar nem deletar arquivos do projeto.

### Passos

1. **Detectar linguagem** — presença de `*.py`, `*.js`/`*.ts`, `requirements.txt`, `package.json`.
2. **Detectar framework** — Flask (`from flask import`, `app = Flask`), Express (`express()`, `app.get/post`).
3. **Listar dependências** — ler `requirements.txt` (Python) ou `package.json` → `dependencies` (Node).
4. **Inferir domínio** — nomes de rotas, models e tabelas (e-commerce, LMS/checkout, task manager, etc.).
5. **Mapear arquitetura atual** — monolito flat, pastas `routes/`/`models/`, God class única, etc.
6. **Inventariar arquivos fonte** — contar `*.py` ou `src/**/*.js` excluindo `node_modules` e `.git`.
7. **Mapear tabelas DB** — `CREATE TABLE`, models ORM, ou schema em `database.py` / migrations.

### Ramificações por stack

| Sinal | Flask (Python) | Express (Node.js) |
|---|---|---|
| Entry point | `app.py`, `wsgi.py` | `app.js`, `src/app.js`, `index.js` |
| Rotas | `@app.route`, `add_url_rule`, Blueprints | `app.get/post`, `Router()` |
| Persistência | `sqlite3`, SQLAlchemy, raw SQL em `models.py` | `sqlite3`, ORM em módulos dedicados |
| Config | `app.config[...]` hardcoded | `utils.js`, `config` object |

Não acoplar a um projeto específico — usar heurísticas genéricas acima.

### Formato de saída (console)

Imprimir exatamente neste formato após a análise:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem detectada>
Framework:     <framework e versão se disponível>
Dependencies:  <lista resumida de deps principais>
Domain:        <domínio da aplicação>
Architecture:  <descrição da organização atual>
Source files:  <N> files analyzed
DB tables:     <tabela1>, <tabela2>, ...
================================
```

### Transição

Ao concluir a Fase 1, informar que a Fase 2 pode iniciar e aguardar instrução ou prosseguir automaticamente se o usuário invocou o fluxo completo.

## Fase 2 — Auditoria

**Pré-requisitos MUST:** `references/anti-patterns-catalog.md`, `references/audit-report-template.md`.

**Restrição absoluta:** esta fase é **somente leitura** em relação ao projeto — **proibido** refatorar, mover, criar ou deletar arquivos de código. Apenas analisar, relatar e persistir o relatório.

### Passos

1. **Inventariar arquivos fonte** — mesma contagem da Fase 1 (excluir `node_modules`, `.git`, `venv`).
2. **Varrer o código** — cruzar cada arquivo contra **todos** os anti-patterns do catálogo, incluindo a seção **APIs deprecated** (Flask `Markup`, `request.json` sem guard, MD5, callback hell, hash DIY).
3. **Registrar findings** — para cada achado:
   - Severidade: **CRITICAL**, **HIGH**, **MEDIUM** ou **LOW** (escala do README raiz do monorepo).
   - Localização obrigatória: `arquivo:relative:linha` ou intervalo `linha-linha_fim`.
   - Description, Impact e Recommendation alinhados ao catálogo.
4. **Ordenar** findings na seção `## Findings`: **CRITICAL → HIGH → MEDIUM → LOW**; dentro da mesma severidade, por caminho de arquivo.
5. **Emitir relatório** no console usando o template literal de `references/audit-report-template.md` (cabeçalho `ARCHITECTURE AUDIT REPORT`, Summary por severidade, blocos `### [SEVERITY] Title`, rodapé com total).
6. **Persistir** cópia Markdown na **raiz do monorepo** (nunca em `reports/` dentro do subprojeto):

   | Projeto | Arquivo (relativo à raiz do monorepo) |
   |---|---|
   | E-commerce Flask flat | `reports/audit-project-1.md` |
   | LMS Express | `reports/audit-project-2.md` |
   | Task Manager Flask parcial | `reports/audit-project-3.md` |

   Quando `cwd` é um subprojeto (ex.: `ecommerce-api-legacy/`), gravar em `../reports/audit-project-N.md`. Criar `reports/` na raiz se ausente.

### Gate HITL obrigatório

Após imprimir o relatório e persistir o arquivo:

1. **PARAR** — não iniciar Fase 3 nem modificar código.
2. Exibir exatamente: `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`
3. Aguardar confirmação explícita do humano (`y` / `yes` / `sim` → prosseguir; qualquer outra resposta → encerrar).
4. Sem confirmação afirmativa, **Fase 3 permanece bloqueada**.

### Formato de saída (exemplo resumido)

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome>
Stack:   <linguagem> + <framework>
Files:   <N> analyzed | ~<LOC> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings
### [CRITICAL] <título>
File: <arquivo>:<linha>
...
================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

### Transição

Somente após resposta `y` à pergunta HITL, carregar refs da Fase 3 e iniciar refatoração.

## Fase 3 — Refatoração + validação

**Pré-requisitos MUST:** `references/mvc-target-guidelines.md`, `references/refactoring-playbook.md`, `references/phase3-validation.md`.

**Pré-condição:** confirmação humana explícita ao final da Fase 2.

### Princípios

- Aplicar transformações do playbook de forma **stack-aware** (Python/Flask vs Node/Express).
- Seguir árvore MVC de `mvc-target-guidelines.md` (`config/`, `models/`, `views/`, `controllers/`, `middlewares/`, composition root `app.py` / `app.js`).
- **Preservar contratos de API:** URLs, métodos HTTP, status codes e shapes de JSON observáveis (`api.http`, README, smoke existente) — inclusive smells intencionais listados em "Contrato vs smell intencional" (ex.: `/admin/query`, `startsWith("4")`, MD5/`password` em login-detalhe, token fake).
- Adaptar quando o projeto já tem `routes/` ou `services/` parciais — adicionar `controllers/` sem quebrar endpoints.

### Passos

1. **Planejar** — mapear cada finding confirmado a uma entrada do playbook (priorizar CRITICAL/HIGH).
2. **Estrutura** — criar diretórios MVC; composition root só faz wiring.
3. **Config** — extrair `SECRET_KEY`, chaves de gateway, SMTP para `config/` + env.
4. **Models** — queries parametrizadas (exceto contratos intencionais); sem HTTP nos models.
5. **Controllers** — fluxo validação → model → resposta; rotas/views finas.
6. **Middlewares** — error handler centralizado (substituir bare `except` espalhados).
7. **Validar boot:**
   - Flask: `python app.py` (ou entry point do projeto).
   - Express: `npm start`.
8. **Smoke de endpoints** — health, CRUD principal, login ou checkout conforme domínio; comparar com contrato pré-refatoração. Usar `api.http` na raiz do projeto ou curls equivalentes em `references/phase3-validation.md` (ordem: `seed.py` → boot → smoke; atenção ao conflito de porta **5000** entre os dois Flask).
9. **Iterar** se validação falhar — ajustar refs e código; esperar **2–4 ciclos** até boot + smoke verdes.
10. **Imprimir** bloco final obrigatório:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios criada>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ API contracts preserved (urls, methods, response shapes)
  ✓ Zero unresolved CRITICAL anti-patterns (or documented intentional)
================================
```

### MUST NOT (Fase 3)

- MUST NOT remover ou alterar comportamento de endpoints de contrato intencional sem evidência de que smoke não exige.
- MUST NOT iniciar sem gate HITL da Fase 2.
- MUST NOT declarar conclusão sem boot e smoke bem-sucedidos.

## MUST DO / MUST NOT

- MUST carregar refs via matrix antes de cada fase.
- MUST manter skill reutilizável — copiar pasta `.claude/skills/refactor-arch/` intacta entre projetos.
- MUST NOT pular confirmação humana entre Fase 2 e Fase 3.
- MUST NOT alterar arquivos na Fase 1.
- MUST NOT remover endpoints sem preservar contrato observável documentado no projeto.

## Estrutura de referências

Conhecimento de domínio vive em `references/` — este `SKILL.md` é apenas o orquestrador:

- `references/analysis-heuristics.md` — heurísticas de detecção (Fase 1)
- `references/anti-patterns-catalog.md` — catálogo com severidades (Fase 2)
- `references/audit-report-template.md` — template do relatório (Fase 2)
- `references/mvc-target-guidelines.md` — regras MVC alvo (Fase 3)
- `references/refactoring-playbook.md` — transformações antes/depois (Fase 3)
- `references/phase3-validation.md` — boot, portas, curls e checklist de smoke (Fase 3)
