from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app import routes

app = FastAPI()

# Monta los archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configura templates
templates = Jinja2Templates(directory="templates")

# Incluye tus rutas API existentes
app.include_router(routes.router)

# Endpoint para el dashboard
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Opcional: otro endpoint para el dashboard
@app.get("/dashboard", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
