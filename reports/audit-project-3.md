================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0
Files:   15 analyzed | ~1158 lines of code

## Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 6 | LOW: 3

## Findings

### [CRITICAL] Credenciais SMTP hardcoded
File: services/notification_service.py:8-10
Description: `NotificationService` define `email_user` e `email_password` como literais string (`taskmanager@gmail.com`, `senha123`) no construtor.
Impact: Vazamento de credenciais via repositório; impossível rotação por ambiente; risco CRITICAL mesmo em demo.
Recommendation: Extrair para `config/` + variáveis de ambiente; nunca commitar senhas SMTP. Serviço não está wired nas rotas — avaliar remoção ou injeção via composition root.

### [CRITICAL] Hash de senha com MD5 (contrato intencional)
File: models/user.py:27-32
Description: `set_password` e `check_password` usam `hashlib.md5` sem salt. Algoritmo obsoleto e vulnerável a rainbow tables.
Impact: Credenciais inadequadas para produção; classificado CRITICAL por severidade de segurança.
Recommendation: Documentar como smell intencional — **preservar MD5 na Fase 3** para compatibilidade com `seed.py` e smoke de login (`joao@email.com` / `1234`). Não migrar para bcrypt sem validar contrato.

### [CRITICAL] SECRET_KEY hardcoded
File: app.py:13
Description: `app.config['SECRET_KEY'] = 'super-secret-key-123'` fixo no código, sem `os.environ` ou `python-dotenv` (presente em `requirements.txt` mas não usado).
Impact: Chave secreta exposta no repositório; sessões/assinaturas previsíveis em qualquer deploy.
Recommendation: Extrair para `config/` com fallback dev documentado via variável de ambiente.

### [HIGH] Hash de senha exposto em serialização (contrato intencional)
File: models/user.py:16-25
Description: `to_dict()` inclui o campo `password` (hash MD5). Usado em `GET /users/<id>`, `POST /users`, `PUT /users/<id>` e `POST /login` via `user_routes.py`.
Impact: Material de autenticação vaza em endpoints públicos; classificado HIGH por exposição de segredo.
Recommendation: Documentar como contrato intencional — **manter `password` em `to_dict()`** onde login/detalhe de usuário exigem (ver `mvc-target-guidelines.md`). Na Fase 3, extrair serialização segura para controllers sem quebrar smoke.

### [HIGH] Rotas gordas — listagem de tasks sem camada controller
File: routes/task_routes.py:11-63
Description: `get_tasks` monta JSON manualmente campo a campo, calcula `overdue` inline, e faz lookup de `User`/`Category` por task — validação, regra de negócio, ORM e serialização na camada de rota.
Impact: Viola MVC; impossível testar regras de overdue/enriquecimento sem HTTP; duplica lógica do model `Task.is_overdue()`.
Recommendation: Extrair `TaskController` + service; rota fina delega. Reutilizar `is_overdue()` do model.

### [HIGH] Ausência de camada `controllers/` — arquitetura MVC incompleta
File: routes/task_routes.py:1-300
Description: Projeto possui `models/`, `routes/`, `services/`, `utils/` mas nenhum `controllers/`. Handlers em `task_routes.py` (300 LOC), `user_routes.py` (212 LOC) e `report_routes.py` (224 LOC) concentram validação, persistência e resposta HTTP.
Impact: Viola separação MVC alvo; rotas são fat handlers; `services/notification_service.py` existe mas não é consumido.
Recommendation: Criar `controllers/` por domínio (task, user, report/category); blueprints/views apenas registram rotas e delegam.

### [MEDIUM] N+1 queries na listagem de tasks
File: routes/task_routes.py:41-57
Description: Loop `for t in tasks` dispara `User.query.get(t.user_id)` e `Category.query.get(t.category_id)` por item, apesar de `Task` ter `relationship` definido.
Impact: Performance degrada linearmente com número de tasks; carga desnecessária no SQLite.
Recommendation: Eager load com `joinedload`/`selectinload` ou JOIN único na query de listagem.

### [MEDIUM] N+1 queries no relatório de produtividade
File: routes/report_routes.py:53-68
Description: Loop `for u in users` executa `Task.query.filter_by(user_id=u.id).all()` por usuário para montar `user_productivity`.
Impact: O(N×M) queries no endpoint `/reports/summary`; degrada com escala.
Recommendation: Query agregada única com `GROUP BY user_id` ou eager load de tasks por usuário.

### [MEDIUM] N+1 queries na listagem de categorias
File: routes/report_routes.py:158-164
Description: Loop `for c in categories` executa `Task.query.filter_by(category_id=c.id).count()` por categoria.
Impact: Uma query adicional por categoria em `GET /categories`.
Recommendation: Subquery agregada ou `func.count` com `GROUP BY category_id`.

### [MEDIUM] Bare except sem tipo
File: routes/task_routes.py:62-63
Description: `get_tasks` usa `except:` genérico retornando `{'error': 'Erro interno'}` sem log nem tipo de exceção.
Impact: Engole qualquer erro (incluindo `KeyboardInterrupt` em edge cases); diagnóstico operacional impossível.
Recommendation: Capturar exceções específicas; middleware de erro centralizado na Fase 3.

### [MEDIUM] Bare except sem tipo (delete task)
File: routes/task_routes.py:236-238
Description: `delete_task` usa `except:` genérico no bloco de commit/rollback.
Impact: Mascara falhas de integridade referencial ou erros de sessão SQLAlchemy.
Recommendation: `except Exception as e` com log; handler centralizado para 500.

### [MEDIUM] Configuração e DB URI hardcoded no composition root
File: app.py:11-13
Description: `SQLALCHEMY_DATABASE_URI` e `SECRET_KEY` definidos inline em `app.py`; `python-dotenv` listado em dependências mas não carregado.
Impact: Configuração não separada por ambiente; dificulta testes e deploy.
Recommendation: Extrair para `config/` (dev/prod) com `load_dotenv()` no boot.

### [LOW] Lógica de overdue duplicada
File: routes/task_routes.py:30-39
Description: Handlers reimplementam conjunto de `if` para `overdue` inline, enquanto `models/task.py:50-60` define `is_overdue()` não utilizado nas rotas.
Impact: Risco de regras divergentes entre endpoints (`get_tasks`, `get_task`, `task_stats`, `get_user_tasks`, `summary_report`).
Recommendation: Centralizar em `Task.is_overdue()` ou método de domínio; controllers chamam uma única fonte.

### [LOW] Validação duplicada — rotas vs helpers
File: routes/task_routes.py:92-114
Description: `create_task` valida título, status e prioridade inline; `utils/helpers.py:57-108` define `process_task_data` com regras equivalentes mas não é usado pelas rotas.
Impact: DRY violado; mudança de regra exige editar múltiplos handlers.
Recommendation: Usar `process_task_data` ou schemas marshmallow (já em `requirements.txt`) nos controllers.

### [LOW] API SQLAlchemy legacy `Model.query.get`
File: routes/user_routes.py:29
Description: Uso de `User.query.get(user_id)` (padrão legado SQLAlchemy 1.x) em múltiplos handlers (`task_routes`, `user_routes`, `report_routes`).
Impact: Deprecation warning em SQLAlchemy 2.x; padrão inconsistente com versões futuras.
Recommendation: Migrar para `db.session.get(User, user_id)` na Fase 3 sem alterar comportamento.

================================
Total: 15 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
