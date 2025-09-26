from db.conexion import get_db
from datetime import datetime

class ClienteModel:
    def __init__(self):
        self.collection = get_db()["clientes"]

    def registrar_cliente(self, productos, total):
        num = self.collection.count_documents({})
        cliente = {
            "nombre": f"Cliente {num + 1}",
            "productos": productos,
            "total": total,
            "fecha": datetime.now().isoformat()
        }
        return self.collection.insert_one(cliente)

    def obtener_clientes_hoy(self):
        hoy_str = datetime.now().strftime('%Y-%m-%d')
        return list(self.collection.find({'fecha': {'$regex': f'^{hoy_str}'}}))
