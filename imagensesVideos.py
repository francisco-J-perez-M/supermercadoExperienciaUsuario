import io
import numpy as np
from PIL import Image
import cv2
import gridfs
from db.conexion import get_db
import os

# ---------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------
db = get_db()
fs = gridfs.GridFS(db, collection="multimedia")
ANCHO, ALTO = 128, 128
FPS = 10
DURACION = 2  # segundos
print("✅ Conectado a MongoDB.\n")

# ---------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------
def guardar_en_mongo(data_bytes, filename, tipo, content_type):
    """Guarda un archivo binario directamente en MongoDB (GridFS)."""
    fs.put(data_bytes, filename=filename, tipo=tipo, contentType=content_type)


def generar_imagen_color(i):
    """Genera una imagen de color sólido y la guarda en MongoDB."""
    color = tuple(np.random.randint(0, 256, 3))
    img = Image.new("RGB", (ANCHO, ALTO), color)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    guardar_en_mongo(buffer.getvalue(), f"imagen_{i:05}.png", "imagen", "image/png")


def generar_imagen_ruido(i):
    """Genera una imagen de ruido aleatorio y la guarda en MongoDB."""
    ruido = np.random.randint(0, 256, (ALTO, ANCHO, 3), dtype=np.uint8)
    img = Image.fromarray(ruido)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    guardar_en_mongo(buffer.getvalue(), f"foto_{i:05}.png", "foto", "image/png")


def generar_video(i):
    """Genera un video corto con colores aleatorios y lo guarda en MongoDB."""
    nombre = f"video_{i:05}.mp4"
    import os
    ruta_temporal = os.path.join(os.getcwd(), nombre)  # Ruta válida en Windows

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(ruta_temporal, fourcc, FPS, (ANCHO, ALTO))

    for _ in range(FPS * DURACION):
        frame = np.random.randint(0, 256, (ALTO, ANCHO, 3), dtype=np.uint8)
        video.write(frame)
    video.release()

    with open(ruta_temporal, "rb") as f:
        guardar_en_mongo(f.read(), nombre, "video", "video/mp4")

    os.remove(ruta_temporal)  # 💡 elimina el archivo local



# ---------------------------------------------
# PROCESO PRINCIPAL
# ---------------------------------------------
def main():
    print("🎨 Generando y guardando imágenes...")
    for i in range(1, 10_001):
        generar_imagen_color(i)
        if i % 1000 == 0:
            print(f"✅ {i}/10000 imágenes guardadas")

    print("\n📸 Generando y guardando fotos (ruido)...")
    for i in range(1, 10_001):
        generar_imagen_ruido(i)
        if i % 1000 == 0:
            print(f"✅ {i}/10000 fotos guardadas")

    print("\n🎥 Generando y guardando videos...")
    for i in range(1, 5_001):
        generar_video(i)
        if i % 100 == 0:
            print(f"🎬 {i}/5000 videos guardados")

    print("\n🎉 ¡Todos los archivos se han generado y guardado directamente en MongoDB!")

if __name__ == "__main__":
    main()
