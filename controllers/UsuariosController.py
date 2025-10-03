# UsuariosController.py
from typing import Optional, List, Dict, Any
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError
from db.conexion import get_db
import re
import bcrypt
from bson.objectid import ObjectId

# Configuración mínima
ALLOWED_ROLES = {"administrador", "vendedor", "cajero", "supervisor"}

# Errores específicos
class UsuarioError(Exception):
    pass

class UsuarioNotFound(UsuarioError):
    pass

class UsuarioExists(UsuarioError):
    pass

def _get_usuarios_collection() -> Collection:
    db = get_db()
    return db["usuarios"]

def _validate_username(username: str) -> None:
    if not isinstance(username, str) or not (3 <= len(username) <= 32):
        raise UsuarioError("El nombre de usuario debe ser texto entre 3 y 32 caracteres")
    if not re.match(r"^[a-zA-Z0-9_.-]+$", username):
        raise UsuarioError("Nombre de usuario contiene caracteres inválidos")

def _validate_password(password: str) -> None:
    if not isinstance(password, str) or len(password) < 6:
        raise UsuarioError("La contraseña debe tener al menos 6 caracteres")

def _validate_role(role: str) -> None:
    if role not in ALLOWED_ROLES:
        raise UsuarioError(f"Rol inválido. Roles permitidos: {', '.join(sorted(ALLOWED_ROLES))}")

def _hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

def _verify_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed)

def create_user(usuario: str, password: str, rol: str = "vendedor", extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Crea un usuario. Lanza UsuarioExists si ya existe y UsuarioError para validación.
    Devuelve el documento insertado (sin contraseña en texto plano).
    """
    _validate_username(usuario)
    _validate_password(password)
    _validate_role(rol)

    usuarios = _get_usuarios_collection()

    # Normalizar usuario para índice único
    usuario_key = usuario.lower()

    doc = {
        "usuario": usuario,
        "usuario_key": usuario_key,
        "password_hash": _hash_password(password),
        "rol": rol,
        "created_at": __import__("datetime").datetime.utcnow()
    }

    if extra:
        # evitar sobrescribir campos sensibles
        extra_filtered = {k: v for k, v in extra.items() if k not in ("password_hash", "usuario_key", "password")}
        doc.update(extra_filtered)

    try:
        result = usuarios.insert_one(doc)
    except DuplicateKeyError:
        raise UsuarioExists(f"El usuario '{usuario}' ya existe")

    # No devolver password_hash
    doc_out = {k: v for k, v in doc.items() if k != "password_hash"}
    doc_out["_id"] = result.inserted_id
    return doc_out

def get_user_by_id(user_id: str) -> Dict[str, Any]:
    """
    Retorna el documento de usuario por _id; lanza UsuarioNotFound si no existe.
    """
    usuarios = _get_usuarios_collection()
    try:
        oid = ObjectId(user_id)
    except Exception:
        raise UsuarioError("ID de usuario inválido")

    doc = usuarios.find_one({"_id": oid}, {"password_hash": 0, "usuario_key": 0})
    if not doc:
        raise UsuarioNotFound("Usuario no encontrado")
    return doc

def get_user_by_username(usuario: str) -> Dict[str, Any]:
    """
    Retorna usuario por nombre (case-insensitive). Lanza UsuarioNotFound si no existe.
    """
    usuarios = _get_usuarios_collection()
    doc = usuarios.find_one({"usuario_key": usuario.lower()}, {"password_hash": 0, "usuario_key": 0})
    if not doc:
        raise UsuarioNotFound("Usuario no encontrado")
    return doc

def list_users(limit: int = 100, skip: int = 0, projection: Optional[Dict[str, int]] = None) -> List[Dict[str, Any]]:
    """
    Lista usuarios paginados. Por defecto no devuelve password_hash ni usuario_key.
    """
    usuarios = _get_usuarios_collection()
    if projection is None:
        projection = {"password_hash": 0, "usuario_key": 0}
    cursor = usuarios.find({}, projection).skip(max(0, skip)).limit(max(1, min(limit, 1000)))
    return list(cursor)

def update_user(user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Actualiza campos permitidos: usuario, password, rol y otros extras seguros.
    Si se actualiza 'usuario', se valida unicidad.
    Devuelve el documento actualizado sin password_hash.
    """
    if not updates:
        raise UsuarioError("No hay campos para actualizar")

    usuarios = _get_usuarios_collection()
    try:
        oid = ObjectId(user_id)
    except Exception:
        raise UsuarioError("ID de usuario inválido")

    db_updates: Dict[str, Any] = {}
    if "usuario" in updates:
        _validate_username(updates["usuario"])
        db_updates["usuario"] = updates["usuario"]
        db_updates["usuario_key"] = updates["usuario"].lower()

    if "password" in updates:
        _validate_password(updates["password"])
        db_updates["password_hash"] = _hash_password(updates["password"])

    if "rol" in updates:
        _validate_role(updates["rol"])
        db_updates["rol"] = updates["rol"]

    # permitir campos extra no sensibles
    for k, v in updates.items():
        if k in ("usuario", "password", "rol", "_id", "password_hash", "usuario_key"):
            continue
        db_updates[k] = v

    if not db_updates:
        raise UsuarioError("No hay campos válidos para actualizar")

    try:
        result = usuarios.find_one_and_update(
            {"_id": oid},
            {"$set": db_updates},
            projection={"password_hash": 0, "usuario_key": 0},
            return_document=True
        )
    except DuplicateKeyError:
        raise UsuarioExists("El nuevo nombre de usuario ya está en uso")

    if not result:
        raise UsuarioNotFound("Usuario no encontrado")

    return result

def delete_user(user_id: str) -> bool:
    """
    Elimina un usuario por _id. Devuelve True si se eliminó, False si no existía.
    """
    usuarios = _get_usuarios_collection()
    try:
        oid = ObjectId(user_id)
    except Exception:
        raise UsuarioError("ID de usuario inválido")

    res = usuarios.delete_one({"_id": oid})
    return res.deleted_count == 1

def authenticate(usuario: str, password: str) -> Dict[str, Any]:
    """
    Comprueba credenciales; devuelve documento sin password_hash si OK.
    Lanza UsuarioNotFound o UsuarioError en caso contrario.
    """
    usuarios = _get_usuarios_collection()
    doc = usuarios.find_one({"usuario_key": usuario.lower()})
    if not doc:
        raise UsuarioNotFound("Usuario o contraseña incorrectos")
    hashed = doc.get("password_hash")
    if not hashed or not _verify_password(password, hashed):
        raise UsuarioNotFound("Usuario o contraseña incorrectos")

    # eliminar campos sensibles
    doc.pop("password_hash", None)
    doc.pop("usuario_key", None)
    return doc

# Opcional: Índices recomendados para ejecutar una vez (por ejemplo, en migración o startup)
def ensure_indexes():
    usuarios = _get_usuarios_collection()
    # índice único case-insensitive usando campo usuario_key
    usuarios.create_index("usuario_key", unique=True)
    usuarios.create_index("rol")
