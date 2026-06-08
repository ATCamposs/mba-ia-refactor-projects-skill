# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo.

Exemplos de requisições estão em `api.http`. Se validar também o `task-manager-api` na mesma sessão, teste um Flask por vez — ambos usam a porta **5000**.

## Análise Manual

Problemas identificados por leitura direta do código **antes** da skill `refactor-arch`. Referências apontam ao layout monolítico original (`models.py`, `controllers.py` na raiz).

| # | Severidade | Problema | Local | Justificativa |
|---|------------|----------|-------|---------------|
| 1 | **CRITICAL** | SQL Injection por concatenação | `models.py:28,47-49,110,291` | Queries montadas com `+` e strings interpoladas (`WHERE id = " + str(id)`, `login_usuario`, `buscar_produtos`). Permite execução arbitrária de SQL e viola a camada de dados. |
| 2 | **MEDIUM** | N+1 queries em listagem de pedidos | `models.py:187-199` | Para cada pedido, o código abre cursores extras para `itens_pedido` e `produtos`. Performance degrada linearmente com volume de pedidos. |
| 3 | **MEDIUM** | Credenciais hardcoded | `app.py:7` | `SECRET_KEY` fixa no código (`"minha-chave-super-secreta-123"`). Impossível rotacionar por ambiente e vaza com o repositório. |
| 4 | **LOW** | Duplicação de validação de produto | `controllers.py:24-62` e `64-96` | `criar_produto` e `atualizar_produto` repetem as mesmas regras (campos obrigatórios, preço/estoque, tamanho do nome, categorias). Viola DRY e aumenta risco de divergência. |
| 5 | **LOW** | Magic numbers em regra de desconto | `models.py:257-262` | Faixas de faturamento (`1000`, `5000`, `10000`) e percentuais (`0.02`, `0.05`, `0.1`) soltos em `relatorio_vendas` sem constantes nomeadas. Dificulta manutenção e leitura da regra de negócio. |
