"""
config.py — Configuración centralizada de la aplicación.

Carga todas las variables de entorno desde el archivo .env usando pydantic-settings.
Si una variable no está definida en .env, se usa el valor por defecto indicado aquí.

Variables disponibles:
    DATABASE_URL: URL de conexión a la base de datos (SQLite por defecto en dev).
    SECRET_KEY:   Clave secreta para firmar los tokens JWT.
    ALGORITHM:    Algoritmo de firma JWT (HS256).
    ACCESS_TOKEN_EXPIRE_MINUTES: Duración del token en minutos (24h por defecto).
    APP_NAME:     Nombre de la aplicación mostrado en la documentación de la API.
    DEBUG:        Activa el logging SQL de SQLAlchemy cuando es True.
    ALLOWED_ORIGINS: Lista de orígenes permitidos por CORS (Angular dev en localhost:4200).
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Base de datos — SQLite async (dev). Cambia a postgresql+asyncpg://... en producción.
    DATABASE_URL: str = "sqlite+aiosqlite:///./tienda_ropa.db"

    # JWT — clave secreta y algoritmo de firma
    SECRET_KEY: str = "cambia-esto-en-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas

    # App
    APP_NAME: str = "Tienda Ropa API"
    DEBUG: bool = False
    # Orígenes permitidos por CORS — agrega el dominio de producción aquí
    ALLOWED_ORIGINS: list[str] = ["http://localhost:4200"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# Instancia global importada por el resto de módulos
settings = Settings()
