import random
from datetime import datetime, timedelta
from conexion import get_db

def generar_cliente(id_cliente: int, productos_db):
    num_productos = random.randint(1, 5)  # entre 1 y 5 productos
    productos_seleccionados = random.sample(productos_db, num_productos)

    productos_finales = []
    total = 0
    for producto in productos_seleccionados:
        cantidad = random.randint(1, 5)
        subtotal = producto["precio"] * cantidad
        total += subtotal
        productos_finales.append({
            "nombre": producto["nombre"],
            "precio": producto["precio"],
            "cantidad": cantidad
        })

    # Fecha aleatoria dentro del último mes
    fecha = datetime.now() - timedelta(
        days=random.randint(0, 30),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )

    return {
        "nombre": f"Cliente {id_cliente}",
        "productos": productos_finales,
        "total": total,
        "fecha": fecha.isoformat()
    }

def poblar_clientes(n=500_000, batch_size=5000):
    db = get_db()
    coleccion_clientes = db["clientes"]
    coleccion_productos = db["productos"]

    # Obtener todos los productos de la colección
    productos_db = list(coleccion_productos.find({}, {"_id": 0, "nombre": 1, "precio": 1}))
    if not productos_db:
        print("⚠️ No hay productos en la colección 'productos'. Poblado cancelado.")
        return

    for i in range(0, n, batch_size):
        batch = [generar_cliente(j, productos_db) for j in range(i + 1, min(i + batch_size + 1, n + 1))]
        coleccion_clientes.insert_many(batch)
        print(f"✅ Insertados {i + len(batch)} / {n} clientes")

if __name__ == "__main__":
    poblar_clientes()
