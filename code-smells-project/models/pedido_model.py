from database import get_db


def _pedidos_com_itens(rows):
    """Agrupa linhas de JOIN em lista de pedidos com itens aninhados."""
    pedidos_map = {}
    for row in rows:
        pedido_id = row["pedido_id"]
        if pedido_id not in pedidos_map:
            pedidos_map[pedido_id] = {
                "id": pedido_id,
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
        if row["item_id"] is not None:
            pedidos_map[pedido_id]["itens"].append({
                "produto_id": row["produto_id"],
                "produto_nome": row["produto_nome"] or "Desconhecido",
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })
    return list(pedidos_map.values())


_PEDIDOS_JOIN = """
    SELECT
        p.id AS pedido_id,
        p.usuario_id,
        p.status,
        p.total,
        p.criado_em,
        ip.id AS item_id,
        ip.produto_id,
        ip.quantidade,
        ip.preco_unitario,
        pr.nome AS produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = ip.produto_id
"""


def get_by_usuario(usuario_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        _PEDIDOS_JOIN + " WHERE p.usuario_id = ? ORDER BY p.id, ip.id",
        (usuario_id,),
    )
    return _pedidos_com_itens(cursor.fetchall())


def get_todos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(_PEDIDOS_JOIN + " ORDER BY p.id, ip.id")
    return _pedidos_com_itens(cursor.fetchall())


def criar(usuario_id, itens):
    db = get_db()
    cursor = db.cursor()
    total = 0

    for item in itens:
        cursor.execute(
            "SELECT * FROM produtos WHERE id = ?",
            (item["produto_id"],),
        )
        produto = cursor.fetchone()
        if produto is None:
            return {"erro": f"Produto {item['produto_id']} não encontrado"}
        if produto["estoque"] < item["quantidade"]:
            return {"erro": f"Estoque insuficiente para {produto['nome']}"}
        total += produto["preco"] * item["quantidade"]

    cursor.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
        (usuario_id, total),
    )
    pedido_id = cursor.lastrowid

    for item in itens:
        cursor.execute(
            "SELECT preco FROM produtos WHERE id = ?",
            (item["produto_id"],),
        )
        produto = cursor.fetchone()
        cursor.execute(
            """INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
               VALUES (?, ?, ?, ?)""",
            (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
        )
        cursor.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (item["quantidade"], item["produto_id"]),
        )

    db.commit()
    return {"pedido_id": pedido_id, "total": total}


def atualizar_status(pedido_id, novo_status):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE pedidos SET status = ? WHERE id = ?",
        (novo_status, pedido_id),
    )
    db.commit()
    return True


def relatorio_vendas():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM pedidos")
    total_pedidos = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total) FROM pedidos")
    faturamento = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'")
    pendentes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'")
    aprovados = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'")
    cancelados = cursor.fetchone()[0]

    desconto = 0
    if faturamento > 10000:
        desconto = faturamento * 0.1
    elif faturamento > 5000:
        desconto = faturamento * 0.05
    elif faturamento > 1000:
        desconto = faturamento * 0.02

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": pendentes,
        "pedidos_aprovados": aprovados,
        "pedidos_cancelados": cancelados,
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
