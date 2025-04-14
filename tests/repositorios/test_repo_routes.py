"""Estas son pruebas unitarias."""

from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@patch("app.repositorios.activity_service.get_pull_requests")
@patch("app.repositorios.activity_service.get_repos")
@patch("app.repositorios.activity_service.get_commits")
def test_get_repositorios(
    mock_get_commits,
    mock_get_repos,
    mock_get_prs
):
    """Prueba del endpoint de repositorios
    con mock de las funciones de servicio."""

    # Simulamos la respuesta de la función get_repos
    mock_get_repos.return_value = [
        {"name": "repo1",
            "html_url": "https://github.com/user/repo1"},
        {"name": "repo2",
            "html_url": "https://github.com/user/repo2"}
    ]

    # Simulamos las respuestas de get_commits
    mock_get_commits.side_effect = [
        [{"sha": "commit1"}],  # repo1 tiene commits recientes
        []  # repo2 no tiene commits recientes
    ]

    # Simulamos las respuestas de get_pull_requests (ahora usando todos los PRs)
    mock_get_prs.side_effect = [
        [  # PRs de repo1
            {"state": "open"},
            {"state": "closed", "merged": True},
            {"state": "closed", "merged": False}
        ],
        [  # PRs de repo2
            {"state": "open"},
            {"state": "open"}
        ]
    ]

    # Realizamos la solicitud GET al endpoint de repositorios
    response = client.get('/repositorios/usuario_prueba')

    # Verificamos que la respuesta sea exitosa
    assert response.status_code == 200

    data = response.json()
    assert "total_repositorios" in data
    assert "repositorios" in data
    assert len(data["repositorios"]) > 0

    # Verificamos que el repositorio 1 sea activo
    repos = data["repositorios"]
    assert repos[0]["status"] == "activo"
    assert repos[1]["status"] == "inactivo"

    # Verificamos la clasificación de los pull requests
    # Repo1 tiene PRs cerrados (2), y uno resuelto, debería ser "Repo Dinámico"
    assert repos[0]["pull_requests"]["estado_repo"] == "Repo Dinámico"

    assert repos[1]["pull_requests"]["estado_repo"] == "Repo Ineficiente"


@patch("app.repositorios.activity_service.get_repos")
@patch("app.repositorios.activity_service.get_commits")
def test_get_repositorios_error(mock_get_commits, mock_get_repos):
    """Prueba para un usuario que no
    existe o cuando ocurre un error en la API."""

    # Simulamos que get_repos lanza una excepción
    mock_get_repos.side_effect = Exception("Error al obtener los repositorios")

    # Realizamos la solicitud GET al endpoint de repositorios
    response = client.get('/repositorios/usuario_invalido')

    # Verificamos que la respuesta sea un error
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
