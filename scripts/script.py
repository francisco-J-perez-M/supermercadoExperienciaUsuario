#!/usr/bin/env python3
"""
scripts/script.py

Crea la base de datos 'supermercado_db' y las colecciones necesarias desde cero.
Uso:
    python scripts/script.py [TOTAL_CLIENTS]

Si TOTAL_CLIENTS no se provee, usa 500000.
Salida progresiva por stdout: "Inserted X/TOTAL clientes"
"""
import sys
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Asegurar que la raíz del proyecto esté en sys.path para importar db.conexion
HERE = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from db.conexion import get_db
except Exception as e:
    print("ERROR: no se pudo importar get_db desde db.conexion:", e, file=sys.stderr)
    sys.exit(2)

try:
    import bcrypt
except Exception:
    print("ERROR: bcrypt no está instalado. Instala con: pip install bcrypt", file=sys.stderr)
    sys.exit(2)

DEFAULT_TOTAL = 500_000
BATCH_SIZE = 5000

def parse_args() -> int:
    if len(sys.argv) >= 2:
        try:
            n = int(sys.argv[1])
            if n <= 0:
                raise ValueError()
            return n
        except Exception:
            print("Argumento inválido; usando valor por defecto:", DEFAULT_TOTAL)
            return DEFAULT_TOTAL
    return DEFAULT_TOTAL

def _hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

def ensure_collections_and_indexes(db):
    # get or create collections by accessing them
    usuarios = db["usuarios"]
    areas = db["areas"]
    productos = db["productos"]
    clientes = db["clientes"]

    # Normalizar usuario_key en documentos existentes (tolerante)
    try:
        usuarios.update_many(
            {"$or": [{"usuario_key": {"$exists": False}}, {"usuario_key": None}]},
            [{"$set": {"usuario_key": {"$toLower": {"$ifNull": ["$usuario", ""]}}}}]
        )
    except Exception:
        # fallback manual
        for d in usuarios.find({"$or": [{"usuario_key": {"$exists": False}}, {"usuario_key": None}]}, {"_id": 1, "usuario": 1}):
            uk = (d.get("usuario") or "").lower()
            usuarios.update_one({"_id": d["_id"]}, {"$set": {"usuario_key": uk}})

    # Índice único parcial sobre usuario_key para evitar fallo por nulls
    try:
        usuarios.create_index("usuario_key", unique=True, partialFilterExpression={"usuario_key": {"$exists": True, "$ne": None}})
    except Exception:
        pass

    return usuarios, areas, productos, clientes

def upsert_seed_users(usuarios):
    pwd = "1234"
    hashed = _hash_password(pwd)
    seeds = [
        {"usuario": "admin", "rol": "administrador"},
        {"usuario": "vendedor1", "rol": "vendedor"},
        {"usuario": "vendedor2", "rol": "vendedor"},
    ]
    now = datetime.utcnow()
    for s in seeds:
        uk = s["usuario"].lower()
        doc = {
            "usuario": s["usuario"],
            "usuario_key": uk,
            "password_hash": hashed,
            "rol": s["rol"],
            "created_at": now
        }
        usuarios.replace_one({"usuario_key": uk}, doc, upsert=True)

