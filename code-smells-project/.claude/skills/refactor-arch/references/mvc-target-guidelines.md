# Guidelines — Arquitetura MVC Alvo (Fase 3)

Regras agnósticas para reorganizar APIs Flask e Express preservando **contratos HTTP observáveis** (URLs, métodos, status codes, shapes de JSON documentados em `api.http` ou README do projeto).

## Árvore de diretórios alvo

```
<project-root>/
├── config/
│   ├── settings.py      # Flask: SECRET_KEY, DEBUG via env
│   └── settings.js      # Express: port, keys via process.env
├── models/              # Persistência, entidades, queries parametrizadas
├── views/               # Flask: Blueprints finos | Express: routers finos
│   └── routes.py / routes/*.js
├── controllers/         # Fluxo: validação → model → resposta
├── middlewares/         # Error handler, auth, logging
├── services/            # Opcional: integrações externas (email, payment)
└── app.py / app.js      # Composition root — só wiring, sem regra de negócio
```

## Responsabilidades por camada

| Camada | Responsabilidade | NÃO deve |
|---|---|---|
| **Models** | Schema, queries, serialização de entidade | Conhecer HTTP, `request`, `response` |
| **Views (Routes)** | Mapear path+method → controller; parsing mínimo | Regras de negócio, SQL direto, loops N+1 |
| **Controllers** | Orquestrar validação, chamar model, montar status/body | SQL inline, config hardcoded |
| **Middlewares** | Erros centralizados, CORS, body parser, auth | Lógica de domínio |
| **Config** | Variáveis de ambiente, defaults dev | Segredos literais em produção |
| **Composition root** | Criar app, registrar blueprints/routers, `app.run`/`listen` | Handlers inline de domínio |

## Flask — regras específicas

- **Blueprints** em `views/` — uma linha por rota delegando ao controller.
- **Controllers** retornam `(dict, status)` ou usam `jsonify` via helper; sem `cursor.execute` direto.
- **`app.py`:** `create_app()` factory opcional; registrar blueprints; sem rotas de negócio inline (exceto contratos intencionais — ver abaixo).
- Migrar `add_url_rule` para Blueprints nomeados.

## Express — regras específicas

- **`express.Router()`** por domínio (`checkout`, `admin`, `courses`).
- **Controllers** exportam funções `async (req, res, next)`.
- **Middleware chain:** `express.json()` → routes → error handler de 4 args `(err, req, res, next)`.
- Quebrar God class: `AppManager` vira models + controllers + `setupRoutes` fino.

## Adaptação — projeto com camadas parciais

Quando já existem `routes/`, `models/`, `services/` (ex.: task-manager):

1. **Não destruir** estrutura que funciona — adicionar `controllers/` e afilar `routes/`.
2. Mover lógica de `routes/task_routes.py` para `controllers/task_controller.py`.
3. Manter `services/` para notificações/integrações; remover código morto com segredos ou documentar.
4. `utils/` pode virar `middlewares/` ou helpers puros sem side effects globais.

## Configuração sem hardcode

| Antes | Depois |
|---|---|
| `app.config['SECRET_KEY'] = 'literal'` | `os.environ.get('SECRET_KEY', 'dev-only')` |
| `config.dbPass = "senha..."` | `process.env.DB_PASS` com `.env.example` |

## Error handling centralizado

**Flask:**

```python
# middlewares/error_handler.py
def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_unexpected(e):
        app.logger.exception(e)
        return jsonify({"error": "Erro interno"}), 500
```

**Express:**

```javascript
// middlewares/error_handler.js
function errorHandler(err, req, res, next) {
  console.error(err);
  res.status(err.status || 500).json({ error: err.message || 'Erro interno' });
}
```

## Preservação de endpoints

Antes de refatorar, inventariar rotas existentes (`grep '@app.route'`, `app.get/post`). Após Fase 3, cada rota original deve responder com **mesmo path, método e shape compatível** com smoke tests.

Checklist:

- [ ] URLs inalteradas (incluindo `/admin/query`, `/api/checkout`, `/login`)
- [ ] Status codes preservados (400, 401, 404, 500 nos mesmos casos)
- [ ] Campos JSON esperados por `api.http` / clientes demo mantidos

## Contrato vs smell intencional

Comportamentos que **não podem ser "corrigidos"** na Fase 3 se quebram smoke ou contrato documentado — refatorar estrutura ao redor, não o comportamento observável:

| Comportamento | Projeto típico | Ação permitida |
|---|---|---|
| `/admin/query` executa SQL do body | E-commerce Flask | Manter rota; documentar CRITICAL; não remover nem restringir sem AC |
| Pagamento `cc.startsWith("4")` → PAID | LMS Express | Manter regra na camada de serviço/controller |
| `DELETE FROM users` deixa órfãos | LMS Express | Manter sem FK cascade se resposta atual assume isso |
| MD5 / campo `password` em `to_dict()` | Task Manager | Manter hash MD5 e exposição onde login/detalhe exigem |
| Token `fake-jwt-token-{id}` | Task Manager | Manter formato do token no login |
| `/health` com `secret_key` no body | E-commerce | **Pode** remover se smoke não exige; se `api.http` lista o campo, preservar |
| Senha em listagem de usuários | E-commerce flat | Avaliar smoke — se listagem retorna `senha`, preservar até validar |

Quando preservar smell de contrato, registrar no relatório Fase 2 como CRITICAL/HIGH com nota "intencional — não alterar comportamento na Fase 3".

## Validação pós-MVC

1. Boot: `python app.py` ou `npm start` sem traceback.
2. Smoke: endpoints principais do domínio (CRUD + health + login/checkout).
3. Estrutura impressa no bloco `PHASE 3: REFACTORING COMPLETE`.
