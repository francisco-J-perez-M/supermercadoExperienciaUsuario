def formatear_moneda(valor):
    return f"${valor:.2f}"

def fecha_actual_iso():
    from datetime import datetime
    return datetime.now().isoformat()
