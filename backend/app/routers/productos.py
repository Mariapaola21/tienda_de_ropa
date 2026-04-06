"""
routers/productos.py — CRUD completo de productos con variantes y categorías.

Rutas públicas (sin autenticación):
    GET  /api/productos/        — Lista el catálogo con filtros opcionales.
    GET  /api/productos/{id}    — Detalle de un producto con variantes y categorías.

Rutas protegidas (solo admin):
    POST   /api/productos/      — Crea un producto con sus variantes.
    PUT    /api/productos/{id}  — Actualiza campos de un producto.
    DELETE /api/productos/{id}  — Soft delete (activo=False).
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Producto, Categoria, VarianteProducto, Usuario
from app.schemas import ProductoCreate, ProductoUpdate, ProductoOut, ProductoListOut
from app.auth import get_current_user, require_admin

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.get("/", response_model=List[ProductoListOut])
async def listar_productos(
    categoria: Optional[str] = Query(None, description="Slug de la categoría para filtrar"),
    marca: Optional[str] = Query(None, description="Nombre parcial de la marca (búsqueda ILIKE)"),
    destacado: Optional[bool] = Query(None, description="Filtrar solo productos destacados"),
    skip: int = Query(0, description="Offset para paginación"),
    limit: int = Query(20, description="Máximo de resultados por página"),
    db: AsyncSession = Depends(get_db),
):
    """
    Retorna el catálogo de productos activos con filtros opcionales.

    Todos los filtros son acumulables. La búsqueda por marca es case-insensitive.
    Solo retorna productos con activo=True.
    """
    query = select(Producto).where(Producto.activo == True)

    if marca:
        # ILIKE para búsqueda case-insensitive en PostgreSQL y SQLite
        query = query.where(Producto.marca.ilike(f"%{marca}%"))
    if destacado is not None:
        query = query.where(Producto.destacado == destacado)
    if categoria:
        # JOIN con la tabla de categorías para filtrar por slug
        query = query.join(Producto.categorias).where(Categoria.slug == categoria)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{producto_id}", response_model=ProductoOut)
async def obtener_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retorna el detalle completo de un producto incluyendo variantes y categorías.

    Usa selectinload para cargar las relaciones en queries separadas
    y evitar el problema N+1.

    Raises:
        404: Si el producto no existe o está inactivo.
    """
    result = await db.execute(
        select(Producto)
        .options(
            selectinload(Producto.categorias),
            selectinload(Producto.variantes),
        )
        .where(Producto.id == producto_id, Producto.activo == True)
    )
    producto = result.scalar_one_or_none()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.post("/", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
async def crear_producto(
    data: ProductoCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    """
    Crea un nuevo producto con sus variantes y categorías asociadas.

    Las categorías se resuelven por ID antes de crear el producto.
    Las variantes se crean en la misma transacción.

    Raises:
        403: Si el usuario no es administrador.
    """
    # Resolver las categorías por sus IDs
    categorias = []
    if data.categoria_ids:
        result = await db.execute(
            select(Categoria).where(Categoria.id.in_(data.categoria_ids))
        )
        categorias = result.scalars().all()

    producto = Producto(
        nombre=data.nombre,
        descripcion=data.descripcion,
        precio=data.precio,
        precio_oferta=data.precio_oferta,
        marca=data.marca,
        material=data.material,
        genero=data.genero,
        imagen_url=data.imagen_url,
        destacado=data.destacado,
        categorias=categorias,
    )
    db.add(producto)
    await db.flush()  # Obtiene el ID del producto antes de crear variantes

    # Crear cada variante asociada al producto recién creado
    for v in data.variantes:
        variante = VarianteProducto(producto_id=producto.id, **v.model_dump())
        db.add(variante)

    await db.flush()
    await db.refresh(producto)
    return producto


@router.put("/{producto_id}", response_model=ProductoOut)
async def actualizar_producto(
    producto_id: int,
    data: ProductoUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    """
    Actualiza los campos de un producto existente.

    Solo actualiza los campos enviados en el body (exclude_unset=True),
    lo que permite actualizaciones parciales sin sobrescribir campos no enviados.

    Raises:
        404: Si el producto no existe.
        403: Si el usuario no es administrador.
    """
    result = await db.execute(select(Producto).where(Producto.id == producto_id))
    producto = result.scalar_one_or_none()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Aplica solo los campos presentes en el request
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(producto, field, value)

    await db.flush()
    await db.refresh(producto)
    return producto


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_producto(
    producto_id: int,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    """
    Realiza un soft delete del producto (activo=False).

    El producto no se elimina físicamente de la BD para preservar
    el historial de pedidos que lo referencian.

    Raises:
        404: Si el producto no existe.
        403: Si el usuario no es administrador.
    """
    result = await db.execute(select(Producto).where(Producto.id == producto_id))
    producto = result.scalar_one_or_none()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Soft delete — el producto deja de aparecer en el catálogo
    producto.activo = False
    await db.flush()
