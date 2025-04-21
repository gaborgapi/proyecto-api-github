"""Este es el router del modulo dependabots"""
from typing import Optional
from fastapi import APIRouter, Query
from app.dependabots.dependabots_service import (
    obtener_dependabots_solucionados_y_no_solucionados
)

# Crear una instancia del router
router = APIRouter()


@router.get("/v1/dependabots")
async def get_dependabots(
    repo_owner: str,
    repo_name: str,
    start_date: Optional[str] = Query(
        None, description="Fecha de inicio en formato YYYY-MM-DD"
    ),
    end_date: Optional[str] = Query(
        None, description="Fecha de fin en formato YYYY-MM-DD"
    )
):
    """
    Endpoint para obtener las alertas de Dependabot clasificadas
    como solucionadas o no solucionadas, filtradas por repositorio
    y rango de fechas.
    """
    # Llamar a la función que obtiene los datos
    result = await obtener_dependabots_solucionados_y_no_solucionados(
        repo_owner=repo_owner,
        repo_name=repo_name,
        start_date=start_date,
        end_date=end_date
    )

    # Devolver el resultado en formato JSON
    return result
