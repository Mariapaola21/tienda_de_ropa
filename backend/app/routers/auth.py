"""
routers/auth.py — Endpoints de autenticación: registro y login.

Rutas:
    POST /api/auth/register — Crea un nuevo usuario cliente.
    POST /api/auth/login    — Autentica credenciales y retorna un JWT.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioOut, LoginRequest, TokenResponse
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
async def register(data: UsuarioCreate, db: AsyncSession = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema.

    Verifica que el correo no esté ya registrado antes de crear la cuenta.
    La contraseña se almacena hasheada con bcrypt, nunca en texto plano.

    Returns:
        UsuarioOut con los datos del usuario creado (sin contraseña).
    Raises:
        400: Si el correo ya existe en la base de datos.
    """
    # Verificar que el correo no esté en uso
    existing = await db.execute(select(Usuario).where(Usuario.correo == data.correo))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    user = Usuario(
        nombre=data.nombre,
        apellido=data.apellido,
        documento=data.documento,
        correo=data.correo,
        password_hash=hash_password(data.password),  # Hash bcrypt
        telefono=data.telefono,
        direccion=data.direccion,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Autentica al usuario con correo y contraseña.

    Busca el usuario por correo, verifica la contraseña con bcrypt
    y genera un JWT con el user_id y el rol como payload.

    Returns:
        TokenResponse con el access_token JWT y el tipo "bearer".
    Raises:
        401: Si las credenciales son incorrectas.
        403: Si la cuenta está desactivada.
    """
    result = await db.execute(select(Usuario).where(Usuario.correo == data.correo))
    user = result.scalar_one_or_none()

    # Verificar existencia y contraseña en un solo bloque para evitar timing attacks
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta desactivada",
        )

    # El payload incluye el ID como string (estándar JWT) y el rol para autorización
    token = create_access_token({"sub": str(user.id), "tipo": user.tipo_usuario})
    return TokenResponse(access_token=token)
