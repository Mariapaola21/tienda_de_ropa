"""
Script para poblar la BD con datos de prueba.
Ejecutar: python seed.py
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.models import Base, Producto, Categoria, VarianteProducto, Usuario, TallaPrenda
from app.auth import hash_password
from app.config import settings

engine = create_async_engine(settings.DATABASE_URL)
Session = async_sessionmaker(engine, expire_on_commit=False)


async def seed():
    from sqlalchemy import select, text

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with Session() as db:
        # Verificar si ya hay datos
        result = await db.execute(select(Categoria))
        if result.scalars().first():
            print("⚠️  Ya existen datos en la BD. Nada que hacer.")
            return

        # Categorías
        cats = [
            Categoria(nombre="Camisas", slug="camisas", descripcion="Camisas para hombre y mujer"),
            Categoria(nombre="Pantalones", slug="pantalones", descripcion="Jeans y pantalones"),
            Categoria(nombre="Vestidos", slug="vestidos", descripcion="Vestidos de temporada"),
        ]
        db.add_all(cats)
        await db.flush()

        # Productos
        productos = [
            Producto(nombre="Camisa Lino Premium", precio=89900, marca="Zara", material="Lino",
                     genero="Hombre", destacado=True,
                     imagen_url="https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400",
                     categorias=[cats[0]]),
            Producto(nombre="Jean Slim Fit", precio=129900, precio_oferta=99900, marca="Levi's",
                     material="Denim", genero="Unisex", destacado=True,
                     imagen_url="https://images.unsplash.com/photo-1542272604-787c3835535d?w=400",
                     categorias=[cats[1]]),
            Producto(nombre="Vestido Floral Verano", precio=149900, marca="Mango",
                     material="Viscosa", genero="Mujer", destacado=False,
                     imagen_url="https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=400",
                     categorias=[cats[2]]),
            Producto(nombre="Camisa Oxford Blanca", precio=75900, precio_oferta=59900, marca="H&M",
                     material="Algodón", genero="Hombre", destacado=False,
                     imagen_url="https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=400",
                     categorias=[cats[0]]),
            Producto(nombre="Pantalón Chino Beige", precio=95900, marca="Zara",
                     material="Algodón", genero="Hombre", destacado=True,
                     imagen_url="https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=400",
                     categorias=[cats[1]]),
            Producto(nombre="Vestido Negro Elegante", precio=189900, precio_oferta=159900, marca="Mango",
                     material="Poliéster", genero="Mujer", destacado=True,
                     imagen_url="https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400",
                     categorias=[cats[2]]),
        ]
        db.add_all(productos)
        await db.flush()

        # Variantes
        tallas = [TallaPrenda.S, TallaPrenda.M, TallaPrenda.L, TallaPrenda.XL]
        for p in productos:
            for t in tallas:
                db.add(VarianteProducto(producto_id=p.id, talla=t, color="Negro", stock=10))

        # Admin
        admin = Usuario(nombre="Admin", apellido="Tienda", documento="000001",
                        correo="admin@tienda.com", password_hash=hash_password("admin123"),
                        tipo_usuario="admin")
        db.add(admin)

        await db.commit()
        print("✅ Datos de prueba creados correctamente")
        print("   Admin: admin@tienda.com / admin123")


if __name__ == "__main__":
    asyncio.run(seed())
