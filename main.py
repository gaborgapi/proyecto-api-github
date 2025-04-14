"""Este es el main del proyecto."""
# main.py
from fastapi import FastAPI
from app.repositorios.repo_routes import router as repo_router

app = FastAPI()

app.include_router(repo_router)


@app.get("/")
def leer_raiz():
    """Esto imprime un hola mundo"""
    return {"mensaje": "¡Hola mundo.!"}
