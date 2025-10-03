# ClientesController.py
from typing import Optional, List, Dict, Any
from pymongo.collection import Collection
from pymongo.errors import BulkWriteError
from db.conexion import get_db
from bson.objectid import ObjectId
from datetime import datetime
import re
import random

# Errores específicos
class ClienteError(Exception):
    pass

class ClienteNotFound(ClienteError):
    pass

class ClienteExists(ClienteError):
    pass

def _get_clientes_collection() -> Collection:
    db = get_db()
    return db["clientes"]

def _validate_nombre(nombre: str) -> None:
    if not isinstance(nombre, str) or not (3 <= len(nombre) <= 100):
        raise ClienteError("El nombre del cliente debe ser texto entre 3 y 100 caracteres")
    if not re.match(r"^[\w\sÁÉÍÓÚáéíóúñÑ\.\-]+$", nombre):
        raise ClienteError("Nombre contiene caracteres inválidos")

def _validate_productos(productos: List[Dict[str, Any]]) -> None:
    if not isinstance(productos, list) or not productos:
        raise ClienteError("Productos debe ser una lista no vacía")
    for p in productos:
        if not isinstance(p, dict):
            raise ClienteError("Cada producto debe ser un objeto")
        if "nombre" not in p or "precio" not in p or "cantidad" not in p:
            raise ClienteError("Cada producto requiere campos 'nombre', 'precio' y 'cantidad'")
        if not isinstance(p["nombre"], str) or not p["nombre"]:
            raise ClienteError("Producto.nombre inválido")
        if not (isinstance(p["precio"], (int, float)) and p["precio"] >= 0):
            raise ClienteError("Producto.precio inválido")
        if not (isinstance(p["cantidad"], int) and p["cantidad"] > 0):
            raise ClienteError("Producto.cantidad inválido")

def _compute_total(productos: List[Dict[str, Any]]) -> float:
    return sum(float(p["precio"]) * int(p["cantidad"]) for p in productos)

