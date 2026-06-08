from flask import jsonify


def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_unexpected(error):
        app.logger.exception(error)
        return jsonify({"erro": str(error)}), 500
