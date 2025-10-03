# ProductosController.py
from typing import Optional, List, Dict, Any
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, BulkWriteError
from pymongo import ReturnDocument
from db.conexion import get_db
from bson.objectid import ObjectId
import re

# Errores específicos
class ProductoError(Exception):
    pass

class ProductoNotFound(ProductoError):
    pass

class ProductoExists(ProductoError):
    pass

def _get_productos_collection() -> Collection:
    db = get_db()
    return db["productos"]

def _validate_nombre(nombre: str) -> None:
    if not isinstance(nombre, str) or not (1 <= len(nombre) <= 200):
        raise ProductoError("El nombre del producto debe ser texto entre 1 y 200 caracteres")
    if not re.match(r"^[\w\sÁÉÍÓÚáéíóúñÑ\.\-&,()]+$", nombre):
        raise ProductoError("Nombre contiene caracteres inválidos")

def _validate_precio(precio: Any) -> None:
    if not isinstance(precio, (int, float)):
        raise ProductoError("El precio debe ser numérico")
    if precio < 0:
        raise ProductoError("El precio no puede ser negativo")

def _validate_area_id(area_id: Any) -> None:
    if not isinstance(area_id, int) or area_id <= 0:
        raise ProductoError("El campo area_id debe ser un entero positivo")

def _normalize_producto_input(data: Dict[str, Any]) -> Dict[str, Any]:
    doc: Dict[str, Any] = {}
    if "nombre" in data:
        _validate_nombre(data["nombre"])
        doc["nombre"] = data["nombre"].strip()
    if "precio" in data:
        _validate_precio(data["precio"])
        doc["precio"] = float(data["precio"])
    if "area_id" in data:
        _validate_area_id(data["area_id"])
        doc["area_id"] = int(data["area_id"])
    for k in data:
        if k not in ("nombre", "precio", "area_id", "_id"):
            doc[k] = data[k]
    return doc

def create_producto(nombre: str, precio: float, area_id: int, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    _validate_nombre(nombre)
    _validate_precio(precio)
    _validate_area_id(area_id)

    coleccion = _get_productos_collection()
    doc = {"nombre": nombre.strip(), "precio": float(precio), "area_id": int(area_id)}
    if extra:
        extra_filtered = {k: v for k, v in extra.items() if k not in ("_id",)}
        doc.update(extra_filtered)
    try:
        res = coleccion.insert_one(doc)
    except DuplicateKeyError:
        raise ProductoExists("Producto con nombre ya existe")
    doc["_id"] = res.inserted_id
    return doc

def get_producto_by_id(producto_id: str) -> Dict[str, Any]:
    coleccion = _get_productos_collection()
    try:
        oid = ObjectId(producto_id)
    except Exception:
        raise ProductoError("ID de producto inválido")
    doc = coleccion.find_one({"_id": oid})
    if not doc:
        raise ProductoNotFound("Producto no encontrado")
    return doc

def get_producto_by_name(nombre: str) -> Dict[str, Any]:
    coleccion = _get_productos_collection()
    doc = coleccion.find_one({"nombre": {"$regex": f"^{re.escape(nombre)}$", "$options": "i"}})
    if not doc:
        raise ProductoNotFound("Producto no encontrado")
    return doc

def list_productos(limit: int = 100, skip: int = 0, area_id: Optional[int] = None, q: Optional[str] = None, sort_by: str = "nombre", desc: bool = False) -> List[Dict[str, Any]]:
    coleccion = _get_productos_collection()
    limit = max(1, min(limit, 5000))
    skip = max(0, skip)
    query: Dict[str, Any] = {}
    if area_id is not None:
        _validate_area_id(area_id)
        query["area_id"] = int(area_id)
    if q:
        query["nombre"] = {"$regex": re.escape(q), "$options": "i"}
    sort_dir = -1 if desc else 1
    cursor = coleccion.find(query).sort([(sort_by, sort_dir)]).skip(skip).limit(limit)
    return list(cursor)

def update_producto(producto_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    if not updates:
        raise ProductoError("No hay campos para actualizar")
    coleccion = _get_productos_collection()
    try:
        oid = ObjectId(producto_id)
    except Exception:
        raise ProductoError("ID de producto inválido")

    db_updates = _normalize_producto_input(updates)
    if not db_updates:
        raise ProductoError("No hay campos válidos para actualizar")

    try:
        updated = coleccion.find_one_and_update(
            {"_id": oid},
            {"$set": db_updates},
            return_document=ReturnDocument.AFTER
        )
    except DuplicateKeyError:
        raise ProductoExists("Nombre de producto en uso por otro registro")

    if not updated:
        raise ProductoNotFound("Producto no encontrado")
    return updated

def delete_producto(producto_id: str) -> bool:
    coleccion = _get_productos_collection()
    try:
        oid = ObjectId(producto_id)
    except Exception:
        raise ProductoError("ID de producto inválido")
    res = coleccion.delete_one({"_id": oid})
    return res.deleted_count == 1

def bulk_insert_productos(productos: List[Dict[str, Any]], batch_size: int = 1000) -> Dict[str, int]:
    if not isinstance(productos, list) or not productos:
        raise ProductoError("Se requiere una lista no vacía de productos")
    coleccion = _get_productos_collection()
    normalized = []
    for p in productos:
        if "nombre" not in p or "precio" not in p or "area_id" not in p:
            raise ProductoError("Cada producto requiere 'nombre', 'precio' y 'area_id'")
        normalized.append(_normalize_producto_input(p))
    inserted = 0
    failed = 0
    for i in range(0, len(normalized), batch_size):
        batch = normalized[i:i + batch_size]
        try:
            res = coleccion.insert_many(batch, ordered=False)
            inserted += len(res.inserted_ids)
        except BulkWriteError as bwe:
            write_result = bwe.details.get("nInserted") or bwe.details.get("result", {}).get("nInserted", 0)
            inserted += int(write_result)
            failed += len(batch) - int(write_result)
    return {"inserted": inserted, "failed": failed}

def ensure_indexes():
    coleccion = _get_productos_collection()
    coleccion.create_index([("nombre", 1)], unique=False)
    coleccion.create_index("area_id")
    coleccion.create_index([("precio", 1)])
