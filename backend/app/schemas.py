"""
Pydantic schemas — validación de entrada/salida para la API REST.
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator
from app.models import TipoUsuario, EstadoPedido, TallaPrenda


# ─── Auth ─────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    correo: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ─── Usuario ──────────────────────────────────────────────────────────────────

class UsuarioCreate(BaseModel):
    nombre: str
    apellido: str
    documento: str
    correo: EmailStr
    password: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None

class UsuarioOut(BaseModel):
    id: int
    nombre: str
    apellido: str
    correo: str
    tipo_usuario: TipoUsuario
    activo: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Categoría ────────────────────────────────────────────────────────────────

class CategoriaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    slug: str
    imagen_url: Optional[str] = None

class CategoriaOut(BaseModel):
    id: int
    nombre: str
    slug: str
    descripcion: Optional[str]
    imagen_url: Optional[str]
    activa: bool

    model_config = {"from_attributes": True}


# ─── Variante ─────────────────────────────────────────────────────────────────

class VarianteCreate(BaseModel):
    talla: TallaPrenda
    color: Optional[str] = None
    sku: Optional[str] = None
    stock: int = 0
    stock_minimo: int = 2

class VarianteOut(BaseModel):
    id: int
    talla: TallaPrenda
    color: Optional[str]
    sku: Optional[str]
    stock: int

    model_config = {"from_attributes": True}


# ─── Producto ─────────────────────────────────────────────────────────────────

class ProductoCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: Decimal
    precio_oferta: Optional[Decimal] = None
    marca: Optional[str] = None
    material: Optional[str] = None
    genero: Optional[str] = None
    imagen_url: Optional[str] = None
    destacado: bool = False
    categoria_ids: List[int] = []
    variantes: List[VarianteCreate] = []

    @field_validator("precio")
    @classmethod
    def precio_positivo(cls, v):
        if v <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        return v

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[Decimal] = None
    precio_oferta: Optional[Decimal] = None
    marca: Optional[str] = None
    material: Optional[str] = None
    genero: Optional[str] = None
    imagen_url: Optional[str] = None
    destacado: Optional[bool] = None
    activo: Optional[bool] = None

class ProductoOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    precio: Decimal
    precio_oferta: Optional[Decimal]
    marca: Optional[str]
    material: Optional[str]
    genero: Optional[str]
    imagen_url: Optional[str]
    destacado: bool
    activo: bool
    categorias: List[CategoriaOut] = []
    variantes: List[VarianteOut] = []

    model_config = {"from_attributes": True}

class ProductoListOut(BaseModel):
    """Schema ligero para listados (sin variantes completas)."""
    id: int
    nombre: str
    precio: Decimal
    precio_oferta: Optional[Decimal]
    marca: Optional[str]
    imagen_url: Optional[str]
    destacado: bool

    model_config = {"from_attributes": True}


# ─── Pedido ───────────────────────────────────────────────────────────────────

class ItemPedidoCreate(BaseModel):
    producto_id: int
    variante_id: Optional[int] = None
    cantidad: int

class ItemPedidoOut(BaseModel):
    id: int
    producto_id: int
    variante_id: Optional[int]
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal

    model_config = {"from_attributes": True}

class PedidoCreate(BaseModel):
    direccion_envio: Optional[str] = None
    notas: Optional[str] = None
    items: List[ItemPedidoCreate]

class PedidoOut(BaseModel):
    id: int
    estado: EstadoPedido
    total: Decimal
    fecha_pedido: datetime
    fecha_entrega: Optional[date]
    items: List[ItemPedidoOut] = []
    usuario: UsuarioOut

    model_config = {"from_attributes": True}

class PedidoEstadoUpdate(BaseModel):
    estado: EstadoPedido
