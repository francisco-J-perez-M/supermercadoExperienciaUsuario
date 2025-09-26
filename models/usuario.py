from db.conexion import get_db

class UsuarioModel:
    def __init__(self):
        self.collection = get_db()["usuarios"]

    def validar_credenciales(self, usuario, password):
        return self.collection.find_one({"usuario": usuario, "password": password})

    def crear_usuario(self, datos):
        return self.collection.insert_one(datos)

    def obtener_por_rol(self, rol):
        return list(self.collection.find({"rol": rol}))
