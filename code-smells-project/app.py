from flask import Flask
from flask_cors import CORS

from config.settings import DEBUG, SECRET_KEY
from database import close_db, init_db
from middlewares.error_handler import register_error_handlers
from views.routes import register_blueprints, register_index


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["DEBUG"] = DEBUG
    CORS(app)

    register_blueprints(app)
    register_index(app)
    register_error_handlers(app)

    app.teardown_appcontext(close_db)

    return app


app = create_app()

if __name__ == "__main__":
    init_db()
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print("Rodando em http://localhost:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=DEBUG)
