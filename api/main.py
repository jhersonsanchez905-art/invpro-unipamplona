from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from asgiref.sync import sync_to_async

app = FastAPI(
    title="InvPro API",
    description="API REST del Sistema de Inventario - Universidad de Pamplona",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── SCHEMAS ───────────────────────────────────────────────────────
class ProductoResponse(BaseModel):
    id:              str
    nombre:          str
    sku:             str
    descripcion:     str
    categoria_id:    str
    categoria_nombre:str
    stock_actual:    float
    stock_minimo:    float
    precio_unitario: float
    tiene_alerta:    bool
    is_active:       bool

class ProductoCreate(BaseModel):
    nombre:          str
    sku:             str
    descripcion:     Optional[str] = ''
    categoria_id:    str
    stock_actual:    float = 0
    stock_minimo:    float = 0
    precio_unitario: float = 0

class ProductoUpdate(BaseModel):
    nombre:          Optional[str] = None
    descripcion:     Optional[str] = None
    categoria_id:    Optional[str] = None
    stock_minimo:    Optional[float] = None
    precio_unitario: Optional[float] = None

# ── HEALTH ────────────────────────────────────────────────────────
@app.get("/v1/health")
async def health_check():
    return {"status": "ok", "sistema": "InvPro", "version": "1.0.0"}

# ── DASHBOARD ─────────────────────────────────────────────────────
@app.get("/v1/dashboard/")
async def dashboard():
    return await sync_to_async(_get_dashboard_data)()

def _get_dashboard_data():
    from django.utils import timezone
    from apps.inventory.models import Producto
    from apps.movements.models import Movimiento
    from apps.movements.services import obtener_resumen_movimientos

    hoy = timezone.now().date()
    total_productos  = Producto.objects.filter(is_active=True).count()
    entradas_hoy     = Movimiento.objects.filter(
        tipo=Movimiento.ENTRADA, created_at__date=hoy).count()
    salidas_hoy      = Movimiento.objects.filter(
        tipo=Movimiento.SALIDA, created_at__date=hoy).count()
    alertas_activas  = Producto.objects.filter(
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

    return {
        "total_productos":     total_productos,
        "entradas_hoy":        entradas_hoy,
        "salidas_hoy":         salidas_hoy,
        "alertas_activas":     alertas_activas,
        "movimientos_7_dias":  obtener_resumen_movimientos(dias=7),
        "ultimos_movimientos": ultimos,
    }

# ── PRODUCTOS — LISTAR ────────────────────────────────────────────
@app.get("/v1/productos/")
async def listar_productos(
    categoria: Optional[str] = None,
    alerta:    Optional[bool] = None,
    buscar:    Optional[str]  = None,
):
    return await sync_to_async(_listar_productos)(categoria, alerta, buscar)

def _listar_productos(categoria, alerta, buscar):
    from apps.inventory.models import Producto
    qs = Producto.objects.select_related('categoria').filter(is_active=True)

    if categoria:
        qs = qs.filter(categoria__nombre__icontains=categoria)
    if alerta is True:
        qs = qs.filter(stock_actual__lte=0)
    if buscar:
        qs = qs.filter(nombre__icontains=buscar) | \
             qs.filter(sku__icontains=buscar)

    return [_producto_to_dict(p) for p in qs]

# ── PRODUCTOS — DETALLE ───────────────────────────────────────────
@app.get("/v1/productos/{producto_id}")
async def detalle_producto(producto_id: str):
    return await sync_to_async(_detalle_producto)(producto_id)

def _detalle_producto(producto_id):
    from apps.inventory.models import Producto
    try:
        p = Producto.objects.select_related('categoria').get(
            id=producto_id, is_active=True)
        return _producto_to_dict(p)
    except Producto.DoesNotExist:
        raise HTTPException(status_code=404, detail='Producto no encontrado')

# ── PRODUCTOS — CREAR ─────────────────────────────────────────────
@app.post("/v1/productos/", status_code=201)
async def crear_producto(data: ProductoCreate):
    return await sync_to_async(_crear_producto)(data)

def _crear_producto(data):
    from apps.inventory.models import Producto, Categoria
    from django.core.exceptions import ValidationError

    try:
        cat = Categoria.objects.get(id=data.categoria_id, is_active=True)
    except Categoria.DoesNotExist:
        raise HTTPException(status_code=404, detail='Categoria no encontrada')

    if Producto.objects.filter(sku=data.sku).exists():
        raise HTTPException(status_code=400,
            detail=f'Ya existe un producto con SKU {data.sku}')

    p = Producto.objects.create(
        nombre=data.nombre,
        sku=data.sku,
        descripcion=data.descripcion or '',
        categoria=cat,
        stock_actual=data.stock_actual,
        stock_minimo=data.stock_minimo,
        precio_unitario=data.precio_unitario,
    )
    return _producto_to_dict(p)

# ── PRODUCTOS — ACTUALIZAR ────────────────────────────────────────
@app.patch("/v1/productos/{producto_id}")
async def actualizar_producto(producto_id: str, data: ProductoUpdate):
    return await sync_to_async(_actualizar_producto)(producto_id, data)

def _actualizar_producto(producto_id, data):
    from apps.inventory.models import Producto, Categoria

    try:
        p = Producto.objects.select_related('categoria').get(
            id=producto_id, is_active=True)
    except Producto.DoesNotExist:
        raise HTTPException(status_code=404, detail='Producto no encontrado')

    if data.nombre          is not None: p.nombre          = data.nombre
    if data.descripcion     is not None: p.descripcion     = data.descripcion
    if data.stock_minimo    is not None: p.stock_minimo    = data.stock_minimo
    if data.precio_unitario is not None: p.precio_unitario = data.precio_unitario

    if data.categoria_id is not None:
        try:
            p.categoria = Categoria.objects.get(
                id=data.categoria_id, is_active=True)
        except Categoria.DoesNotExist:
            raise HTTPException(status_code=404,
                detail='Categoria no encontrada')

    p.save()
    return _producto_to_dict(p)

# ── PRODUCTOS — ELIMINAR (soft delete) ────────────────────────────
@app.delete("/v1/productos/{producto_id}", status_code=204)
async def eliminar_producto(producto_id: str):
    await sync_to_async(_eliminar_producto)(producto_id)

def _eliminar_producto(producto_id):
    from apps.inventory.models import Producto
    try:
        p = Producto.objects.get(id=producto_id, is_active=True)
        p.is_active = False
        p.save(update_fields=['is_active'])
    except Producto.DoesNotExist:
        raise HTTPException(status_code=404, detail='Producto no encontrado')

# ── HELPER ────────────────────────────────────────────────────────
def _producto_to_dict(p):
    return {
        "id":               str(p.id),
        "nombre":           p.nombre,
        "sku":              p.sku,
        "descripcion":      p.descripcion,
        "categoria_id":     str(p.categoria.id),
        "categoria_nombre": p.categoria.nombre,
        "stock_actual":     float(p.stock_actual),
        "stock_minimo":     float(p.stock_minimo),
        "precio_unitario":  float(p.precio_unitario),
        "tiene_alerta":     p.tiene_alerta,
        "is_active":        p.is_active,
    }