# Catálogo de Anti-Patterns (Fase 2)

Cada entrada tem sinais de detecção acionáveis, severidade default e recomendação. Cruzar **todo** arquivo fonte do projeto contra estas regras. Severidades seguem o README raiz: CRITICAL (segurança/arquitetura grave), HIGH (MVC/SOLID forte), MEDIUM (padronização/performance moderada), LOW (legibilidade).

---

## [CRITICAL] SQL Injection por concatenação

**Severidade:** CRITICAL

**Sinais de detecção:**
- Grep: `execute\([^)]*\+`, `execute\([^)]*f"`, `execute\([^)]*' \+`
- SQL montado com `str(id)`, concatenação de literais de usuário em INSERT/UPDATE/SELECT
- Ausência de placeholders `?` ou parâmetros nomeados

**Impacto:** Execução arbitrária de SQL; exfiltração ou destruição de dados.

**Recomendação:** Parametrizar queries (`cursor.execute("... WHERE id = ?", (id,))`). Ver playbook "Parametrizar queries".

**Verificado em:** monolitos Flask com `models.py` único (e-commerce flat).

---

## [CRITICAL] Endpoint de SQL arbitrário

**Severidade:** CRITICAL

**Sinais de detecção:**
- Rota `/admin/query` ou similar aceitando `sql`/`query` no body
- `cursor.execute(query)` onde `query` vem de `request.get_json()` sem whitelist

**Impacto:** Bypass total da camada de dados; risco CRITICAL mesmo em demo.

**Recomendação:** **Não remover** se faz parte do contrato de smoke — documentar como "smell intencional" e parametrizar apenas endpoints de domínio. Não "corrigir" fechando o endpoint sem validar `api.http`/README.

**Verificado em:** Flask com rota admin de query livre.

---

## [CRITICAL] Credenciais hardcoded

**Severidade:** CRITICAL

**Sinais de detecção:**
- Grep: `SECRET_KEY`, `password`, `api[_-]?key`, `pk_live`, `dbPass`, `smtp` com literais string
- `app.config["SECRET_KEY"] = "..."` sem `os.environ`
- Objeto `config` em JS com senhas/chaves em plain text

**Impacto:** Vazamento via repositório; impossível rotação por ambiente.

**Recomendação:** Extrair para `config/` + variáveis de ambiente com fallback dev documentado.

**Verificado em:** `app.py` (Flask), `utils.js` (Express).

---

## [CRITICAL] God Class / God Module

**Severidade:** CRITICAL

**Sinais de detecção:**
- Um arquivo >250 LOC combinando: schema DB + rotas HTTP + regras de negócio
- Classe única com `setupRoutes`, `initDb`, processamento de pagamento
- `models.py` com CRUD de 4+ domínios sem separação

**Impacto:** Impossível testar em isolamento; mudança local quebra tudo.

**Recomendação:** Separar models, controllers, views/routes por domínio (playbook "Extrair God module").

**Verificado em:** `models.py` monolítico, `AppManager.js`.

---

## [HIGH] Vazamento de segredos em responses HTTP

**Severidade:** HIGH

**Sinais de detecção:**
- Health check ou listagens retornando `secret_key`, `password`, `pass`, hash de senha
- `jsonify({..., "secret_key": app.config[...]})`
- `to_dict()` incluindo campo `password`

**Impacto:** Endpoint público expõe material sensível.

**Recomendação:** Remover de responses **exceto** onde smoke/`api.http` exige o campo (ex.: `password` em detalhe de usuário/login no task-manager — ver MVC guidelines "Contrato vs smell").

**Verificado em:** `/health` com secret, `User.to_dict()`.

---

## [HIGH] Estado global mutável

**Severidade:** HIGH

**Sinais de detecção:**
- Variável módulo-nível `db_connection`, `globalCache`, `totalRevenue` mutados em runtime
- Singleton de conexão sem factory/DI

**Impacto:** Acoplamento; testes flaky; concorrência imprevisível.

**Recomendação:** Encapsular em factory/app context; injetar dependência no composition root.

**Verificado em:** `database.py` global, `utils.js` `globalCache`.

---

## [HIGH] Fat routes / lógica pesada em handlers HTTP

**Severidade:** HIGH

**Sinais de detecção:**
- Funções de rota >80 LOC com validação + ORM + serialização + regra de negócio
- `Blueprint` handlers sem camada `controllers/`
- Express route callback com múltiplos `db.run` aninhados

