# script.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import random
from datetime import datetime, timedelta
from db.conexion import get_db

# Seguridad para passwords
import bcrypt

# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def _hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

def _ensure_usuario_key_and_index(collection):
    # Normalizar documentos que no tengan usuario_key
    try:
        collection.update_many(
            {"$or": [{"usuario_key": {"$exists": False}}, {"usuario_key": None}]},
            [{"$set": {"usuario_key": {"$toLower": {"$ifNull": ["$usuario", ""]}}}}]
        )
    except Exception as e:
        print("⚠️ Warning al normalizar usuario_key:", e)

    # Crear índice único parcial para usuario_key (evita fallar por documentos con usuario_key nulo)
    try:
        collection.create_index("usuario_key", unique=True, partialFilterExpression={"usuario_key": {"$exists": True, "$ne": None}})
    except Exception as e:
        print("⚠️ Warning al crear índice usuario_key único:", e)

# --------------------------------------------------------------------------------------
# 1. Conectar a la base de datos
# --------------------------------------------------------------------------------------
db = get_db()
print("✅ Conexión a la base de datos establecida.")

# --------------------------------------------------------------------------------------
# 2. Poblar la colección 'usuarios' (contraseñas hasheadas, usuario_key normalizado)
# --------------------------------------------------------------------------------------
usuarios = db["usuarios"]

# Normalizar existentes y asegurar índice de forma segura
_ensure_usuario_key_and_index(usuarios)

# Usuarios a insertar/actualizar (misma contraseña '1234' pero guardada hasheada)
default_password = "1234"
password_hash = _hash_password(default_password)

seed_users = [
    {"usuario": "admin", "rol": "administrador"},
    {"usuario": "vendedor1", "rol": "vendedor"},
    {"usuario": "vendedor2", "rol": "vendedor"},
]

for u in seed_users:
    usuario_key = u["usuario"].lower()
    doc = {
        "usuario": u["usuario"],
        "usuario_key": usuario_key,
        "password_hash": password_hash,
        "rol": u["rol"],
        "created_at": datetime.utcnow()
    }
    # upsert para evitar duplicados y dejar consistencia
    usuarios.replace_one({"usuario_key": usuario_key}, doc, upsert=True)

print("✅ Colección 'usuarios' poblada (contraseñas hasheadas).")

# --------------------------------------------------------------------------------------
# 3. Poblar las colecciones 'areas' y 'productos'
# --------------------------------------------------------------------------------------
# Eliminar colecciones existentes para empezar de cero
db.areas.drop()
db.productos.drop()
print("⚠️ Colecciones 'areas' y 'productos' eliminadas para ser repobladas.")

# Insertar Áreas
areas = [
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
]
db.areas.insert_many(areas)
print("✅ Colección 'areas' poblada.")

