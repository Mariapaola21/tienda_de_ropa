"""
models.py — Modelos ORM de SQLAlchemy para la tienda de ropa multimarca.

Define todas las tablas de la base de datos usando el patrón DeclarativeBase.
Migrado y extendido desde el sistema Laravel original (disfraces → ropa).

Modelos:
    Usuario         — Clientes y administradores del sistema.
    Categoria       — Categorías de productos (Camisas, Pantalones, etc.).
    Producto        — Prenda de ropa con precio, marca, material y género.
    VarianteProducto— Combinación talla + color con stock individual.
    Pedido          — Orden de compra con estado y dirección de envío.
    ItemPedido      — Línea de detalle dentro de un pedido.
    Bloqueo         — Registro de bloqueos de usuario por incumplimiento.

Relaciones:
    Producto ↔ Categoria  (many-to-many via producto_categoria)
    Producto → VarianteProducto (one-to-many, cascade delete)
    Pedido   → ItemPedido       (one-to-many, cascade delete)
    Usuario  → Pedido           (one-to-many)
    Usuario  → Bloqueo          (one-to-many)
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Boolean,
    DateTime, Date, ForeignKey, Enum as SAEnum, Table
)
from sqlalchemy.orm import relationship, DeclarativeBase
import enum


class Base(DeclarativeBase):
    """Base declarativa compartida por todos los modelos."""
    pass


# ─── Enums ────────────────────────────────────────────────────────────────────

class TipoUsuario(str, enum.Enum):
    """Roles disponibles en el sistema."""
    admin = "admin"
    cliente = "cliente"


class EstadoPedido(str, enum.Enum):
    """Ciclo de vida de un pedido."""
    pendiente = "pendiente"
    confirmado = "confirmado"
    enviado = "enviado"
    entregado = "entregado"
    cancelado = "cancelado"


class TallaPrenda(str, enum.Enum):
    """Tallas estándar de ropa."""
    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"
    XXL = "XXL"
    UNICA = "UNICA"


# ─── Tabla asociativa: producto ↔ categoría (many-to-many) ────────────────────

producto_categoria = Table(
    "producto_categoria",
    Base.metadata,
    Column("producto_id", ForeignKey("productos.id"), primary_key=True),
    Column("categoria_id", ForeignKey("categorias.id"), primary_key=True),
)


# ─── Modelos ──────────────────────────────────────────────────────────────────

class Usuario(Base):
    """
    Representa a un usuario del sistema (cliente o administrador).
    El campo tipo_usuario controla el acceso a rutas protegidas.
    El campo activo permite desactivar cuentas sin eliminarlas (soft disable).
    """
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    documento = Column(String(20), unique=True, nullable=False)
    correo = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # Hash bcrypt, nunca texto plano
    telefono = Column(String(20), nullable=True)
    direccion = Column(String(255), nullable=True)
    tipo_usuario = Column(SAEnum(TipoUsuario), default=TipoUsuario.cliente)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pedidos = relationship("Pedido", back_populates="usuario")
    bloqueos = relationship("Bloqueo", back_populates="usuario")


class Categoria(Base):
    """
    Categoría de productos (ej: Camisas, Pantalones, Vestidos).
    El slug es el identificador URL-friendly usado en los filtros del catálogo.
    Soft delete via campo activa=False.
    """
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    slug = Column(String(120), unique=True, nullable=False)  # Ej: "camisas", "pantalones"
    imagen_url = Column(String(500), nullable=True)
    activa = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    productos = relationship("Producto", secondary=producto_categoria, back_populates="categorias")


class Producto(Base):
    """
    Prenda de ropa multimarca con soporte para variantes (talla/color).

    precio_oferta es opcional — si está presente, el frontend lo muestra
    como precio rebajado y lo usa para calcular totales.

    imagenes_extra almacena un JSON array de URLs para galería de imágenes.
    Soft delete via campo activo=False (no se elimina físicamente).
    """
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    precio = Column(Numeric(10, 2), nullable=False)
    precio_oferta = Column(Numeric(10, 2), nullable=True)   # Precio con descuento
    marca = Column(String(100), nullable=True, index=True)
    material = Column(String(150), nullable=True)
    genero = Column(String(20), nullable=True)               # Hombre / Mujer / Unisex
    imagen_url = Column(String(500), nullable=True)
    imagenes_extra = Column(Text, nullable=True)             # JSON array de URLs adicionales
    activo = Column(Boolean, default=True)
    destacado = Column(Boolean, default=False)               # Aparece en sección destacados
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    categorias = relationship("Categoria", secondary=producto_categoria, back_populates="productos")
    variantes = relationship("VarianteProducto", back_populates="producto", cascade="all, delete-orphan")
    items_pedido = relationship("ItemPedido", back_populates="producto")


class VarianteProducto(Base):
    """
    Variante de un producto: combinación única de talla + color con su propio stock.

    Cada variante tiene un SKU opcional para integración con sistemas de inventario.
    stock_minimo sirve para alertas de reabastecimiento (no se valida en la API aún).
    """
    __tablename__ = "variantes_producto"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    talla = Column(SAEnum(TallaPrenda), nullable=False)
    color = Column(String(50), nullable=True)
    sku = Column(String(100), unique=True, nullable=True)    # Código único de inventario
    stock = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=2)                # Umbral de alerta de stock bajo
    created_at = Column(DateTime, default=datetime.utcnow)

    producto = relationship("Producto", back_populates="variantes")
    items_pedido = relationship("ItemPedido", back_populates="variante")


class Pedido(Base):
    """
    Orden de compra generada desde el carrito del frontend.

    El estado sigue el ciclo: pendiente → confirmado → enviado → entregado.
    También puede cancelarse en cualquier punto antes de enviado.
    El total se calcula en el router al momento de crear el pedido.
    """
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    estado = Column(SAEnum(EstadoPedido), default=EstadoPedido.pendiente, index=True)
    total = Column(Numeric(10, 2), nullable=False, default=0)
    direccion_envio = Column(String(500), nullable=True)
    notas = Column(Text, nullable=True)
    fecha_pedido = Column(DateTime, default=datetime.utcnow, index=True)
    fecha_entrega = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="pedidos")
    items = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")


class ItemPedido(Base):
    """
    Línea de detalle de un pedido.

    Almacena el precio_unitario al momento de la compra para preservar
    el historial aunque el precio del producto cambie después.
    variante_id es opcional para productos sin variantes de talla/color.
    """
    __tablename__ = "items_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    variante_id = Column(Integer, ForeignKey("variantes_producto.id"), nullable=True)
    cantidad = Column(Integer, nullable=False, default=1)
    precio_unitario = Column(Numeric(10, 2), nullable=False)  # Precio al momento de compra
    subtotal = Column(Numeric(10, 2), nullable=False)          # precio_unitario * cantidad

    pedido = relationship("Pedido", back_populates="items")
    producto = relationship("Producto", back_populates="items_pedido")
    variante = relationship("VarianteProducto", back_populates="items_pedido")


class Bloqueo(Base):
    """
    Registro de bloqueo de un usuario por incumplimiento de políticas.
    Migrado 1:1 desde el sistema Laravel original.
    fecha_fin=None indica bloqueo indefinido.
    """
    __tablename__ = "bloqueos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    motivo = Column(String(500), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=True)   # None = bloqueo indefinido
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="bloqueos")
