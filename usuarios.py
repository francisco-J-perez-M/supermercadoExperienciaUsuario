from conexion import get_db

db = get_db()
usuarios = db["usuarios"]

usuarios.insert_many([
    {"usuario": "admin", "password": "1234", "rol": "administrador"},
    {"usuario": "vendedor1", "password": "1234", "rol": "vendedor"},
    {"usuario": "vendedor2", "password": "1234", "rol": "vendedor"},
])
