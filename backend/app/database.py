"""
database.py — Configuración del motor async de SQLAlchemy.

Crea el engine y la fábrica de sesiones. Expone `get_db` como dependencia
de FastAPI para inyectar una sesión por request con commit/rollback automático.

Compatibilidad:
    - SQLite (desarrollo): no soporta pool_size ni max_overflow.
    - PostgreSQL (producción): usa pool con pre-ping y tamaño configurable.
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings

# Detecta si se usa SQLite para ajustar los parámetros del pool
_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Loguea SQL cuando DEBUG=True
    # SQLite requiere check_same_thread=False para uso async
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    # PostgreSQL: pool con pre-ping para detectar conexiones caídas
    **({} if _is_sqlite else {"pool_pre_ping": True, "pool_size": 10, "max_overflow": 20}),
)

# Fábrica de sesiones — expire_on_commit=False evita lazy-load tras commit
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """
    Dependencia de FastAPI que provee una sesión de base de datos por request.

    Hace commit automático al finalizar sin errores.
    Hace rollback automático si ocurre cualquier excepción.
    La sesión se cierra siempre al salir del bloque async with.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
