from fastapi import FastAPI

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
    return {
        "total_productos": 0,
        "entradas_hoy": 0,
        "salidas_hoy": 0,
        "alertas_activas": 0,
        "movimientos_7_dias": [],
        "ultimos_movimientos": []
    }