def populate_areas_and_products(db):
    # garantizamos recreación desde cero
    if "areas" in db.list_collection_names():
        db.areas.drop()
    if "productos" in db.list_collection_names():
        db.productos.drop()

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
        {"nombre": "Lechuga", "precio": 10, "area_id": 2},
        {"nombre": "Papa", "precio": 11, "area_id": 2},
        {"nombre": "Pollo Entero", "precio": 90, "area_id": 3},
        {"nombre": "Carne Molida de Res", "precio": 150, "area_id": 3},
        {"nombre": "Salmón", "precio": 250, "area_id": 3},
        {"nombre": "Camarones", "precio": 180, "area_id": 3},
        {"nombre": "Filete de Res", "precio": 200, "area_id": 3},
        {"nombre": "Pechuga de Pollo", "precio": 85, "area_id": 3},
        {"nombre": "Tilapia", "precio": 70, "area_id": 3},
        {"nombre": "Leche Entera", "precio": 25, "area_id": 4},
        {"nombre": "Queso Panela", "precio": 60, "area_id": 4},
        {"nombre": "Yogurt Natural", "precio": 18, "area_id": 4},
        {"nombre": "Huevos (docena)", "precio": 40, "area_id": 4},
        {"nombre": "Mantequilla", "precio": 28, "area_id": 4},
        {"nombre": "Crema", "precio": 32, "area_id": 4},
        {"nombre": "Queso Cheddar", "precio": 75, "area_id": 4},
        {"nombre": "Pan de Molde", "precio": 30, "area_id": 5},
        {"nombre": "Galletas de Avena", "precio": 22, "area_id": 5},
        {"nombre": "Pastelillos", "precio": 50, "area_id": 5},
        {"nombre": "Pan Integral", "precio": 35, "area_id": 5},
        {"nombre": "Donas", "precio": 15, "area_id": 5},
        {"nombre": "Croissants", "precio": 20, "area_id": 5},
        {"nombre": "Jugo de Naranja", "precio": 28, "area_id": 6},
        {"nombre": "Agua Mineral", "precio": 10, "area_id": 6},
        {"nombre": "Refresco de Cola", "precio": 15, "area_id": 6},
        {"nombre": "Cerveza", "precio": 30, "area_id": 6},
        {"nombre": "Vino Tinto", "precio": 120, "area_id": 6},
        {"nombre": "Café", "precio": 45, "area_id": 6},
        {"nombre": "Té", "precio": 25, "area_id": 6},
        {"nombre": "Papas a la Francesa Congeladas", "precio": 45, "area_id": 7},
        {"nombre": "Helado de Vainilla", "precio": 70, "area_id": 7},
        {"nombre": "Pizza congelada", "precio": 85, "area_id": 7},
        {"nombre": "Verduras Congeladas", "precio": 40, "area_id": 7},
        {"nombre": "Nuggets de Pollo", "precio": 55, "area_id": 7},
        {"nombre": "Helado de Chocolate", "precio": 75, "area_id": 7},
        {"nombre": "Jabón de Manos", "precio": 20, "area_id": 8},
        {"nombre": "Shampoo", "precio": 45, "area_id": 8},
        {"nombre": "Pasta Dental", "precio": 25, "area_id": 8},
        {"nombre": "Papel higiénico", "precio": 38, "area_id": 8},
        {"nombre": "Desodorante", "precio": 35, "area_id": 8},
        {"nombre": "Crema Corporal", "precio": 50, "area_id": 8},
        {"nombre": "Maquinilla de Afeitar", "precio": 40, "area_id": 8},
        {"nombre": "Detergente Líquido", "precio": 80, "area_id": 9},
        {"nombre": "Cloro", "precio": 15, "area_id": 9},
        {"nombre": "Limpiador multiusos", "precio": 30, "area_id": 9},
        {"nombre": "Jabón para Trastes", "precio": 25, "area_id": 9},
        {"nombre": "Desinfectante", "precio": 35, "area_id": 9},
        {"nombre": "Trapos", "precio": 20, "area_id": 9},
        {"nombre": "Alimento para perro", "precio": 120, "area_id": 10},
        {"nombre": "Arena para gato", "precio": 65, "area_id": 10},
        {"nombre": "Juguete para Mascota", "precio": 45, "area_id": 10},
        {"nombre": "Shampoo para Mascotas", "precio": 55, "area_id": 10},
        {"nombre": "Collar", "precio": 30, "area_id": 10},
        {"nombre": "Audífonos inalámbricos", "precio": 400, "area_id": 11},
        {"nombre": "Cable USB", "precio": 50, "area_id": 11},
        {"nombre": "Cargador", "precio": 80, "area_id": 11},
        {"nombre": "Batería Externa", "precio": 250, "area_id": 11},
        {"nombre": "Adaptador", "precio": 35, "area_id": 11},
        {"nombre": "Mouse Inalámbrico", "precio": 150, "area_id": 11}
    ]
    db.productos.insert_many(productos)

def generar_compra(productos_db: List[Dict[str, Any]], idx: int) -> Dict[str, Any]:
    num_productos = random.randint(1, 5)
    seleccion = random.choices(productos_db, k=num_productos)
    productos_finales = []
    total_price = 0
    for prod in seleccion:
        cantidad = random.randint(1, 5)
        subtotal = prod["precio"] * cantidad
        total_price += subtotal
        productos_finales.append({"nombre": prod["nombre"], "precio": prod["precio"], "cantidad": cantidad})
    fecha = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0,23), minutes=random.randint(0,59))
    return {"nombre": f"Cliente {idx}", "productos": productos_finales, "total": total_price, "fecha": fecha.isoformat()}

def poblar_clientes(db, total: int, batch_size: int = BATCH_SIZE):
    if "clientes" in db.list_collection_names():
        db.clientes.drop()
    coleccion_clientes = db["clientes"]
    productos_db = list(db.productos.find({}, {"_id": 0, "nombre": 1, "precio": 1}))
    if not productos_db:
        raise RuntimeError("No hay productos en la colección 'productos' para generar ventas")
    inserted = 0
    docs = []
    for i in range(1, total + 1):
        docs.append(generar_compra(productos_db, i))
        if len(docs) >= batch_size:
            coleccion_clientes.insert_many(docs)
            inserted += len(docs)
            print(f"Inserted {inserted}/{total} clientes")
            docs = []
    if docs:
        coleccion_clientes.insert_many(docs)
        inserted += len(docs)
        print(f"Inserted {inserted}/{total} clientes")
    print("Clientes poboados correctamente.")

def main():
    total = parse_args()
    print(f"Inicio de poblado: total={total}, batch_size={BATCH_SIZE}")

    db = get_db()
    if db is None:
        print("ERROR: No se pudo conectar a MongoDB desde get_db()", file=sys.stderr)
        sys.exit(2)

    usuarios, areas, productos, clientes = ensure_collections_and_indexes(db)  # usuarios es colección
    print("Colecciones aseguradas, creando/actualizando seeds...")

    upsert_seed_users(usuarios)
    print("Usuarios seed creados/actualizados.")

    print("Poblando areas y productos...")
    populate_areas_and_products(db)

    print("Generando clientes/ventas...")
    poblar_clientes(db, total, batch_size=BATCH_SIZE)

    print("Poblado completado correctamente.")
    sys.exit(0)

if __name__ == "__main__":
    main()
