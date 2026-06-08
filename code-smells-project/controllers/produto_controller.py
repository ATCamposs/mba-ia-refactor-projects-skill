from flask import request, jsonify

from models import produto_model
from validators.produto_validator import validate_produto_fields


def listar_produtos():
    produtos = produto_model.get_todos()
    print(f"Listando {len(produtos)} produtos")
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar_produto(produto_id):
    produto = produto_model.get_by_id(produto_id)
    if produto:
        return jsonify({"dados": produto, "sucesso": True}), 200
    return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404


def criar_produto():
    dados = request.get_json()
    erro = validate_produto_fields(dados)
    if erro:
        return jsonify(erro), 400

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", "geral")

    novo_id = produto_model.criar(nome, descricao, preco, estoque, categoria)
    print(f"Produto criado com ID: {novo_id}")
    return jsonify({
        "dados": {"id": novo_id},
        "sucesso": True,
        "mensagem": "Produto criado",
    }), 201


def atualizar_produto(produto_id):
    dados = request.get_json()

    if not produto_model.get_by_id(produto_id):
        return jsonify({"erro": "Produto não encontrado"}), 404

    erro = validate_produto_fields(dados)
    if erro:
        return jsonify(erro), 400

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", "geral")

    produto_model.atualizar(produto_id, nome, descricao, preco, estoque, categoria)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar_produto(produto_id):
    if not produto_model.get_by_id(produto_id):
        return jsonify({"erro": "Produto não encontrado"}), 404

    produto_model.deletar(produto_id)
    print(f"Produto {produto_id} deletado")
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    preco_min = request.args.get("preco_min", None)
    preco_max = request.args.get("preco_max", None)

    if preco_min:
        preco_min = float(preco_min)
    if preco_max:
        preco_max = float(preco_max)

    resultados = produto_model.buscar(termo, categoria, preco_min, preco_max)
    return jsonify({
        "dados": resultados,
        "total": len(resultados),
        "sucesso": True,
    }), 200
