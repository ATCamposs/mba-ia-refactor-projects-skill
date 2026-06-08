# Playbook de Refatoração (Fase 3)

Transformações concretas mapeadas ao catálogo de anti-patterns. Cada entrada: pré-condição, passos, verificação pós-transformação. Aplicar de forma **stack-aware** (Python vs Node).

---

## 1. Extrair God module Flask → models + controllers

**Anti-pattern:** [CRITICAL] God Class / God Module

**Pré-condição:** `models.py` concentra CRUD de múltiplos domínios.

**Before (Python):**

```python
# models.py — 300+ linhas
def get_produto_por_id(id):
    cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
    ...

def criar_pedido(...):
    ...
```

**After (Python):**

```python
# models/produto_model.py
def get_by_id(conn, id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
    ...

# controllers/produto_controller.py
def buscar_produto(id):
    produto = produto_model.get_by_id(get_db(), id)
    if not produto:
        return {"erro": "Produto não encontrado", "sucesso": False}, 404
    return {"dados": produto, "sucesso": True}, 200
```

**Passos:** Criar `models/` por domínio; mover funções puras; controllers chamam models; views só delegam.

**Verificação:** `GET /produtos/<id>` retorna mesmo JSON; imports atualizados; boot OK.

---

## 2. Parametrizar queries (anti SQLi)

**Anti-pattern:** [CRITICAL] SQL Injection por concatenação

**Pré-condição:** Grep encontrou `execute(...+ str(` em models — **exceto** endpoint `/admin/query` (contrato intencional).

**Before:**

```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute(
    "INSERT INTO produtos (...) VALUES ('" + nome + "', ...)"
)
```

**After:**

```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute(
    "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
    (nome, descricao, preco, estoque, categoria),
)
```

**Verificação:** CRUD de produtos/usuários funciona; `/admin/query` ainda aceita SQL livre se contrato exige.

---

## 3. Mover SECRET_KEY e credenciais para config/env

**Anti-pattern:** [CRITICAL] Credenciais hardcoded

**Before (Flask):**

```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
```

**After (Flask):**

```python
# config/settings.py
import os
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
DEBUG = os.environ.get("DEBUG", "true").lower() == "true"

# app.py
from config.settings import SECRET_KEY, DEBUG
app.config["SECRET_KEY"] = SECRET_KEY
```

**Before (Express):**

```javascript
const config = { dbPass: "senha_super_secreta_prod_123", paymentGatewayKey: "pk_live_..." };
```

**After (Express):**

```javascript
// config/settings.js
module.exports = {
  dbPass: process.env.DB_PASS || 'dev-pass',
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || 'pk_test_dev',
};
```

**Verificação:** App inicia; health/login OK; nenhum literal de produção no composition root.

---

## 4. Extrair middleware de erro centralizado

**Anti-pattern:** [MEDIUM] Bare except / erro engolido

**Before (Flask):**

```python
@task_bp.route('/tasks')
def get_tasks():
    try:
        ...
    except:
        return jsonify({'error': 'Erro interno'}), 500
```

**After (Flask):**

```python
# middlewares/error_handler.py — register on app
# controllers/task_controller.py
def list_tasks():
    tasks = task_model.list_all()  # exceções propagam
    return jsonify(tasks), 200
```

**Before (Express):**

```javascript
app.post('/api/checkout', (req, res) => {
  db.get("...", (err, row) => {
    if (err) return res.status(500).send("Erro DB");
    ...
  });
});
```

**After (Express):**

```javascript
// middlewares/error_handler.js
app.use((err, req, res, next) => {
  res.status(500).json({ error: err.message });
});
```

**Verificação:** Erro simulado retorna JSON consistente; stack logado no servidor.

---

## 5. Fat route → controller (Flask parcial)

**Anti-pattern:** [HIGH] Fat routes

**Before:**

```python
@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    result = []
    for t in tasks:
        task_data = {}
        task_data['id'] = t.id
        ...
        user = User.query.get(t.user_id)
```

**After:**

```python
# views/task_routes.py
@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    return task_controller.list_tasks()

# controllers/task_controller.py
def list_tasks():
    return jsonify(task_service.list_with_relations()), 200
```

