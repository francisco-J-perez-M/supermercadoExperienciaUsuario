from models.producto import ProductoModel

def cargar_areas():
    modelo = ProductoModel()
    return modelo.obtener_areas()

def cargar_productos_por_area(area_id):
    modelo = ProductoModel()
    return modelo.obtener_productos_por_area(area_id)
