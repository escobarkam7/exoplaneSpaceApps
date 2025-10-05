from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncpg
import os
app = FastAPI()

# Monta los archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configura templates
templates = Jinja2Templates(directory="templates")

# Importa e incluye las rutas - CORREGIDO
from app.routes import router
app.include_router(router, prefix="/api")

# Endpoint para el dashboard
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# Database
@app.get("/database", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/classify", response_class=HTMLResponse)
async def classify_page(request: Request):  # ✅ CORREGIDO: añadí request parameter
    return templates.TemplateResponse("classify.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
@app.get("/planets/{dataset}")
async def get_planets(dataset: str, limit: int = 50):
    """
    Endpoint para la página de database - conecta con PostgreSQL
    """
    try:
        # Aquí va tu lógica para conectar con PostgreSQL
        # Por ahora devuelve datos de ejemplo
        
        if dataset not in ['kepler', 'k2planets', 'tess']:
            raise HTTPException(status_code=404, detail="Dataset no encontrado")
        
        # Datos de ejemplo - reemplaza con tu conexión real a PostgreSQL
        sample_data = [
            {
                "kepler_name": f"KEPLER-{i}",
                "kepoi_name": f"K{i}",
                "kepid": f"KIC{1000000 + i}",
                "koi_disposition": "CONFIRMED",
                "koi_period": 100 + i,
                "koi_prad": 2.5,
                "koi_teq": 500,
                "koi_steff": 6000
            } for i in range(min(limit, 10))
        ]
        
        return JSONResponse({
            "data": sample_data,
            "total": len(sample_data),
            "dataset": dataset
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)