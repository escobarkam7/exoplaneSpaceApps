from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Monta los archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configura templates
templates = Jinja2Templates(directory="templates")

# Importa y incluye las rutas - CORREGIDO
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
