"""Estas son pruebas unitarias."""
import unittest
from unittest.mock import patch
from app.utils.github_utils import GithubAPIException
from app.repositorios.activity_service import clasificar_repositorios


class TestClasificarRepositorios(unittest.TestCase):
    """Pruebas unitarias para la función clasificar_repositorios."""

    @patch("app.repositorios.activity_service.get_pull_requests")
    @patch("app.repositorios.activity_service.get_repos")
    @patch("app.repositorios.activity_service.get_commits")
    def test_clasificar_repositorios_activos_inactivos(
        self,
        mock_get_commits,
        mock_get_repos,
        mock_get_prs
    ):
        """Prueba para clasificar repositorios en activos e inactivos."""

        # Simulamos que la función get_repos devuelve una lista de repositorios
        mock_get_repos.return_value = [
            {"name": "repo1",
                "html_url": "https://github.com/user/repo1"},
            {"name": "repo2",
                "html_url": "https://github.com/user/repo2"},
            {"name": "repo3",
                "html_url": "https://github.com/user/repo3"},
        ]

        # Simulamos las respuestas de get_commits
        mock_get_commits.side_effect = [
            [{"sha": "commit1"}],  # repo1 tiene commits recientes
            [],  # repo2 no tiene commits recientes
            [{"sha": "commit3"}],  # repo3: activo

        ]

        mock_get_prs.side_effect = [
            [  # repo1 → Repo Dinámico (2 cerrados, 1 abierto) = 66.6%
                {"state": "open"},
                {"state": "closed", "merged": True},
                {"state": "closed", "merged": False},
            ],
            [  # repo2 → Repo Ineficiente (2 abiertos, 0 cerrados) = 0%
                {"state": "open"},
                {"state": "open"},
            ],
            [  # repo3 → Repo Estable (5 cerrados, 1 abierto) > 80%
                {"state": "closed", "merged": True},
                {"state": "closed", "merged": False},
                {"state": "closed", "merged": True},
                {"state": "closed", "merged": True},
                {"state": "closed", "merged": True},
                {"state": "open"},
            ],
        ]

        # Llamamos a la función que estamos probando
        resultado = clasificar_repositorios("usuario_prueba")

        # Verificamos que la función retorna el número correcto de repos
        self.assertEqual(resultado["total"], 3)
        # Verificamos los repos con su estado
        repos = resultado["repos_con_estado"]

        # 🔹 Repo1: activo, dinámico
        self.assertEqual(repos[0]["repo"], "repo1")
        self.assertEqual(repos[0]["status"], "activo")
        self.assertEqual(repos[0]["pull_requests"]["abiertos"], 1)
        self.assertEqual(repos[0]["pull_requests"]["cerrados"], 2)
        self.assertEqual(repos[0]["pull_requests"]["resueltos"], 1)
        self.assertEqual(
            repos[0]["pull_requests"]["estado_repo"],
            "Repo Dinámico"
        )

        # 🔹 Repo2: inactivo, ineficiente
        self.assertEqual(repos[1]["repo"], "repo2")
        self.assertEqual(repos[1]["status"], "inactivo")
        self.assertEqual(repos[1]["pull_requests"]["abiertos"], 2)
        self.assertEqual(repos[1]["pull_requests"]["cerrados"], 0)
        self.assertEqual(repos[1]["pull_requests"]["resueltos"], 0)
        self.assertEqual(
            repos[1]["pull_requests"]["estado_repo"],
            "Repo Ineficiente")

        # 🔹 Repo3: activo, estable
        self.assertEqual(repos[2]["repo"], "repo3")
        self.assertEqual(repos[2]["status"], "activo")
        self.assertEqual(repos[2]["pull_requests"]["abiertos"], 1)
        self.assertEqual(repos[2]["pull_requests"]["cerrados"], 5)
        self.assertEqual(repos[2]["pull_requests"]["resueltos"], 4)
        self.assertEqual(
            repos[2]["pull_requests"]["estado_repo"], "Repo Estable"
        )

    @patch("app.repositorios.activity_service.get_pull_requests")
    @patch("app.repositorios.activity_service.get_repos")
    @patch("app.repositorios.activity_service.get_commits")
    def test_clasificar_repositorios_con_error(
        self,
        mock_get_commits,
        mock_get_repos,
        mock_get_prs
    ):
        """Prueba para cuando get_commits lanza una
        excepción y se clasifica como inactivo."""

        # Simulamos que la función get_repos devuelve una lista de repositorios
        mock_get_repos.return_value = [
            {"name": "repo1",
                "html_url": "https://github.com/user/repo1"},
            {"name": "repo2",
                "html_url": "https://github.com/user/repo2"}
        ]

        mock_get_commits.side_effect = [
            [{"sha": "commit1"}],  # repo1 tiene commits recientes
            # repo2 lanza una excepción
            GithubAPIException("Error al obtener commits")
        ]

        # Se mockea también get_pull_requests (aunque no sea el foco del test)
        mock_get_prs.side_effect = [
            [],  # PRs de repo1
            []   # PRs de repo2
        ]
        # Llamamos a la función que estamos probando
        resultado = clasificar_repositorios("usuario_prueba")

        # Verificamos que la función retorna el número correcto de repos
        self.assertEqual(resultado["total"], 2)

        # Verificamos los repos con su estado
        repos = resultado["repos_con_estado"]
        self.assertEqual(repos[0]["repo"], "repo1")
        self.assertEqual(repos[0]["status"], "activo")
        self.assertEqual(repos[1]["repo"], "repo2")
        self.assertEqual(repos[1]["status"], "inactivo")

    @patch("app.repositorios.activity_service.get_pull_requests")
    @patch("app.repositorios.activity_service.get_repos")
    @patch("app.repositorios.activity_service.get_commits")
    def test_clasificar_repositorios_sin_commits(
        self,
        mock_get_commits,
        mock_get_repos,
        mock_get_prs
    ):
        """Prueba para cuando get_commits no encuentra
        commits en el último mes y se clasifica como inactivo."""

        # Simulamos que la función get_repos devuelve una lista de repositorios
        mock_get_repos.return_value = [
            {"name": "repo1",
                "html_url": "https://github.com/user/repo1"},
            {"name": "repo2",
                "html_url": "https://github.com/user/repo2"}
        ]

        mock_get_commits.side_effect = [
            [],  # repo1 no tiene commits
            []   # repo2 no tiene commits
        ]

        # Simulamos los PRs vacíos
        mock_get_prs.side_effect = [
            [],  # PRs repo1
            []   # PRs repo2
        ]

        # Llamamos a la función que estamos probando
        resultado = clasificar_repositorios("usuario_prueba")

        # Verificamos que la función retorna el número correcto de repos
        self.assertEqual(resultado["total"], 2)

        # Verificamos los repos con su estado
        repos = resultado["repos_con_estado"]
        self.assertEqual(repos[0]["repo"], "repo1")
        self.assertEqual(repos[0]["status"], "inactivo")
        self.assertEqual(repos[1]["repo"], "repo2")
        self.assertEqual(repos[1]["status"], "inactivo")


if __name__ == "__main__":
    unittest.main()
