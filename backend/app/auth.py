"""
auth.py — Lógica de autenticación JWT y dependencias de seguridad.

Provee:
    hash_password()      — Hashea una contraseña en texto plano con bcrypt.
    verify_password()    — Verifica una contraseña contra su hash.
    create_access_token()— Genera un JWT firmado con expiración configurable.
    get_current_user()   — Dependencia FastAPI: decodifica el token y retorna el usuario activo.
    require_admin()      — Dependencia FastAPI: exige que el usuario sea administrador.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import get_db
from app.models import Usuario, TipoUsuario

# Contexto de hashing — usa bcrypt, depreca esquemas antiguos automáticamente
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema OAuth2 — apunta al endpoint de login para la documentación Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    """Retorna el hash bcrypt de la contraseña en texto plano."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Compara la contraseña en texto plano contra el hash almacenado."""
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Genera un JWT firmado con los datos proporcionados.

    Args:
        data: Payload del token (ej: {"sub": user_id, "tipo": rol}).
        expires_delta: Tiempo de vida personalizado. Si no se pasa, usa ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        Token JWT como string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    """
    Dependencia FastAPI que valida el JWT del header Authorization.

    Decodifica el token, extrae el user_id del campo 'sub',
    consulta el usuario en la BD y verifica que esté activo.

    Raises:
        HTTPException 401: Si el token es inválido, expirado o el usuario no existe/está inactivo.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(Usuario).where(Usuario.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None or not user.activo:
        raise credentials_exception
    return user


def require_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """
    Dependencia FastAPI que exige rol de administrador.

    Reutiliza get_current_user y agrega la verificación de tipo_usuario.

    Raises:
        HTTPException 403: Si el usuario autenticado no es admin.
    """
    if current_user.tipo_usuario != TipoUsuario.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso solo para administradores",
        )
    return current_user