**Verificação:** `GET /tasks` shape idêntico; N+1 reduzido se service usa joinedload.

---

## 6. Quebrar God class Express

**Anti-pattern:** [CRITICAL] God Class

**Before:**

```javascript
class AppManager {
  initDb() { ... }
  setupRoutes(app) {
    app.post('/api/checkout', (req, res) => { /* 50 linhas */ });
  }
}
```

**After:**

```javascript
// models/db.js — init schema
// controllers/checkout_controller.js
async function checkout(req, res, next) { ... }

// views/checkout_routes.js
router.post('/api/checkout', checkoutController.checkout);

// app.js
const app = express();
app.use('/api', checkoutRoutes);
initDb();
```

**Verificação:** `POST /api/checkout` mesmo body/response; `startsWith("4")` preservado.

---

## 7. Callback hell → async/await

**Anti-pattern:** [MEDIUM] Callback hell

**Before:**

```javascript
this.db.get("SELECT ...", [cid], (err, course) => {
  this.db.get("SELECT ...", [e], (err, user) => {
    this.db.run("INSERT ...", function(err) {
      ...
    });
  });
});
```

**After:**

```javascript
const course = await dbGet("SELECT * FROM courses WHERE id = ? AND active = 1", [cid]);
const user = await dbGet("SELECT id FROM users WHERE email = ?", [e]);
const enrollmentId = await dbRun("INSERT INTO enrollments ...", [userId, cid]);
```

**Passos:** Promisify sqlite3 ou usar wrapper; manter ordem transacional.

**Verificação:** Checkout happy path e recusa de cartão não-4xx mantêm status codes.

---

## 8. Remover segredos de responses (seletivo)

**Anti-pattern:** [HIGH] Vazamento de segredos em responses

**Before:**

```python
return jsonify({
    "status": "ok",
    "secret_key": "minha-chave-super-secreta-123",
    "debug": True,
}), 200
```

**After (quando smoke NÃO exige o campo):**

```python
return jsonify({
    "status": "ok",
    "database": "connected",
    "counts": {...},
}), 200
```

**Contrato task-manager — NÃO remover `password` de `to_dict()`** se login/detalhe de usuário retornam hash para smoke:

```python
# Preservar onde api.http exige:
# GET /users/<id> → inclui password
# POST /login → user.password no payload
```

**Verificação:** Comparar resposta com `api.http`; health sem secret se AC permite; login ainda retorna password onde exigido.

---

## 9. Extrair validação duplicada (DRY)

**Anti-pattern:** [LOW] Duplicação de validação

**Before:**

```python
def criar_produto():
    if "nome" not in dados: ...
    if len(nome) < 2: ...
def atualizar_produto():
    if "nome" not in dados: ...  # duplicado
```

**After:**

```python
# validators/produto_validator.py
def validate_produto_fields(dados, partial=False):
    ...

def criar_produto():
    err = validate_produto_fields(dados)
    if err:
        return jsonify(err), 400
```

**Verificação:** Mesmos 400 nos casos inválidos de POST e PUT.

---

## 10. Substituir estado global DB por factory

**Anti-pattern:** [HIGH] Estado global mutável

**Before:**

```python
db_connection = None
def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect(...)
```

**After:**

```python
# database.py
def create_connection():
    return sqlite3.connect("loja.db", check_same_thread=False)

def get_db():
    if 'db' not in g:
        g.db = create_connection()
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db:
        db.close()
```

**Verificação:** Requests concorrentes em dev; sem variável módulo `db_connection`.

---

## Ciclo de validação (2–4 iterações)

Após cada lote de transformações:

1. **Boot:** `python app.py` (Flask) ou `npm start` (Express) — zero traceback.
2. **Smoke:** health, listagem principal, create/read, login ou checkout conforme domínio.
3. Se falhar: reverter último lote, ajustar playbook, repetir.
4. Imprimir estrutura final e checklist no formato `PHASE 3: REFACTORING COMPLETE`.

**Formato de saída obrigatório:**

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ API contracts preserved (urls, methods, response shapes)
  ✓ Zero unresolved CRITICAL anti-patterns (or documented intentional)
================================
```
