# Heurísticas de Análise (Fase 1)

Heurísticas agnósticas para detectar stack, domínio e arquitetura atual. Use **grep**, leitura de manifestos e inventário de diretórios — nunca hardcode paths absolutos nem nomes de repositório.

## 1. Linguagem

| Sinal | Heurística | Comando sugerido |
|---|---|---|
| Python | Arquivos `*.py`, `requirements.txt`, `pyproject.toml`, shebang `#!/usr/bin/env python` | `find . -name '*.py' -not -path '*/.git/*'` |
| Node.js | `package.json`, `*.js`/`*.ts`, `node_modules/` | `test -f package.json && jq .name package.json` |
| Misto | Ambos presentes — priorizar entry point da API (Flask/Express) | Inspecionar qual `app.run` / `app.listen` existe |

**Regra:** contar apenas arquivos fonte do projeto (excluir `.git`, `node_modules`, `venv`, `__pycache__`).

## 2. Framework

### Flask (Python)

| Sinal | Padrão grep |
|---|---|
| Import | `from flask import`, `import flask` |
| App factory | `Flask(__name__)`, `app = Flask` |
| Rotas | `@app.route`, `@.*\.route`, `add_url_rule`, `Blueprint` |
| Extensões comuns | `flask_cors`, `SQLAlchemy`, `flask_sqlalchemy` |

### Express (Node.js)

| Sinal | Padrão grep |
|---|---|
| Require/import | `require('express')`, `from 'express'` |
| App | `express()`, `const app = express()` |
| Rotas | `app.get(`, `app.post(`, `app.use(`, `Router()` |
| Middleware | `app.use(cors`, `body-parser`, `express.json()` |

**Versão:** ler `requirements.txt` (`Flask==x.y`) ou `package.json` → `dependencies.express`.

## 3. Dependências

| Stack | Fonte | O que extrair |
|---|---|---|
| Python | `requirements.txt`, `Pipfile` | flask, flask-cors, sqlalchemy, sqlite3 (stdlib) |
| Node | `package.json` | `dependencies`, `devDependencies` — express, sqlite3, cors |

Listar as 3–6 dependências mais relevantes para o domínio (ORM, CORS, auth).

## 4. Banco de dados

| Sinal | Inferência |
|---|---|
| `sqlite3`, `*.db`, `:memory:` | SQLite (arquivo ou in-memory) |
| `SQLAlchemy`, `db.Model`, `create_all` | ORM SQLAlchemy sobre SQLite/Postgres |
| `CREATE TABLE` em código | Schema inline (migrations ausentes) |
| Connection string | `SQLALCHEMY_DATABASE_URI`, `new sqlite3.Database` |

**Descoberta de tabelas:**

- Grep `CREATE TABLE` em `database.py`, `AppManager.js`, migrations.
- Models ORM: `__tablename__`, classes que herdam `db.Model`.
- Seed/init: `INSERT INTO` no bootstrap.

## 5. Domínio da aplicação

Inferir pelo vocabulário de rotas, models e tabelas — sem assumir nome do repo:

| Vocabulário | Domínio provável |
|---|---|
| `produtos`, `pedidos`, `usuarios`, `checkout` | E-commerce / loja |
| `courses`, `enrollments`, `payments`, `checkout` | LMS / cursos online |
| `tasks`, `users`, `categories`, `task_manager` | Task Manager / produtividade |

Ler paths de rota (`/produtos`, `/api/checkout`, `/tasks`) e nomes de tabelas.

## 6. Arquitetura atual

| Padrão observado | Classificação |
|---|---|
| 3–5 arquivos flat (`app.py`, `models.py`, `controllers.py`) | Monolito flat sem MVC |
| Uma classe JS com `setupRoutes` + DB | God class monolítica |
| Pastas `models/`, `routes/`, `services/` sem `controllers/` | Camadas parciais (routes = fat handlers) |
| `config/` ou `settings.py` centralizado | Config já extraída (parcial) |
| Blueprints / `Router()` separados | Views/Routes organizadas |

**Contagem de arquivos fonte:**

- Python: `*.py` exceto `venv`, `__pycache__`, `.git`
- Node: `src/**/*.js` ou raiz `*.js` exceto `node_modules`

## 7. Sinais por tipo de projeto (sem paths fixos)

Use estes padrões genéricos — os três projetos-alvo do monorepo ilustram os extremos:

| Perfil | Sinais típicos | O que esperar na Fase 2 |
|---|---|---|
| E-commerce Flask flat | `models.py` >200 linhas, SQL concat, `add_url_rule` em `app.py` | God module, SQLi, SECRET_KEY hardcoded |
| LMS Express monolito | Classe única com `sqlite3` + rotas inline | God class, callback hell, credenciais em `utils` |
| Task Manager Flask parcial | `routes/*.py` + `models/` + sem `controllers/` | Fat routes, MD5, `to_dict()` com password |

**Mapeamento de relatório (Fase 2):** ao persistir em `reports/audit-project-N.md` na **raiz do monorepo**, usar N=1 para projeto e-commerce Flask flat, N=2 para LMS Express, N=3 para Task Manager Flask com camadas parciais — inferir N pelo domínio/stack detectados, não pelo `cwd`.

## 8. Checklist rápido Fase 1

1. Linguagem e framework identificados com evidência (arquivo:linha).
2. Dependências listadas a partir de manifesto.
3. Domínio inferido de rotas/tabelas.
4. Arquitetura classificada (monolito / parcial / MVC).
5. Contagem de arquivos fonte documentada.
6. Tabelas DB listadas.
7. Saída impressa no formato `PHASE 1: PROJECT ANALYSIS` do SKILL.md.