def create_cliente(nombre: str, productos: List[Dict[str, Any]], fecha: Optional[datetime] = None, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    _validate_nombre(nombre)
    _validate_productos(productos)

    coleccion = _get_clientes_collection()
    fecha = fecha or datetime.utcnow()
    doc = {
        "nombre": nombre,
        "productos": productos,
        "total": _compute_total(productos),
        "fecha": fecha.isoformat(),
        "created_at": datetime.utcnow()
    }
    if extra:
        extra_filtered = {k: v for k, v in extra.items() if k not in ("_id", "total", "created_at", "fecha")}
        doc.update(extra_filtered)

    res = coleccion.insert_one(doc)
    doc["_id"] = res.inserted_id
    return doc

def get_cliente_by_id(cliente_id: str) -> Dict[str, Any]:
    coleccion = _get_clientes_collection()
    try:
        oid = ObjectId(cliente_id)
    except Exception:
        raise ClienteError("ID de cliente inválido")
    doc = coleccion.find_one({"_id": oid})
    if not doc:
        raise ClienteNotFound("Cliente no encontrado")
    return doc

def list_clientes(limit: int = 100, skip: int = 0, sort_desc: bool = True, desde: Optional[str] = None, hasta: Optional[str] = None) -> List[Dict[str, Any]]:
    coleccion = _get_clientes_collection()
    limit = max(1, min(limit, 5000))
    skip = max(0, skip)
    query: Dict[str, Any] = {}
    if desde or hasta:
        rango = {}
        if desde:
            rango["$gte"] = desde
        if hasta:
            rango["$lte"] = hasta
        query["fecha"] = rango

    sort = [("fecha", -1 if sort_desc else 1)]
    cursor = coleccion.find(query).sort(sort).skip(skip).limit(limit)
    return list(cursor)

def update_cliente(cliente_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    if not updates:
        raise ClienteError("No hay campos para actualizar")
    coleccion = _get_clientes_collection()
    try:
        oid = ObjectId(cliente_id)
    except Exception:
        raise ClienteError("ID de cliente inválido")

    db_updates: Dict[str, Any] = {}
    if "nombre" in updates:
        _validate_nombre(updates["nombre"])
        db_updates["nombre"] = updates["nombre"]

    if "productos" in updates:
        _validate_productos(updates["productos"])
        db_updates["productos"] = updates["productos"]
        db_updates["total"] = _compute_total(updates["productos"])

    if "fecha" in updates:
        # aceptar string ISO o datetime
        fecha_val = updates["fecha"]
        if isinstance(fecha_val, datetime):
            db_updates["fecha"] = fecha_val.isoformat()
        elif isinstance(fecha_val, str):
            db_updates["fecha"] = fecha_val
        else:
            raise ClienteError("Campo 'fecha' debe ser ISO string o datetime")

    for k, v in updates.items():
        if k in ("nombre", "productos", "fecha", "_id", "total", "created_at"):
            continue
        db_updates[k] = v

    if not db_updates:
        raise ClienteError("No hay campos válidos para actualizar")

    result = coleccion.find_one_and_update(
        {"_id": oid},
        {"$set": db_updates},
        return_document=True
    )
    if not result:
        raise ClienteNotFound("Cliente no encontrado")
    return result

def delete_cliente(cliente_id: str) -> bool:
    coleccion = _get_clientes_collection()
    try:
        oid = ObjectId(cliente_id)
    except Exception:
        raise ClienteError("ID de cliente inválido")
    res = coleccion.delete_one({"_id": oid})
    return res.deleted_count == 1

def bulk_insert_clientes(clientes: List[Dict[str, Any]], batch_size: int = 5000) -> Dict[str, int]:
    """
    Inserta clientes en bloques; devuelve resumen {'inserted': X, 'failed': Y}.
    Validación previa y normalización rápida para evitar errores en bulk.
    """
    if not isinstance(clientes, list) or not clientes:
        raise ClienteError("Se requiere una lista no vacía de clientes para bulk insert")

    coleccion = _get_clientes_collection()
    normalized = []
    for c in clientes:
        if "nombre" not in c or "productos" not in c:
            raise ClienteError("Cada cliente requiere 'nombre' y 'productos'")
        nombre = c["nombre"]
        productos = c["productos"]
        _validate_nombre(nombre)
        _validate_productos(productos)
        fecha = c.get("fecha")
        if isinstance(fecha, datetime):
            fecha = fecha.isoformat()
        elif fecha is None:
            fecha = datetime.utcnow().isoformat()
        normalized.append({
            "nombre": nombre,
            "productos": productos,
            "total": _compute_total(productos),
            "fecha": fecha,
            "created_at": datetime.utcnow()
        })

    inserted = 0
    failed = 0
    for i in range(0, len(normalized), batch_size):
        batch = normalized[i:i + batch_size]
        try:
            res = coleccion.insert_many(batch, ordered=False)
            inserted += len(res.inserted_ids)
        except BulkWriteError as bwe:
            # contar los insertados exitosos según writeErrors
            write_result = bwe.details.get("nInserted", 0) or bwe.details.get("result", {}).get("nInserted", 0)
            inserted += int(write_result)
            failed += len(batch) - int(write_result)

    return {"inserted": inserted, "failed": failed}

def sample_cliente_random() -> Dict[str, Any]:
    """
    Retorna un cliente aleatorio; útil para pruebas y demo.
    """
    coleccion = _get_clientes_collection()
    count = coleccion.count_documents({})
    if count == 0:
        raise ClienteNotFound("No hay clientes en la colección")
    skip = random.randint(0, max(0, count - 1))
    doc = coleccion.find().skip(skip).limit(1)
    return list(doc)[0]

def ensure_indexes():
    coleccion = _get_clientes_collection()
    coleccion.create_index("fecha")
    coleccion.create_index("nombre")
    coleccion.create_index([("created_at", 1)])
