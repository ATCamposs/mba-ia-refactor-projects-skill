# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`. Diferente dos outros projetos, este já possui alguma separação de camadas (`models/`, `routes/`, `services/`, `utils/`), mas ainda contém problemas arquiteturais e de qualidade.

## Como rodar

```bash
pip install -r requirements.txt
python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula o banco SQLite (`tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso contrário os endpoints vão retornar listas vazias.

Exemplos de requisições estão em `api.http`. Se validar também o `code-smells-project` na mesma sessão, teste um Flask por vez — ambos usam a porta **5000**.

## Análise Manual

Problemas identificados por leitura direta do código antes da skill `refactor-arch`. O projeto já tem pastas `models/`, `routes/` e `services/`, mas ainda concentra lógica nas rotas e mantém falhas de segurança e performance.

| # | Severidade | Problema | Local | Justificativa |
|---|------------|----------|-------|---------------|
| 1 | **CRITICAL** | Hash de senha com MD5 | `models/user.py:29-32` | `set_password` e `check_password` usam `hashlib.md5` sem salt. Algoritmo obsoleto e vulnerável a rainbow tables — inadequado para credenciais. |
| 2 | **HIGH** | Hash de senha exposto na serialização | `models/user.py:16-25` | `to_dict()` inclui o campo `password` (hash) nas respostas de `GET /users`, `POST /users` e login. Material de autenticação não deve sair da API. |
| 3 | **HIGH** | Rotas “gordas” (lógica fora de controllers) | `routes/task_routes.py:11-59` | `GET /tasks` monta JSON manualmente, calcula `overdue` inline e faz lookup de `User`/`Category` por task — papel de controller/service misturado na camada de rota. |
| 4 | **MEDIUM** | N+1 queries em listagem de tasks | `routes/task_routes.py:41-57` | Para cada task, `User.query.get` e `Category.query.get` disparam queries adicionais. O model já tem `relationship`, mas não há eager load. |
| 5 | **MEDIUM** | `SECRET_KEY` hardcoded | `app.py:13` | Chave secreta fixa (`'super-secret-key-123'`) no código. Mesmo padrão inseguro dos outros projetos; deveria vir de variável de ambiente. |
| 6 | **LOW** | `except` nu sem tipo | `routes/task_routes.py:62,236` | Blocos `except:` genéricos engolem qualquer exceção e retornam erro genérico. Dificulta diagnóstico e pode mascarar bugs reais. |
| 7 | **LOW** | Lógica de overdue duplicada | `routes/task_routes.py:30-39` vs `models/task.py:50-60` | O model define `is_overdue()`, mas as rotas reimplementam o mesmo conjunto de `if` inline em vários handlers. Código morto no model e risco de regras divergentes. |
