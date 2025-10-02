# controllers/analisis_controller.py
from analytics.analisis_completo import realizar_analisis, test_conexion, exportar_csv

def ejecutar_analisis():
    return realizar_analisis()

def probar_conexion():
    return test_conexion()

def exportar_resultados(contenido):
    exportar_csv(contenido)