**Impacto:** Viola MVC; difícil testar regras sem HTTP.

**Recomendação:** Extrair controllers; rotas só delegam (playbook "Fat route → controller").

**Verificado em:** `routes/task_routes.py`, checkout inline em `AppManager`.

---

## [MEDIUM] N+1 queries

**Severidade:** MEDIUM

**Sinais de detecção:**
- Loop `for` com `query.get` / `cursor.execute` / `db.all` dentro
- Relatório que itera coleção e dispara query por item

**Impacto:** Performance degrada linearmente; carga desnecessária no DB.

**Recomendação:** Eager load, JOIN, ou query agregada única.

**Verificado em:** `get_pedidos_usuario`, relatório financeiro Express.

---

## [MEDIUM] Callback hell (Node)

**Severidade:** MEDIUM

**Sinais de detecção:**
- 3+ níveis de `db.get`/`db.run` aninhados
- Grep: `function(err` dentro de `function(err` dentro de callback

**Impacto:** Fluxo ilegível; erro handling inconsistente.

**Recomendação:** Promises/async-await ou extrair funções nomeadas por etapa.

**Verificado em:** checkout e financial-report em Express.

---

## [MEDIUM] Bare except / erro engolido

**Severidade:** MEDIUM

**Sinais de detecção:**
- `except:` sem tipo
- `catch (e) {}` vazio ou retorno 500 genérico sem log

**Impacto:** Diagnóstico operacional impossível.

**Recomendação:** Capturar exceções específicas; middleware de erro centralizado.

**Verificado em:** `routes/task_routes.py`.

---

## [LOW] Duplicação de validação

**Severidade:** LOW

**Sinais de detecção:**
- Mesmos `if not dados` / limites de tamanho copiados em create vs update
- Validação de categoria/status repetida em múltiplos handlers

**Impacto:** DRY violado; divergência futura entre endpoints.

**Recomendação:** Extrair validadores compartilhados ou schema (marshmallow/zod).

**Verificado em:** `controllers.py` criar/atualizar produto.

---

## [LOW] Nomenclatura críptica / magic values

**Severidade:** LOW

**Sinais de detecção:**
- Variáveis de 1 letra (`u`, `e`, `cc`) em fluxo crítico
- Números mágicos sem constante nomeada

**Impacto:** Legibilidade e revisão prejudicadas.

**Recomendação:** Renomear para nomes de domínio; extrair constantes.

**Verificado em:** checkout Express.

---

## APIs deprecated

Identificar uso de APIs obsoletas e recomendar equivalente moderno. Reportar como finding MEDIUM ou LOW conforme exposição.

| Stack | Sinal deprecated | Moderno recomendado |
|---|---|---|
| Flask | `from flask import Markup` (removido Flask 3) | `markupsafe.Markup` |
| Flask | `request.json` sem guard (`if request.json is None`) | `request.get_json(silent=True)` + validação 400 |
| Flask | `User.query.get(id)` (SQLAlchemy 2.0 legacy) | `db.session.get(User, id)` |
| Python | `hashlib.md5` para senha | `bcrypt` ou `argon2` — **exceto** se smoke exige MD5 no task-manager |
| Node | Callbacks profundos sem `util.promisify` | `async/await` + `sqlite` promisified |
| Node | `md5`/hash custom (`badCrypto`) para senha | `bcrypt.hash` / `scrypt` |
| Node | `body` parse manual sem `express.json()` | Middleware `express.json()` centralizado |

**Sinais grep:**
- `hashlib.md5`, `Markup`, `request\.json[^a-z]`
- `badCrypto`, funções hash DIY com loops + `base64`

**Exemplo finding:**

```markdown
### [MEDIUM] MD5 para hash de senha (API deprecated)
File: models/user.py:29
Description: set_password usa hashlib.md5 — algoritmo obsoleto.
Impact: Rainbow tables; não atende requisitos mínimos de segurança.
Recommendation: Migrar para bcrypt em código novo; preservar MD5 apenas se contrato de login/smoke exigir compatibilidade (documentar em MVC guidelines).
```

---

## Calibração esperada

Aplicando este catálogo nos três projetos do monorepo, espera-se **≥5 findings** por projeto, incluindo ≥1 CRITICAL ou HIGH, alinhados à Análise Manual do README raiz.
