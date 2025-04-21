"""Este es el router"""
# app/routes/repo_routes.py

from fastapi import APIRouter, HTTPException
from app.repositorios.activity_service import clasificar_repositorios

# Creamos un router de FastAPI
router = APIRouter()


@router.get("/v1/repositorios/{usuario}")
async def obtener_repositorios(usuario: str):
    """
    Endpoint que devuelve los repositorios activos e inactivos de un usuario.
    """
    try:
        resultado = await clasificar_repositorios(usuario)

        # Retornamos el resultado como un JSON
        return {
            "total_repositorios": resultado["total"],
            "repo": resultado["repos_con_estado"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=str(e)
        ) from e
