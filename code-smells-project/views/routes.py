from flask import Blueprint, jsonify

from controllers import (
    admin_controller,
    health_controller,
    pedido_controller,
    produto_controller,
    usuario_controller,
)

produto_bp = Blueprint("produtos", __name__)
usuario_bp = Blueprint("usuarios", __name__)
pedido_bp = Blueprint("pedidos", __name__)
relatorio_bp = Blueprint("relatorios", __name__)
admin_bp = Blueprint("admin", __name__)

# Produtos
produto_bp.add_url_rule("", "listar", produto_controller.listar_produtos, methods=["GET"])
produto_bp.add_url_rule(
    "/busca", "buscar", produto_controller.buscar_produtos, methods=["GET"],
)
produto_bp.add_url_rule(
    "/<int:produto_id>", "buscar_por_id", produto_controller.buscar_produto, methods=["GET"],
)
produto_bp.add_url_rule("", "criar", produto_controller.criar_produto, methods=["POST"])
produto_bp.add_url_rule(
    "/<int:produto_id>", "atualizar", produto_controller.atualizar_produto, methods=["PUT"],
)
produto_bp.add_url_rule(
    "/<int:produto_id>", "deletar", produto_controller.deletar_produto, methods=["DELETE"],
)

# Usuários e login
usuario_bp.add_url_rule("", "listar", usuario_controller.listar_usuarios, methods=["GET"])
usuario_bp.add_url_rule(
    "/<int:usuario_id>", "buscar", usuario_controller.buscar_usuario, methods=["GET"],
)
usuario_bp.add_url_rule("", "criar", usuario_controller.criar_usuario, methods=["POST"])

login_bp = Blueprint("login", __name__)
login_bp.add_url_rule("", "login", usuario_controller.login, methods=["POST"])

# Pedidos
pedido_bp.add_url_rule("", "criar", pedido_controller.criar_pedido, methods=["POST"])
pedido_bp.add_url_rule(
    "", "listar_todos", pedido_controller.listar_todos_pedidos, methods=["GET"],
)
pedido_bp.add_url_rule(
    "/usuario/<int:usuario_id>",
    "listar_por_usuario",
    pedido_controller.listar_pedidos_usuario,
    methods=["GET"],
)
pedido_bp.add_url_rule(
    "/<int:pedido_id>/status",
    "atualizar_status",
    pedido_controller.atualizar_status_pedido,
    methods=["PUT"],
)

# Relatórios
relatorio_bp.add_url_rule(
    "/vendas", "vendas", pedido_controller.relatorio_vendas, methods=["GET"],
)

# Admin (smells intencionais de contrato)
admin_bp.add_url_rule(
    "/reset-db", "reset_db", admin_controller.reset_database, methods=["POST"],
)
admin_bp.add_url_rule(
    "/query", "query", admin_controller.executar_query, methods=["POST"],
)

# Health
health_bp = Blueprint("health", __name__)
health_bp.add_url_rule("", "check", health_controller.health_check, methods=["GET"])


def register_blueprints(app):
    app.register_blueprint(produto_bp, url_prefix="/produtos")
    app.register_blueprint(usuario_bp, url_prefix="/usuarios")
    app.register_blueprint(login_bp, url_prefix="/login")
    app.register_blueprint(pedido_bp, url_prefix="/pedidos")
    app.register_blueprint(relatorio_bp, url_prefix="/relatorios")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(health_bp, url_prefix="/health")


def register_index(app):
    @app.route("/")
    def index():
        return jsonify({
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "1.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        })
