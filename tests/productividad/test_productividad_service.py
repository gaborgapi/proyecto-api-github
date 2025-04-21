"""Esto es un test"""
import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
from app.productividad.productividad_service import (
    obtener_productividad_repositorio, obtener_productividad_por_repositorio
)


class TestProductividadRepositorio(unittest.TestCase):
    """Esta clase testea el servicio del modulo productividad"""

    def setUp(self):

        self.fecha_prueba = (
            datetime.now() - timedelta(weeks=1)).strftime(
                '%Y-%m-%dT%H:%M:%SZ'
        )

    @patch("app.productividad.productividad_service.get_commits")
    @patch("app.productividad.productividad_service.get_pull_requests")
    def test_obtener_productividad_repositorio_productivo(
        self,
        mock_get_prs,
        mock_get_commits
    ):
        """Prueba para un usuario productivo"""

        # Simulamos los commits
        mock_get_commits.return_value = [
            {
                "author": {"login": "usuario1"},
                "commit": {"author": {"date": self.fecha_prueba}}
            }
        ]

        # Simulamos los pull requests
        mock_get_prs.return_value = [
            {"user": {"login": "usuario1"}, "state": "open", "created_at":
                self.fecha_prueba
             },
            {"user": {"login": "usuario1"}, "state": "closed", "merged": True,
                "created_at": self.fecha_prueba
             }
        ]

        # Llamamos al servicio
        resultado = obtener_productividad_repositorio(
            "owner_test", "repo_test")

        # Verificamos que el usuario sea clasificado como productivo
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]['usuario'], "usuario1")
        self.assertEqual(resultado[0]['status'], "productivo")
        self.assertEqual(resultado[0]['commits'], 1)
        self.assertEqual(resultado[0]['pull_requests_abiertos'], 1)
        self.assertEqual(resultado[0]['pull_requests_no_fusionados'], 0)

    @patch("app.productividad.productividad_service.get_commits")
    @patch("app.productividad.productividad_service.get_pull_requests")
    def test_obtener_productividad_repositorio_improductivo(
        self,
        mock_get_prs,
        mock_get_commits
    ):
        """Prueba para un usuario improductivo"""

        # Simulamos los commits
        mock_get_commits.return_value = [
            {
                "author": {"login": "usuario2"},
                "commit": {"author": {"date": self.fecha_prueba}}
            }
        ]

        # Simulamos los pull requests
        mock_get_prs.return_value = [
            {"user": {"login": "usuario2"}, "state": "closed", "merged": False,
                "created_at": self.fecha_prueba
             },
            {"user": {"login": "usuario2"}, "state": "closed", "merged": False,
                "created_at": self.fecha_prueba
             },
            {"user": {"login": "usuario2"}, "state": "closed", "merged": False,
                "created_at": self.fecha_prueba
             },
            {"user": {"login": "usuario2"}, "state": "closed", "merged": False,
                "created_at": self.fecha_prueba
             },
            {"user": {"login": "usuario2"}, "state": "closed", "merged": False,
                "created_at": self.fecha_prueba
             }
        ]

        # Llamamos al servicio
        resultado = obtener_productividad_repositorio(
            "owner_test", "repo_test")

        # Verificamos que el usuario sea clasificado como improductivo
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]['usuario'], "usuario2")
        self.assertEqual(resultado[0]['status'], "improductivo")
        self.assertEqual(resultado[0]['commits'], 1)
        self.assertEqual(resultado[0]['pull_requests_abiertos'], 0)
        self.assertEqual(resultado[0]['pull_requests_no_fusionados'], 5)

    @patch("app.productividad.productividad_service.get_commits")
    @patch("app.productividad.productividad_service.get_pull_requests")
    def test_obtener_productividad_por_repositorio(
        self,
        mock_get_prs,
        mock_get_commits
    ):
        """Prueba para obtener la productividad de un repositorio completo"""

        # Simulamos los commits
        mock_get_commits.return_value = [
            {
                "author": {"login": "usuario1"},
                "commit": {"author": {"date": self.fecha_prueba}}
            },
            {
                "author": {"login": "usuario2"},
                "commit": {"author": {"date": self.fecha_prueba}}
            }
        ]

        # Simulamos los pull requests
        mock_get_prs.return_value = [
            {"user": {"login": "usuario1"}, "state": "open", "created_at":
                self.fecha_prueba
             },
            {"user": {"login": "usuario2"}, "state": "closed", "merged": False,
                "created_at": self.fecha_prueba
             },
            {"user": {"login": "usuario2"}, "state": "closed", "merged": False,
             "created_at": self.fecha_prueba
             },
            {"user": {"login": "usuario2"}, "state": "closed", "merged": False,
             "created_at": self.fecha_prueba
             },
            {"user": {"login": "usuario2"}, "state": "closed", "merged": False,
             "created_at": self.fecha_prueba
             },
            {"user": {"login": "usuario2"}, "state": "closed", "merged": False,
             "created_at": self.fecha_prueba
             },
            {"user": {"login": "usuario3"}, "state": "closed", "merged": False,
                "created_at": self.fecha_prueba},
            {"user": {"login": "usuario1"}, "state": "closed", "merged": True,
                "created_at": self.fecha_prueba}
        ]

        # Llamamos al servicio
        resultado = obtener_productividad_por_repositorio(
            "owner_test", "repo_test")

        # Verificamos que el resultado contenga los datos esperados para cada
        # usuario
        self.assertEqual(resultado['repo'], "repo_test")
        self.assertEqual(
            len(resultado['usuarios_productivos_improductivos']), 3)

        # Datos de verificación para cada usuario
        usuarios_info = [
            {"usuario": "usuario1", "status": "productivo", "commits": 1,
             "pull_requests_abiertos": 1, "pull_requests_no_fusionados": 0},
            {"usuario": "usuario2", "status": "improductivo", "commits": 1,
             "pull_requests_abiertos": 0, "pull_requests_no_fusionados": 5},
            {"usuario": "usuario3", "status": "improductivo", "commits": 0,
             "pull_requests_abiertos": 0, "pull_requests_no_fusionados": 1}
        ]

        # Ordenar ambos por nombre de usuario
        resultado_ordenado = sorted(
            resultado['usuarios_productivos_improductivos'],
            key=lambda x: x['usuario']
        )

        usuarios_info_ordenado = sorted(
            usuarios_info, key=lambda x: x['usuario']
        )

        # Verificación de cada usuario
        for i, usuario_data in enumerate(usuarios_info_ordenado):
            usuario = resultado_ordenado[i]
            self.assertEqual(usuario['usuario'], usuario_data['usuario'])
            self.assertEqual(usuario['status'], usuario_data['status'])
            self.assertEqual(usuario['commits'], usuario_data['commits'])
            self.assertEqual(usuario['pull_requests_abiertos'],
                             usuario_data['pull_requests_abiertos'])
            self.assertEqual(usuario['pull_requests_no_fusionados'],
                             usuario_data['pull_requests_no_fusionados'])


if __name__ == "__main__":
    unittest.main()
