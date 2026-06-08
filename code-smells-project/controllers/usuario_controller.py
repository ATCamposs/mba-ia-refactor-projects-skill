from flask import request, jsonify

from models import usuario_model


def listar_usuarios():
    usuarios = usuario_model.get_todos()
    return jsonify({"dados": usuarios, "sucesso": True}), 200


def buscar_usuario(usuario_id):
    usuario = usuario_model.get_by_id(usuario_id)
    if usuario:
        return jsonify({"dados": usuario, "sucesso": True}), 200
    return jsonify({"erro": "Usuário não encontrado"}), 404


def criar_usuario():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400

    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not nome or not email or not senha:
        return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400

    novo_id = usuario_model.criar(nome, email, senha)
    print(f"Usuário criado: {email}")
    return jsonify({"dados": {"id": novo_id}, "sucesso": True}), 201


def login():
    dados = request.get_json()
    email = dados.get("email", "") if dados else ""
    senha = dados.get("senha", "") if dados else ""

    if not email or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400

    usuario = usuario_model.login(email, senha)
    if usuario:
        print(f"Login bem-sucedido: {email}")
        return jsonify({
            "dados": usuario,
            "sucesso": True,
            "mensagem": "Login OK",
        }), 200

    print(f"Login falhou: {email}")
    return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401
