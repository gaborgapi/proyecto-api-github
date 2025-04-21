"""Este es el router del modulo productividad"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.productividad.productividad_service import (
    obtener_productividad_por_repositorio
)

router = APIRouter()


class ProductividadResponse(BaseModel):
    """Modelo de respuesta que usaremos para el endpoint"""
    repo: str
    usuarios_productivos_improductivos: list


@router.get(
        "/v1/repositorio/{repo_owner}/{repo_name}/productividad",
        response_model=ProductividadResponse
    )
async def obtener_productividad(repo_owner: str, repo_name: str):
    """Endpoint para obtener la productividad de
    los usuarios de un repositorio"""

    try:
        # Llamamos al servicio para obtener la productividad
        resultado = obtener_productividad_por_repositorio(
            repo_owner, repo_name
        )

        # Devolvemos la respuesta
        return await resultado

    except Exception as e:
        # En caso de error, retornamos un mensaje de error
        raise HTTPException(
            status_code=500, detail=str(e)
        ) from e
