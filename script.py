import random
from datetime import datetime, timedelta
from conexion import get_db
from pymongo.errors import BulkWriteError

# --------------------------------------------------------------------------------------
# 1. Conectar a la base de datos
# --------------------------------------------------------------------------------------
db = get_db()
print("Conexión a la base de datos establecida.")

# --------------------------------------------------------------------------------------
# 2. Poblar la colección 'usuarios' (solo si está vacía)
# --------------------------------------------------------------------------------------
usuarios = db["usuarios"]
if usuarios.count_documents({}) == 0:
    usuarios.insert_many([
        {"usuario": "admin", "password": "1234", "rol": "administrador"},
        {"usuario": "vendedor1", "password": "1234", "rol": "vendedor"},
        {"usuario": "vendedor2", "password": "1234", "rol": "vendedor"},
    ])
    print("Colección 'usuarios' poblada.")
else:
    print("Colección 'usuarios' ya tiene datos, no se modificó.")

# --------------------------------------------------------------------------------------
# 3. Poblar las colecciones 'areas' y 'productos' (solo si están vacías)
# --------------------------------------------------------------------------------------
areas = db["areas"]
productos_col = db["productos"]

if areas.count_documents({}) == 0:
    areas.insert_many([
        {"_id": 1, "nombre": "Abarrotes"},
        {"_id": 2, "nombre": "Frutas y Verduras"},
        {"_id": 3, "nombre": "Carnes y Pescados"},
        {"_id": 4, "nombre": "Lácteos y Huevos"},
        {"_id": 5, "nombre": "Panadería y Repostería"},
        {"_id": 6, "nombre": "Bebidas"},
        {"_id": 7, "nombre": "Congelados"},
        {"_id": 8, "nombre": "Higiene Personal"},
        {"_id": 9, "nombre": "Limpieza del Hogar"},
        {"_id": 10, "nombre": "Mascotas"},
        {"_id": 11, "nombre": "Electrónica"}
    ])
    print("Colección 'areas' poblada.")
else:
    print("Colección 'areas' ya tiene datos, no se modificó.")

if productos_col.count_documents({}) == 0:
    productos = [
        {"nombre": "Arroz", "precio": 20, "area_id": 1},
        {"nombre": "Aceite Vegetal", "precio": 35, "area_id": 1},
        {"nombre": "Lentejas", "precio": 18, "area_id": 1},
        {"nombre": "Atún enlatado", "precio": 25, "area_id": 1},
        {"nombre": "Pasta", "precio": 12, "area_id": 1},
        {"nombre": "Frijol", "precio": 22, "area_id": 1},
        {"nombre": "Harina de Trigo", "precio": 18, "area_id": 1},
        {"nombre": "Azúcar", "precio": 15, "area_id": 1},
        {"nombre": "Manzana", "precio": 15, "area_id": 2},
        {"nombre": "Plátano", "precio": 12, "area_id": 2},
        {"nombre": "Tomate", "precio": 8, "area_id": 2},
        {"nombre": "Aguacate", "precio": 30, "area_id": 2},
        {"nombre": "Cebolla", "precio": 7, "area_id": 2},
        {"nombre": "Zanahoria", "precio": 9, "area_id": 2},
        {"nombre": "Leche Entera", "precio": 25, "area_id": 4},
        {"nombre": "Queso Panela", "precio": 60, "area_id": 4},
        {"nombre": "Pan de Molde", "precio": 30, "area_id": 5},
        {"nombre": "Jugo de Naranja", "precio": 28, "area_id": 6},
        {"nombre": "Refresco de Cola", "precio": 15, "area_id": 6},
        {"nombre": "Helado de Vainilla", "precio": 70, "area_id": 7},
        {"nombre": "Shampoo", "precio": 45, "area_id": 8},
        {"nombre": "Detergente Líquido", "precio": 80, "area_id": 9},
        {"nombre": "Alimento para perro", "precio": 120, "area_id": 10},
        {"nombre": "Audífonos inalámbricos", "precio": 400, "area_id": 11},
    ]
    productos_col.insert_many(productos)
    print("Colección 'productos' poblada.")
else:
    print("Colección 'productos' ya tiene datos, no se modificó.")

# --------------------------------------------------------------------------------------
# 4. Poblar la colección 'clientes' con hasta 1 millón de registros
# --------------------------------------------------------------------------------------
def generar_cliente(id_cliente: int, productos_db):
    """Genera un documento de cliente con una compra aleatoria."""
    num_productos = random.randint(1, 5)
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

    fecha = datetime.now() - timedelta(
        days=random.randint(0, 365),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )

    return {
        "nombre": f"Cliente {id_cliente}",
        "productos": productos_finales,
        "total": total,
        "fecha": fecha.isoformat()
    }

def poblar_clientes(n=1_000_000, batch_size=10_000):
    """Pobla la colección 'clientes' con 'n' documentos en lotes."""
    coleccion_clientes = db["clientes"]
    productos_db = list(productos_col.find({}, {"_id": 0, "nombre": 1, "precio": 1}))
    if not productos_db:
        print("No hay productos en la colección 'productos'. Poblado cancelado.")
        return

    inicio = coleccion_clientes.count_documents({})
    for i in range(inicio, n, batch_size):
        batch = [
            generar_cliente(j, productos_db)
            for j in range(i + 1, min(i + batch_size + 1, n + 1))
        ]
        try:
            coleccion_clientes.insert_many(batch, ordered=False)
            print(f"Insertados {i + len(batch)} / {n} clientes")
        except BulkWriteError as bwe:
            print("Error en inserción masiva:", bwe.details)

if __name__ == "__main__":
    poblar_clientes()

print("\nBase de datos poblada exitosamente.")
