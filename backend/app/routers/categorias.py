"""Router de categorías — CRUD para admin."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Categoria, Usuario
from app.schemas import CategoriaCreate, CategoriaOut
from app.auth import require_admin

router = APIRouter(prefix="/categorias", tags=["Categorías"])


@router.get("/", response_model=List[CategoriaOut])
async def listar_categorias(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Categoria).where(Categoria.activa == True))
    return result.scalars().all()


@router.post("/", response_model=CategoriaOut, status_code=status.HTTP_201_CREATED)
async def crear_categoria(
    data: CategoriaCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    existing = await db.execute(select(Categoria).where(Categoria.slug == data.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El slug ya existe")

    categoria = Categoria(**data.model_dump())
    db.add(categoria)
    await db.flush()
    await db.refresh(categoria)
    return categoria


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_categoria(
    categoria_id: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    result = await db.execute(select(Categoria).where(Categoria.id == categoria_id))
    categoria = result.scalar_one_or_none()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    categoria.activa = False
