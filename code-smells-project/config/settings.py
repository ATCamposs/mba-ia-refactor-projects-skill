import os

SECRET_KEY = os.environ.get("SECRET_KEY", "minha-chave-super-secreta-123")
DEBUG = os.environ.get("DEBUG", "true").lower() == "true"
DB_PATH = os.environ.get("DB_PATH", "loja.db")