# Insertar Productos
productos = [
    # Abarrotes
    {"nombre": "Arroz", "precio": 20, "area_id": 1},
    {"nombre": "Aceite Vegetal", "precio": 35, "area_id": 1},
    {"nombre": "Lentejas", "precio": 18, "area_id": 1},
    {"nombre": "Atún enlatado", "precio": 25, "area_id": 1},
    {"nombre": "Pasta", "precio": 12, "area_id": 1},
    {"nombre": "Frijol", "precio": 22, "area_id": 1},
    {"nombre": "Harina de Trigo", "precio": 18, "area_id": 1},
    {"nombre": "Azúcar", "precio": 15, "area_id": 1},
    
    # Frutas y Verduras
    {"nombre": "Manzana", "precio": 15, "area_id": 2},
    {"nombre": "Plátano", "precio": 12, "area_id": 2},
    {"nombre": "Tomate", "precio": 8, "area_id": 2},
    {"nombre": "Aguacate", "precio": 30, "area_id": 2},
    {"nombre": "Cebolla", "precio": 7, "area_id": 2},
    {"nombre": "Zanahoria", "precio": 9, "area_id": 2},
    {"nombre": "Lechuga", "precio": 10, "area_id": 2},
    {"nombre": "Papa", "precio": 11, "area_id": 2},
    
    # Carnes y Pescados
    {"nombre": "Pollo Entero", "precio": 90, "area_id": 3},
    {"nombre": "Carne Molida de Res", "precio": 150, "area_id": 3},
    {"nombre": "Salmón", "precio": 250, "area_id": 3},
    {"nombre": "Camarones", "precio": 180, "area_id": 3},
    {"nombre": "Filete de Res", "precio": 200, "area_id": 3},
    {"nombre": "Pechuga de Pollo", "precio": 85, "area_id": 3},
    {"nombre": "Tilapia", "precio": 70, "area_id": 3},
    
    # Lácteos y Huevos
    {"nombre": "Leche Entera", "precio": 25, "area_id": 4},
    {"nombre": "Queso Panela", "precio": 60, "area_id": 4},
    {"nombre": "Yogurt Natural", "precio": 18, "area_id": 4},
    {"nombre": "Huevos (docena)", "precio": 40, "area_id": 4},
    {"nombre": "Mantequilla", "precio": 28, "area_id": 4},
    {"nombre": "Crema", "precio": 32, "area_id": 4},
    {"nombre": "Queso Cheddar", "precio": 75, "area_id": 4},
    
    # Panadería y Repostería
    {"nombre": "Pan de Molde", "precio": 30, "area_id": 5},
    {"nombre": "Galletas de Avena", "precio": 22, "area_id": 5},
    {"nombre": "Pastelillos", "precio": 50, "area_id": 5},
    {"nombre": "Pan Integral", "precio": 35, "area_id": 5},
    {"nombre": "Donas", "precio": 15, "area_id": 5},
    {"nombre": "Croissants", "precio": 20, "area_id": 5},
    
    # Bebidas
    {"nombre": "Jugo de Naranja", "precio": 28, "area_id": 6},
    {"nombre": "Agua Mineral", "precio": 10, "area_id": 6},
    {"nombre": "Refresco de Cola", "precio": 15, "area_id": 6},
    {"nombre": "Cerveza", "precio": 30, "area_id": 6},
    {"nombre": "Vino Tinto", "precio": 120, "area_id": 6},
    {"nombre": "Café", "precio": 45, "area_id": 6},
    {"nombre": "Té", "precio": 25, "area_id": 6},
    
    # Congelados
    {"nombre": "Papas a la Francesa Congeladas", "precio": 45, "area_id": 7},
    {"nombre": "Helado de Vainilla", "precio": 70, "area_id": 7},
    {"nombre": "Pizza congelada", "precio": 85, "area_id": 7},
    {"nombre": "Verduras Congeladas", "precio": 40, "area_id": 7},
    {"nombre": "Nuggets de Pollo", "precio": 55, "area_id": 7},
    {"nombre": "Helado de Chocolate", "precio": 75, "area_id": 7},
    
    # Higiene Personal
    {"nombre": "Jabón de Manos", "precio": 20, "area_id": 8},
    {"nombre": "Shampoo", "precio": 45, "area_id": 8},
    {"nombre": "Pasta Dental", "precio": 25, "area_id": 8},
    {"nombre": "Papel higiénico", "precio": 38, "area_id": 8},
    {"nombre": "Desodorante", "precio": 35, "area_id": 8},
    {"nombre": "Crema Corporal", "precio": 50, "area_id": 8},
    {"nombre": "Maquinilla de Afeitar", "precio": 40, "area_id": 8},
    
    # Limpieza del Hogar
    {"nombre": "Detergente Líquido", "precio": 80, "area_id": 9},
    {"nombre": "Cloro", "precio": 15, "area_id": 9},
    {"nombre": "Limpiador multiusos", "precio": 30, "area_id": 9},
    {"nombre": "Jabón para Trastes", "precio": 25, "area_id": 9},
    {"nombre": "Desinfectante", "precio": 35, "area_id": 9},
    {"nombre": "Trapos", "precio": 20, "area_id": 9},
    
    # Mascotas
    {"nombre": "Alimento para perro", "precio": 120, "area_id": 10},
    {"nombre": "Arena para gato", "precio": 65, "area_id": 10},
    {"nombre": "Juguete para Mascota", "precio": 45, "area_id": 10},
    {"nombre": "Shampoo para Mascotas", "precio": 55, "area_id": 10},
    {"nombre": "Collar", "precio": 30, "area_id": 10},
    
    # Electrónica
    {"nombre": "Audífonos inalámbricos", "precio": 400, "area_id": 11},
    {"nombre": "Cable USB", "precio": 50, "area_id": 11},
    {"nombre": "Cargador", "precio": 80, "area_id": 11},
    {"nombre": "Batería Externa", "precio": 250, "area_id": 11},
    {"nombre": "Adaptador", "precio": 35, "area_id": 11},
    {"nombre": "Mouse Inalámbrico", "precio": 150, "area_id": 11}
]
db.productos.insert_many(productos)
print("✅ Colección 'productos' poblada.")

# --------------------------------------------------------------------------------------
# 4. Poblar la colección 'clientes' con datos generados aleatoriamente
# --------------------------------------------------------------------------------------
def generar_cliente(id_cliente: int, productos_db):
    """Genera un documento de cliente con una compra aleatoria."""
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
    """Pobla la colección 'clientes' con 'n' documentos en lotes."""
    coleccion_clientes = db["clientes"]
    coleccion_productos = db["productos"]

    # Obtener todos los productos de la colección 'productos'
    productos_db = list(coleccion_productos.find({}, {"_id": 0, "nombre": 1, "precio": 1}))
    if not productos_db:
        print("⚠️ No hay productos en la colección 'productos'. Poblado de clientes cancelado.")
        return

    # Poblar la colección en lotes para mejorar el rendimiento
    for i in range(0, n, batch_size):
        batch = [generar_cliente(j, productos_db) for j in range(i + 1, min(i + batch_size + 1, n + 1))]
        coleccion_clientes.insert_many(batch)
        print(f"✅ Insertados {i + len(batch)} / {n} clientes")

# Iniciar el proceso de poblado
if __name__ == "__main__":
    poblar_clientes()

print("\n🎉 Base de datos poblada exitosamente con usuarios, áreas, productos y clientes.")
