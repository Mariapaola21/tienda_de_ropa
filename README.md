# Tienda de Ropa Multimarca

E-commerce de ropa con backend en FastAPI y frontend en Angular. Migrado desde un sistema Laravel monolítico.

---

## Stack

| Capa       | Tecnología                              |
|------------|-----------------------------------------|
| Backend    | Python 3.11+, FastAPI, SQLAlchemy async |
| Base de datos | SQLite (dev) / PostgreSQL (prod)     |
| Autenticación | JWT con python-jose + bcrypt         |
| Frontend   | Angular 21, Tailwind CSS, Signals       |
| HTTP       | Angular HttpClient con interceptores    |

---

## Estructura del proyecto

```
tienda-ropa/
├── backend/
│   ├── app/
│   │   ├── config.py       # Variables de entorno (pydantic-settings)
│   │   ├── database.py     # Engine async y dependencia get_db
│   │   ├── models.py       # Modelos ORM (SQLAlchemy)
│   │   ├── schemas.py      # Schemas Pydantic (validación entrada/salida)
│   │   ├── auth.py         # JWT, bcrypt y dependencias de seguridad
│   │   └── routers/
│   │       ├── auth.py     # POST /api/auth/register, /api/auth/login
│   │       ├── productos.py# CRUD /api/productos
│   │       ├── pedidos.py  # CRUD /api/pedidos
│   │       └── categorias.py # CRUD /api/categorias
│   ├── main.py             # Punto de entrada FastAPI
│   ├── seed.py             # Script para poblar la BD con datos de prueba
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    └── src/app/
        ├── core/
        │   ├── models/     # Interfaces TypeScript (Producto, Carrito)
        │   ├── services/   # ApiService, AuthService, CarritoService, PedidoService
        │   └── interceptors/ # authInterceptor, errorInterceptor
        └── features/
            ├── auth/       # Login, Register, Profile
            └── shop/       # Catálogo, Detalle, Carrito, Editorial
```

---

## Requisitos previos

- Python 3.11 o superior
- Node.js 18 o superior
- npm 9 o superior

---

## Ejecutar en desarrollo

### 1. Backend

```bash
cd backend

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores (SECRET_KEY mínimo)

# Iniciar el servidor (crea las tablas automáticamente al arrancar)
uvicorn main:app --reload
```

El backend queda disponible en `http://localhost:8000`.
Documentación interactiva en `http://localhost:8000/docs`.

### 2. Poblar la base de datos (opcional)

```bash
cd backend
python seed.py
```

### 3. Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar el servidor de desarrollo
npm start
```

El frontend queda disponible en `http://localhost:4200`.

---

## Variables de entorno (backend)

Copia `backend/.env.example` a `backend/.env` y configura:

| Variable                    | Descripción                                      | Default                        |
|-----------------------------|--------------------------------------------------|--------------------------------|
| `DATABASE_URL`              | URL de conexión a la BD                          | SQLite local                   |
| `SECRET_KEY`                | Clave para firmar los JWT (cambiar en producción)| `cambia-esto-en-produccion`    |
| `ALGORITHM`                 | Algoritmo JWT                                    | `HS256`                        |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración del token en minutos                  | `1440` (24h)                   |
| `DEBUG`                     | Activa logging SQL                               | `false`                        |
| `ALLOWED_ORIGINS`           | Orígenes permitidos por CORS                     | `["http://localhost:4200"]`    |

---

## API — Endpoints principales

### Auth
| Método | Ruta                  | Descripción                  | Auth |
|--------|-----------------------|------------------------------|------|
| POST   | /api/auth/register    | Registrar nuevo usuario      | No   |
| POST   | /api/auth/login       | Login, retorna JWT           | No   |

### Productos
| Método | Ruta                      | Descripción                        | Auth  |
|--------|---------------------------|------------------------------------|-------|
| GET    | /api/productos            | Listar catálogo (con filtros)      | No    |
| GET    | /api/productos/{id}       | Detalle con variantes              | No    |
| POST   | /api/productos            | Crear producto                     | Admin |
| PUT    | /api/productos/{id}       | Actualizar producto                | Admin |
| DELETE | /api/productos/{id}       | Soft delete                        | Admin |

### Pedidos
| Método | Ruta                          | Descripción                    | Auth    |
|--------|-------------------------------|--------------------------------|---------|
| POST   | /api/pedidos                  | Crear pedido desde el carrito  | Usuario |
| GET    | /api/pedidos/mis-pedidos      | Historial del usuario          | Usuario |
| GET    | /api/pedidos                  | Todos los pedidos              | Admin   |
| PATCH  | /api/pedidos/{id}/estado      | Cambiar estado del pedido      | Admin   |

### Categorías
| Método | Ruta                      | Descripción          | Auth  |
|--------|---------------------------|----------------------|-------|
| GET    | /api/categorias           | Listar categorías    | No    |
| POST   | /api/categorias           | Crear categoría      | Admin |
| DELETE | /api/categorias/{id}      | Soft delete          | Admin |

---

## Despliegue en producción

### Backend → Render o Railway

1. Conecta el repositorio en [render.com](https://render.com) o [railway.app](https://railway.app).
2. Configura el directorio raíz como `backend/`.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Agrega las variables de entorno (especialmente `DATABASE_URL` con PostgreSQL y `SECRET_KEY`).

### Frontend → Vercel o Netlify

1. Conecta el repositorio.
2. Configura el directorio raíz como `frontend/`.
3. Build command: `npm run build`
4. Output directory: `dist/frontend/browser`
5. Agrega la variable de entorno `API_URL` apuntando al backend desplegado.

---

## Notas de seguridad

- Nunca subas el archivo `.env` al repositorio (ya está en `.gitignore`).
- Cambia `SECRET_KEY` por una clave aleatoria segura en producción.
- En producción, actualiza `ALLOWED_ORIGINS` con el dominio real del frontend.
