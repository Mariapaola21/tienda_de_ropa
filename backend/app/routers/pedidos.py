"""
routers/pedidos.py — Creación y gestión del flujo de compra.

Rutas protegidas (usuario autenticado):
    POST /api/pedidos/            — Crea un pedido desde el carrito del frontend.
    GET  /api/pedidos/mis-pedidos — Lista los pedidos del usuario autenticado.

Rutas protegidas (solo admin):
    GET   /api/pedidos/              — Lista todos los pedidos del sistema.
    PATCH /api/pedidos/{id}/estado   — Actualiza el estado de un pedido.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Pedido, ItemPedido, Producto, VarianteProducto, Usuario
from app.schemas import PedidoCreate, PedidoOut, PedidoEstadoUpdate
from app.auth import get_current_user, require_admin

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post("/", response_model=PedidoOut, status_code=status.HTTP_201_CREATED)
async def crear_pedido(
    data: PedidoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Convierte el carrito del frontend en un pedido persistido en la BD.

    Para cada item: verifica producto activo, usa precio_oferta si existe,
    y descuenta stock de la variante si aplica.
    Si el flush falla, hace rollback para revertir los descuentos de stock.

    Raises:
        400: Carrito vacío o stock insuficiente.
        404: Producto no encontrado o inactivo.
        500: Error al persistir el pedido.
    """
    if not data.items:
        raise HTTPException(status_code=400, detail="El pedido no puede estar vacío")

    total = 0
    items_db = []

    for item in data.items:
        # Verificar que el producto exista y esté activo
        prod_result = await db.execute(
            select(Producto).where(Producto.id == item.producto_id, Producto.activo == True)
        )
        producto = prod_result.scalar_one_or_none()
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {item.producto_id} no encontrado")

        # Usar precio de oferta si existe, sino precio base
        precio = float(producto.precio_oferta or producto.precio)
        subtotal = precio * item.cantidad

        # Verificar y descontar stock de la variante si aplica
        if item.variante_id:
            var_result = await db.execute(
                select(VarianteProducto).where(VarianteProducto.id == item.variante_id)
            )
            variante = var_result.scalar_one_or_none()
            if not variante or variante.stock < item.cantidad:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para variante {item.variante_id}",
                )
            variante.stock -= item.cantidad  # Descuento en memoria, se persiste en el flush

        items_db.append(ItemPedido(
            producto_id=item.producto_id,
            variante_id=item.variante_id,
            cantidad=item.cantidad,
            precio_unitario=precio,
            subtotal=subtotal,
        ))
        total += subtotal

    pedido = Pedido(
        usuario_id=current_user.id,
        total=total,
        direccion_envio=data.direccion_envio,
        notas=data.notas,
        items=items_db,
    )
    db.add(pedido)

    # Flush con rollback explícito para revertir descuentos de stock si falla
    try:
        await db.flush()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Error al guardar el pedido")

    # Recarga el pedido con sus relaciones para construir la respuesta completa
    result = await db.execute(
        select(Pedido)
        .options(selectinload(Pedido.items), selectinload(Pedido.usuario))
        .where(Pedido.id == pedido.id)
    )
    return result.scalar_one()


@router.get("/mis-pedidos", response_model=List[PedidoOut])
async def mis_pedidos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Retorna los pedidos del usuario autenticado, del más reciente al más antiguo."""
    result = await db.execute(
        select(Pedido)
        .options(selectinload(Pedido.items), selectinload(Pedido.usuario))
        .where(Pedido.usuario_id == current_user.id)
        .order_by(Pedido.fecha_pedido.desc())
    )
    return result.scalars().all()


@router.get("/", response_model=List[PedidoOut])
async def listar_pedidos(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    """Admin: retorna todos los pedidos del sistema ordenados por fecha descendente."""
    result = await db.execute(
        select(Pedido)
        .options(selectinload(Pedido.items), selectinload(Pedido.usuario))
        .order_by(Pedido.fecha_pedido.desc())
    )
    return result.scalars().all()


@router.patch("/{pedido_id}/estado", response_model=PedidoOut)
async def actualizar_estado(
    pedido_id: int,
    data: PedidoEstadoUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    """
    Admin: actualiza el estado de un pedido.
    Ciclo esperado: pendiente → confirmado → enviado → entregado.

    Raises:
        404: Si el pedido no existe.
    """
    result = await db.execute(select(Pedido).where(Pedido.id == pedido_id))
    pedido = result.scalar_one_or_none()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    pedido.estado = data.estado
    await db.flush()
    await db.refresh(pedido)
    return pedido
