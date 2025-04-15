"""Esto es un test"""
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from main import app  # Asegúrate de importar el FastAPI app principal
from app.productividad.productividad_router import (
    router as productividad_router
)

# Registramos el router en la app (si no está ya incluido en main.py)
app.include_router(productividad_router)

client = TestClient(app)


@pytest.fixture
def mock_productividad_data():
    """Este metodo hace un mockea una respuesta de la api"""
    return {
        "repositorio": "repo_test",
        "usuarios_productivos_improductivos": [
            {
                "usuario": "usuario1",
                "status": "productivo",
                "commits": 3,
                "pull_requests_abiertos": 2,
                "pull_requests_no_fusionados": 0
            }
        ]
    }


@patch(
    "app.productividad.productividad_router."
    "obtener_productividad_por_repositorio"
)
def test_obtener_productividad_ok(mock_service, mock_productividad_data):
    """Verifica que el endpoint retorne 200 OK con datos correctos"""

    # Simulamos la respuesta del servicio
    mock_service.return_value = mock_productividad_data

    response = client.get("/v1/repositorio/owner_test/repo_test/productividad")

    assert response.status_code == 200
    assert response.json() == mock_productividad_data


@patch(
    "app.productividad.productividad_router."
    "obtener_productividad_por_repositorio"
)
def test_obtener_productividad_error(mock_service):
    """Verifica que el endpoint maneje errores y retorne 500"""

    # Simulamos que el servicio lanza una excepción
    mock_service.side_effect = Exception("Error interno del servicio")

    response = client.get("/v1/repositorio/owner_test/repo_test/productividad")

    assert response.status_code == 500
    assert response.json() == {"detail": "Error interno del servicio"}
