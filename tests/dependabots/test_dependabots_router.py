"""Estos son los tests"""
from unittest.mock import patch
from fastapi.testclient import TestClient
import pytest
from main import app

# Datos de ejemplo para los tests
example_alertas = [
    {
        "state": "open",
        "dependency": {"package": {"name": "paquete1"}},
        "security_advisory": {"severity": "high"},
        "created_at": "2025-04-01T00:00:00Z"
    },
    {
        "state": "dismissed",
        "dependency": {"package": {"name": "paquete2"}},
        "security_advisory": {"severity": "medium"},
        "created_at": "2025-03-25T00:00:00Z"
    },
    {
        "state": "fixed",
        "dependency": {"package": {"name": "paquete3"}},
        "security_advisory": {"severity": "low"},
        "created_at": "2025-03-20T00:00:00Z"
    }
]

client = TestClient(app)


@patch("app.dependabots.dependabots_service.get_dependabot_alerts")
def test_obtener_dependabots_solucionados_y_no_solucionados(
    mock_get_dependabot_alerts
):
    """Test para el servicio de obtener dependabots
    solucionados y no solucionados."""
    # Configurar el mock para que devuelva las alertas de ejemplo
    mock_get_dependabot_alerts.side_effect = lambda repo_owner, repo_name, state, start_date, end_date: [
        alerta for alerta in example_alertas if alerta["state"] == state
    ]

    # Realizamos la solicitud GET al endpoint
    response = client.get(
        "/v1/dependabots?repo_owner=usuario&repo_name=repositorio"
    )

    # Verificamos que la respuesta tenga el código de estado 200 OK
    assert response.status_code == 200

    # Verificamos que el contenido de la respuesta sea el esperado
    data = response.json()

    # Verificamos los totales de alertas
    assert data["total_alertas"] == 3
    assert data["total_no_solucionadas"] == 2
    assert data["total_solucionadas"] == 1

    # Verificamos que las alertas no solucionadas estén correctamente clasificadas
    assert len(data["no_solucionadas"]) == 2
    assert data["no_solucionadas"][0]["paquete"] == "paquete1"
    assert data["no_solucionadas"][1]["paquete"] == "paquete2"

    # Verificamos que las alertas solucionadas estén correctamente clasificadas
    assert len(data["solucionadas"]) == 1
    assert data["solucionadas"][0]["paquete"] == "paquete3"


@patch("app.dependabots.dependabots_service.get_dependabot_alerts")
def test_obtener_dependabots_solucionados_y_no_solucionados_con_fechas(
    mock_get_dependabot_alerts
):
    "Test para filtrar dependabots por fechas"
    mock_get_dependabot_alerts.side_effect = lambda repo_owner, repo_name, state, start_date, end_date: [
        alerta for alerta in example_alertas if alerta["state"] == state and start_date <= alerta["created_at"] <= end_date
    ]

    # Establecemos un rango de fechas
    start_date = "2025-03-01T00:00:00Z"
    end_date = "2025-04-01T00:00:00Z"

    # Realizamos la solicitud GET al endpoint con fechas
    response = client.get(
        f"/v1/dependabots?repo_owner=usuario&repo_name=repositorio&start_date={start_date}&end_date={end_date}"
    )

    # Verificamos que la respuesta tenga el código de estado 200 OK
    assert response.status_code == 200

    # Verificamos que el contenido de la respuesta sea el esperado
    data = response.json()

    # Verificamos los totales de alertas
    assert data["total_alertas"] == 3
    assert data["total_no_solucionadas"] == 2
    assert data["total_solucionadas"] == 1

    # Verificamos que las alertas no solucionadas estén
    # correctamente clasificadas
    assert len(data["no_solucionadas"]) == 2
    assert data["no_solucionadas"][0]["paquete"] == "paquete1"
    assert data["no_solucionadas"][1]["paquete"] == "paquete2"

    # Verificamos que las alertas solucionadas estén correctamente clasificadas
    assert len(data["solucionadas"]) == 1
    assert data["solucionadas"][0]["paquete"] == "paquete3"


@patch("app.dependabots.dependabots_service.get_dependabot_alerts")
def test_obtener_dependabots_sin_alertas(mock_get_dependabot_alerts):
    """Test para el endpoint de dependabots sin alertas"""

    # Simulamos que no hay alertas para el repositorio
    mock_get_dependabot_alerts.return_value = []

    # Realizamos la solicitud GET al endpoint
    response = client.get(
        "/v1/dependabots?repo_owner=usuario&repo_name=repositorio"
    )

    # Verificamos que la respuesta tenga el código de estado 200 OK
    assert response.status_code == 200

    # Verificamos que el contenido de la respuesta sea el esperado
    data = response.json()

    # Verificamos que no haya alertas y que los totales sean cero
    assert data["total_alertas"] == 0
    assert data["total_no_solucionadas"] == 0
    assert data["total_solucionadas"] == 0
    assert data["no_solucionadas"] == []
    assert data["solucionadas"] == []

# Test cuando ocurre una excepción al obtener las alertas


@patch("app.dependabots.dependabots_service.get_dependabot_alerts")
def test_obtener_dependabots_error(mock_get_dependabot_alerts):
    """Test para el endpoint de dependabots con error"""

    # Simulamos un error en la API de dependabot
    mock_get_dependabot_alerts.side_effect = Exception(
        "Error en la API de GitHub")

    # Realizamos la solicitud GET al endpoint
    response = client.get(
        "/v1/dependabots?repo_owner=usuario&repo_name=repositorio"
    )

    # Verificamos que la respuesta tenga el código de estado 500 Internal
    # Server Error
    assert response.status_code == 500

    # Verificamos el detalle del error
    assert response.json() == {"detail": "Error en la API de GitHub"}
