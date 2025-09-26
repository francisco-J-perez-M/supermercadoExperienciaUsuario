from db.conexion import get_db

class ProductoModel:
    def __init__(self):
        db = get_db()
        self.collection_areas = db["areas"]
        self.collection_productos = db["productos"]

    def obtener_areas(self):
        return list(self.collection_areas.find().sort("nombre"))

    def obtener_productos_por_area(self, area_id):
        return list(self.collection_productos.find({"area_id": area_id}).sort("nombre"))
