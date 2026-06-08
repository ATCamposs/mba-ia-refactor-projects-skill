CATEGORIAS_VALIDAS = [
    "informatica", "moveis", "vestuario", "geral", "eletronicos", "livros",
]


def validate_produto_fields(dados):
    """Valida payload de produto para create/update. Retorna dict de erro ou None."""
    if not dados:
        return {"erro": "Dados inválidos"}
    if "nome" not in dados:
        return {"erro": "Nome é obrigatório"}
    if "preco" not in dados:
        return {"erro": "Preço é obrigatório"}
    if "estoque" not in dados:
        return {"erro": "Estoque é obrigatório"}

    nome = dados["nome"]
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", "geral")

    if preco < 0:
        return {"erro": "Preço não pode ser negativo"}
    if estoque < 0:
        return {"erro": "Estoque não pode ser negativo"}
    if len(nome) < 2:
        return {"erro": "Nome muito curto"}
    if len(nome) > 200:
        return {"erro": "Nome muito longo"}
    if categoria not in CATEGORIAS_VALIDAS:
        return {
            "erro": f"Categoria inválida. Válidas: {CATEGORIAS_VALIDAS}",
        }
    return None
