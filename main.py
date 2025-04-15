"""Este es el main del proyecto."""
# main.py
from fastapi import FastAPI
from app.repositorios.repo_routes import router as repo_router
from app.productividad.productividad_router import (
    router as productividad_router
)
from app.dependabots.dependabots_router import (
    router as dependabots_router
)

app = FastAPI()

app.include_router(repo_router, tags=["repositorios"])
app.include_router(productividad_router, tags=["producitividad"])
app.include_router(dependabots_router, tags=["dependabots"])


@app.get("/")
def leer_raiz():
    """Esto imprime un hola mundo"""
    return {"mensaje": "¡Hola mundo.!"}
