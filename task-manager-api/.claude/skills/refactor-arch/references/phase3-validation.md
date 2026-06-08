# Validação Fase 3 — Boot, portas e smoke

Playbook complementar para validar boot e endpoints após refatoração MVC. Não substitui `mvc-target-guidelines.md` nem `refactoring-playbook.md` — cobre **como executar** os smokes documentados nos `api.http` de cada projeto.

## Matriz dos 3 projetos

| Projeto | Stack | Boot | Porta | Pré-requisito extra |
|---------|-------|------|-------|---------------------|
| `code-smells-project` | Flask | `pip install -r requirements.txt && python app.py` | **5000** | SQLite seed automático no primeiro boot (`database.py`) |
| `task-manager-api` | Flask | `pip install -r requirements.txt && python app.py` | **5000** | **`python seed.py` antes do primeiro boot** (usuários, categorias, tasks) |
| `ecommerce-api-legacy` | Express | `npm install && npm start` | **3000** | Seed em memória no boot |

### Conflito de porta 5000

`code-smells-project` e `task-manager-api` usam a mesma porta **5000**. Na mesma sessão de validação, suba **apenas um Flask por vez** — pare o processo anterior (`Ctrl+C`) antes de iniciar o outro.

### Ordem recomendada (task-manager)

1. `pip install -r requirements.txt`
2. `python seed.py` (obrigatório na primeira execução ou após apagar `tasks.db`)
3. `python app.py`
4. Smoke via `api.http` (REST Client) ou curls abaixo

## Smoke — code-smells-project (`api.http`)

Arquivo: `code-smells-project/api.http` · `@baseUrl = http://localhost:5000`

| Request | curl one-liner |
|---------|----------------|
| Health check | `curl -sS http://localhost:5000/health` |
| Listar produtos | `curl -sS http://localhost:5000/produtos` |
| Login | `curl -sS -X POST http://localhost:5000/login -H 'Content-Type: application/json' -d '{"email":"joao@email.com","senha":"123456"}'` |
| Criar pedido | `curl -sS -X POST http://localhost:5000/pedidos -H 'Content-Type: application/json' -d '{"usuario_id":2,"itens":[{"produto_id":1,"quantidade":1}]}'` |
| Relatório de vendas | `curl -sS http://localhost:5000/relatorios/vendas` |

Credenciais e IDs vêm do seed em `database.py` (usuário João `id=2`, produtos `id=1+`).

## Smoke — task-manager-api (`api.http`)

Arquivo: `task-manager-api/api.http` · `@baseUrl = http://localhost:5000`

| Request | curl one-liner |
|---------|----------------|
| Health check | `curl -sS http://localhost:5000/health` |
| Raiz | `curl -sS http://localhost:5000/` |
| Listar tasks | `curl -sS http://localhost:5000/tasks` |
| Task por ID | `curl -sS http://localhost:5000/tasks/1` |
| Login | `curl -sS -X POST http://localhost:5000/login -H 'Content-Type: application/json' -d '{"email":"joao@email.com","password":"1234"}'` |
| Stats tasks | `curl -sS http://localhost:5000/tasks/stats` |
| Listar usuários | `curl -sS http://localhost:5000/users` |
| Relatório resumo | `curl -sS http://localhost:5000/reports/summary` |
| Categorias | `curl -sS http://localhost:5000/categories` |

Sem `python seed.py`, listas retornam vazias e `GET /tasks/1` pode responder **404**.

## Smoke — ecommerce-api-legacy (`api.http`)

Arquivo: `ecommerce-api-legacy/api.http` · `@baseUrl = http://localhost:3000`

| Request | curl one-liner |
|---------|----------------|
| Checkout sucesso | `curl -sS -X POST http://localhost:3000/api/checkout -H 'Content-Type: application/json' -d '{"usr":"Guilherme","eml":"gui@fullcycle.com.br","pwd":"senhaforte","c_id":2,"card":"4111222233334444"}'` |
| Checkout recusado | `curl -sS -X POST http://localhost:3000/api/checkout -H 'Content-Type: application/json' -d '{"usr":"João","eml":"joao@teste.com","pwd":"123","c_id":1,"card":"5111222233334444"}'` |
| Relatório financeiro | `curl -sS http://localhost:3000/api/admin/financial-report` |
| Deletar usuário | `curl -sS -X DELETE http://localhost:3000/api/users/1` |

## Checklist pós-refatoração

Use após cada ciclo de Fase 3:

- [ ] Servidor sobe **sem traceback** no terminal (`python app.py` ou `npm start`).
- [ ] Cada request do `api.http` do projeto retorna **2xx** (ou **401** esperado em login com credenciais inválidas, quando testado ad hoc).
- [ ] **URLs e métodos HTTP** idênticos ao contrato pré-refatoração (`app.py` / routes / `api.http`).
- [ ] Shapes de JSON principais preservados (campos documentados em smoke/README).
- [ ] Para task-manager: `seed.py` executado antes do boot quando o banco está vazio.
- [ ] Ao validar os dois Flask na mesma máquina: apenas um processo na porta **5000** por vez.

Quando todos os itens passarem, imprimir o bloco `PHASE 3: REFACTORING COMPLETE` definido em `SKILL.md`.
