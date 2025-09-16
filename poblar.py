from conexion import get_db

db = get_db()

# Drop existing collections to start fresh
db.areas.drop()
db.productos.drop()

# ---
## Insertar Áreas (Areas)
# ---

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

# ---
## Insertar Productos (Products)
# ---

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

print("Base de datos poblada.")