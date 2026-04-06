"""
main.py — Punto de entrada de la API FastAPI
Tienda de Ropa Multimarca | Migrado desde Laravel monolítico
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.models import Base
from app.routers import auth, productos, pedidos, categorias


# ─── Lifespan: crear tablas al iniciar (dev). En prod usar Alembic. ───────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


# ─── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="API REST para tienda de ropa multimarca. Migrada desde Laravel.",
    lifespan=lifespan,
)

# CORS — permite peticiones desde Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Rutas ────────────────────────────────────────────────────────────────────

app.include_router(auth.router,       prefix="/api")
app.include_router(productos.router,  prefix="/api")
app.include_router(pedidos.router,    prefix="/api")
app.include_router(categorias.router, prefix="/api")


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
