from fastapi import FastAPI
from asgiref.sync import sync_to_async

app = FastAPI(
    title="InvPro API",
    description="API REST del Sistema de Inventario - Universidad de Pamplona",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.get("/v1/health")
async def health_check():
    return {
        "status": "ok",
        "sistema": "InvPro",
        "version": "1.0.0"
    }

@app.get("/v1/dashboard/")
async def dashboard():
    return await sync_to_async(_get_dashboard_data)()

def _get_dashboard_data():
    from django.utils import timezone
    from django.db.models import Sum
    from apps.inventory.models import Producto
    from apps.movements.models import Movimiento
    from apps.movements.services import obtener_resumen_movimientos

    hoy = timezone.now().date()

    total_productos = Producto.objects.filter(is_active=True).count()

    entradas_hoy = Movimiento.objects.filter(
        tipo=Movimiento.ENTRADA,
        created_at__date=hoy).count()

    salidas_hoy = Movimiento.objects.filter(
        tipo=Movimiento.SALIDA,
        created_at__date=hoy).count()

    alertas_activas = Producto.objects.filter(
        is_active=True,
        stock_actual__lte=0).count()

    ultimos = []
    for mov in Movimiento.objects.select_related(
            'producto').order_by('-created_at')[:10]:
        ultimos.append({
            "tipo":     mov.tipo,
            "producto": mov.producto.sku,
            "cantidad": float(mov.cantidad),
            "fecha":    mov.created_at.strftime('%d/%m %H:%M'),
        })

    movimientos_7_dias = obtener_resumen_movimientos(dias=7)

    return {
        "total_productos":     total_productos,
        "entradas_hoy":        entradas_hoy,
        "salidas_hoy":         salidas_hoy,
        "alertas_activas":     alertas_activas,
        "movimientos_7_dias":  movimientos_7_dias,
        "ultimos_movimientos": ultimos,
    }