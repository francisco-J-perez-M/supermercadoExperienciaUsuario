from db.conexion import get_db

def poblar_base_servidor():
    db = get_db()

    # Usuarios
    usuarios = db["usuarios"]
    if usuarios.count_documents({}) == 0:
        usuarios.insert_many([
            {"usuario": "admin", "password": "1234", "rol": "administrador"},
            {"usuario": "vendedor1", "password": "1234", "rol": "vendedor"},
            {"usuario": "vendedor2", "password": "1234", "rol": "vendedor"},
        ])

    # Áreas y productos (puedes reducir el set para pruebas)
    # Clientes: opcional, máximo 10
