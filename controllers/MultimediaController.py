import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import gridfs
import io
import os
import tempfile
import cv2
from db.conexion import get_db


class MultimediaController:
    def __init__(self, root):
        self.root = root
        self.db = get_db()
        self.fs = gridfs.GridFS(self.db, collection="multimedia")
        self.view = None

    def set_view(self, view):
        """Establece la vista asociada al controlador"""
        self.view = view

    def inicializar(self):
        """Inicializa la aplicación"""
        if self.view:
            self.view.crear_vista()

    # ----------------------------------------------------------
    # Métodos funcionales
    # ----------------------------------------------------------

    def actualizar_lista_archivos(self, event=None):
        """Carga los nombres de archivos del tipo seleccionado"""
        if not self.view:
            return

        tipo = self.view.obtener_tipo_seleccionado()
        archivos = self._obtener_archivos_bd(tipo)
        self.view.actualizar_lista_ui(archivos)

    def _obtener_archivos_bd(self, tipo):
        """Obtiene archivos de la base de datos"""
        try:
            archivos = self.fs.find({"tipo": tipo}).limit(100)
            return [archivo.filename for archivo in archivos]
        except Exception as e:
            if self.view:
                self.view.mostrar_error("Error", f"Error al cargar archivos: {str(e)}")
            return []

    def ver_archivo(self, event=None):
        """Muestra imagen o reproduce video seleccionado"""
        if not self.view:
            return

        tipo = self.view.obtener_tipo_seleccionado()
        nombre = self.view.obtener_archivo_seleccionado()
        
        if not nombre:
            self.view.mostrar_advertencia("Atención", "Selecciona un archivo de la lista.")
            return

        archivo = self.fs.find_one({"filename": nombre})
        if not archivo:
            self.view.mostrar_error("Error", "No se encontró el archivo en la base de datos.")
            return

        data = archivo.read()

        if tipo in ("imagen", "foto"):
            self._mostrar_imagen(data)
        elif tipo == "video":
            self._reproducir_video_temporal(data, nombre)

    def _mostrar_imagen(self, data):
        """Convierte bytes a imagen y la muestra en el label"""
        try:
            imagen = Image.open(io.BytesIO(data))
            imagen = imagen.resize((400, 400), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(imagen)
            
            if self.view:
                self.view.mostrar_imagen(img_tk)
                
        except Exception as e:
            if self.view:
                self.view.mostrar_error("Error al mostrar imagen", str(e))

    def _reproducir_video_temporal(self, data, nombre):
        """Guarda video temporalmente y lo reproduce con OpenCV"""
        try:
            temp_path = os.path.join(tempfile.gettempdir(), nombre)
            with open(temp_path, "wb") as f:
                f.write(data)

            cap = cv2.VideoCapture(temp_path)
            if not cap.isOpened():
                self.view.mostrar_error("Error", "No se pudo abrir el video.")
                return

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                cv2.imshow(f"Reproduciendo: {nombre}", frame)
                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()
            
            # Limpiar archivo temporal
            try:
                os.unlink(temp_path)
            except:
                pass
                
        except Exception as e:
            if self.view:
                self.view.mostrar_error("Error al reproducir video", str(e))