"""Estas son pruebas unitarias."""


import unittest
from unittest.mock import patch, MagicMock
import requests
from app.utils.github_utils import (
    get_repos,
    get_commits,
    get_pull_requests,
    get_dependabot_alerts,
    GithubAPIException
)

TIMEOUT = 10  # Mismo valor de TIMEOUT que en la función original


class TestGithubUtils(unittest.TestCase):
    """Pruebas unitarias para las funciones
    que interactúan con la API de GitHub."""

    @patch("app.utils.github_utils.requests.get")
    def test_get_repos_success(self, mock_get):
        """Prueba de éxito para la función get_repos."""
        # Configuramos el mock de la respuesta
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "repo1"},
            {"name": "repo2"},
        ]  # Simulamos dos repositorios
        mock_get.return_value = mock_response

        # Llamamos a la función y verificamos que devuelve lo esperado
        repos = get_repos("usuario_prueba")
        self.assertEqual(repos, [{"name": "repo1"}, {"name": "repo2"}])

    @patch("app.utils.github_utils.requests.get")
    def test_get_repos_timeout(self, mock_get):
        """Prueba para un error de tiempo de espera (Timeout)."""
        # Simulamos un timeout
        mock_get.side_effect = requests.exceptions.Timeout
        with self.assertRaises(GithubAPIException):
            get_repos("usuario_prueba")

    @patch("app.utils.github_utils.requests.get")
    def test_get_repos_request_exception(self, mock_get):
        """Prueba para una excepción general en la
        solicitud
        (RequestException)."""
        # Simulamos una excepción de tipo RequestException
        mock_get.side_effect = requests.exceptions.RequestException(
            "Error de conexión")
        with self.assertRaises(GithubAPIException):
            get_repos("usuario_prueba")

    @patch("app.utils.github_utils.requests.get")
    def test_get_commits_success(self, mock_get):
        """Prueba de éxito para la función get_commits."""
        # Configuramos el mock de la respuesta
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"sha": "commit1"},
            {"sha": "commit2"},
        ]  # Simulamos dos commits
        mock_get.return_value = mock_response

        # Llamamos a la función y verificamos que devuelve lo esperado
        commits = get_commits("usuario_prueba", "repo_prueba")
        self.assertEqual(commits, [{"sha": "commit1"}, {"sha": "commit2"}])

    @patch("app.utils.github_utils.requests.get")
    def test_get_commits_timeout(self, mock_get):
        """Prueba para un error de
        tiempo de espera (Timeout) en get_commits."""
        # Simulamos un timeout
        mock_get.side_effect = requests.exceptions.Timeout
        with self.assertRaises(GithubAPIException):
            get_commits("usuario_prueba", "repo_prueba")

    @patch("app.utils.github_utils.requests.get")
    def test_get_commits_request_exception(self, mock_get):
        """Prueba para una excepción general en la solicitud
        (RequestException) en get_commits."""
        # Simulamos una excepción de tipo RequestException
        mock_get.side_effect = requests.exceptions.RequestException(
            "Error de conexión")
        with self.assertRaises(GithubAPIException):
            get_commits("usuario_prueba", "repo_prueba")

    @patch("app.utils.github_utils.requests.get")
    def test_get_pull_requests_success(self, mock_get):
        """Prueba de la función get_pull_requests
        cuando la respuesta es exitosa."""
        mock_prs = [
            {"id": 1, "state": "open", "title": "PR 1"},
            {"id": 2, "state": "closed", "title": "PR 2"},
            {"id": 3, "state": "closed", "title": "PR 3", "merged": True}
        ]
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_prs

        # Llamamos a la función para obtener los pull requests
        prs = get_pull_requests("user_test", "repo_test")

        # Verificamos que se han obtenido correctamente los PRs
        self.assertEqual(len(prs), 3)
        self.assertEqual(prs[0]["state"], "open")
        self.assertEqual(prs[1]["state"], "closed")
        self.assertTrue("merged" in prs[2])

    @patch("app.utils.github_utils.requests.get")
    def test_get_pull_requests_timeout(self, mock_get):
        """Prueba de la función get_pull_requests cuando ocurre un timeout."""
        # Simulamos que la petición a la API genera un timeout
        mock_get.side_effect = requests.exceptions.Timeout("Timeout error")

        # Verificamos que se lanza una excepción de tipo GithubAPIException
        with self.assertRaises(GithubAPIException):
            get_pull_requests("user_test", "repo_test")

    @patch("app.utils.github_utils.requests.get")
    def test_get_pull_requests_request_exception(self, mock_get):
        """Prueba de la función get_pull_requests
        cuando ocurre una RequestException."""
        # Simulamos un error genérico en la petición a la API
        mock_get.side_effect = requests.exceptions.RequestException(
            "Request error"
        )

        # Verificamos que se lanza una excepción de tipo GithubAPIException
        with self.assertRaises(GithubAPIException):
            get_pull_requests("user_test", "repo_test")

    @patch("app.utils.github_utils.requests.get")
    def test_get_dependabot_alerts_success(self, mock_get):
        """Prueba de éxito para la función get_dependabot_alerts."""
        # Simulamos la respuesta de la API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "number": 1,
                "state": "open",
                "dependency": {"package": {"name": "requests"}},
                "created_at": "2024-03-01T00:00:00Z"
            }
        ]
        mock_get.return_value = mock_response

        result = get_dependabot_alerts(
            repo_owner="test-org",
            repo_name="test-repo",
            state="open",
            start_date="2024-01-01",
            end_date="2024-04-01"
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["state"], "open")

        # Validamos que los parámetros hayan sido pasados correctamente
        called_params = mock_get.call_args[1]["params"]
        self.assertEqual(called_params["state"], "open")
        self.assertEqual(called_params["created"], "<=2024-04-01")

    @patch("app.utils.github_utils.requests.get")
    def test_get_dependabot_alerts_timeout(self, mock_get):
        """Prueba para un error de Timeout en get_dependabot_alerts."""
        mock_get.side_effect = requests.exceptions.Timeout

        with self.assertRaises(GithubAPIException):
            get_dependabot_alerts("org", "repo")

    @patch("app.utils.github_utils.requests.get")
    def test_get_dependabot_alerts_request_exception(self, mock_get):
        """Prueba para una excepción RequestException
        en get_dependabot_alerts."""
        mock_get.side_effect = requests.exceptions.RequestException(
            "Error general"
        )

        with self.assertRaises(GithubAPIException):
            get_dependabot_alerts("org", "repo")


if __name__ == "__main__":
    unittest.main()
