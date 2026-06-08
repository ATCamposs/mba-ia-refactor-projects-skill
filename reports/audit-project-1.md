================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1 / SQLite
Files:   8 analyzed | ~885 lines of code

## Summary
CRITICAL: 4 | HIGH: 2 | MEDIUM: 3 | LOW: 1

## Findings

### [CRITICAL] SQL Injection por concatenação
File: code-smells-project/models.py:28,47-49,68,92,109-110,127-128,140,155,158-165,174,188,192,220,224,279-280,291-297
Description: O módulo ativo `models.py` monta queries com concatenação de strings — `get_produto_por_id` usa `"WHERE id = " + str(id)`, INSERT/UPDATE interpolam campos de usuário, `login_usuario` concatena email/senha, `buscar_produtos` monta LIKE com termo do cliente, e fluxo de pedidos repete o padrão. Existe `models/produto_model.py` parametrizado, mas não está conectado ao app.
Impact: Execução arbitrária de SQL; exfiltração ou destruição de dados (anti-pattern: SQL Injection por concatenação).
Recommendation: Conectar models MVC por domínio com placeholders `?`; remover ou substituir `models.py` monolítico conforme playbook "Parametrizar queries".

### [CRITICAL] Endpoint de SQL arbitrário
File: code-smells-project/app.py:59-78
Description: Rota `POST /admin/query` aceita campo `sql` no JSON e executa `cursor.execute(query)` sem whitelist nem validação.
Impact: Bypass total da camada de dados; risco CRITICAL mesmo em demo (anti-pattern: Endpoint de SQL arbitrário).
Recommendation: Manter rota como smell intencional de contrato; documentar CRITICAL; parametrizar apenas endpoints de domínio na Fase 3.

### [CRITICAL] Credenciais hardcoded no composition root
File: code-smells-project/app.py:7-8
Description: `SECRET_KEY` e `DEBUG` definidos como literais em `app.config` apesar de `config/settings.py` já expor `SECRET_KEY` via `os.environ.get`. O composition root não importa a config extraída.
Impact: Vazamento via repositório; impossível rotação por ambiente (anti-pattern: Credenciais hardcoded).
Recommendation: Importar `config.settings` no `app.py` e remover literais do composition root conforme playbook.

### [CRITICAL] God module em models.py
File: code-smells-project/models.py:1-315
Description: Arquivo único (~315 LOC) concentra CRUD de produtos, usuários, pedidos, itens, relatórios e busca — quatro domínios sem separação. `models/produto_model.py` é scaffolding órfão.
Impact: Impossível testar em isolamento; mudança local quebra múltiplos fluxos (anti-pattern: God Class / God Module).
Recommendation: Extrair `models/` por domínio e controllers dedicados; composition root só faz wiring (playbook "Extrair God module").

### [HIGH] Vazamento de segredos em responses HTTP
File: code-smells-project/controllers.py:287-289
Description: Endpoint `/health` retorna `secret_key` com valor literal `"minha-chave-super-secreta-123"` no JSON de resposta.
Impact: Endpoint público expõe material sensível a qualquer cliente (anti-pattern: Vazamento de segredos em responses HTTP).
Recommendation: Remover `secret_key` da resposta de health — `api.http` não exige o campo (MVC guidelines permitem remoção).

### [HIGH] Senhas expostas em serializações de API
File: code-smells-project/models.py:83,99
Description: `get_todos_usuarios` e `get_usuario_por_id` incluem campo `senha` no dict retornado, propagado para `GET /usuarios` e `GET /usuarios/<id>`.
Impact: Senhas em plain text vazam em listagens públicas (anti-pattern: Vazamento de segredos em responses HTTP).
Recommendation: Avaliar smoke — README documenta como smell; preservar campo se contrato exigir, senão remover das serializações expostas.

### [MEDIUM] N+1 queries em get_pedidos_usuario
File: code-smells-project/models.py:187-199
Description: Para cada pedido, loop dispara queries separadas em `itens_pedido` e `produtos` (cursor2 + cursor3 por iteração).
Impact: Performance degrada linearmente com número de pedidos/itens (anti-pattern: N+1 queries).
Recommendation: Substituir por JOIN único ou batch fetch de itens e produtos.

### [MEDIUM] N+1 queries em get_todos_pedidos
File: code-smells-project/models.py:219-225
Description: Mesmo padrão N+1 de `get_pedidos_usuario` replicado em listagem global de pedidos.
Impact: Carga desnecessária no DB em relatórios administrativos (anti-pattern: N+1 queries).
Recommendation: Eager load com JOIN entre `pedidos`, `itens_pedido` e `produtos`.

### [MEDIUM] Scaffolding MVC órfão
File: code-smells-project/models/produto_model.py:1-86
Description: Módulo parametrizado e correto existe em `models/`, mas `controllers.py` importa `models` (flat) e ignora o pacote novo. Duas implementações paralelas geram confusão e falsa sensação de correção.
Impact: Refatoração parcial não entrega valor; risco de regressão ao editar arquivo errado.
Recommendation: Completar wiring MVC na Fase 3 — controllers importam `models.produto_model`, demais domínios extraídos do God module.

### [LOW] Duplicação de validação de produto
File: code-smells-project/controllers.py:24-62,64-96
Description: `criar_produto` e `atualizar_produto` repetem blocos idênticos de validação (campos obrigatórios, preço/estoque negativos, tamanho do nome, categorias válidas).
Impact: Violação DRY; divergência futura entre create e update (anti-pattern: Duplicação de validação).
Recommendation: Extrair validador compartilhado reutilizado por ambos handlers.

================================
Total: 10 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
