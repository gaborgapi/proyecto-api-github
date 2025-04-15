"""Esto es un test"""
import unittest
from unittest.mock import patch
from app.dependabots.dependabots_service import (
    obtener_dependabots_solucionados_y_no_solucionados
)


class TestDependabotService(unittest.TestCase):
    """Pruebas unitarias para el servicio de dependabot."""

    @patch("app.dependabots.dependabots_service.get_dependabot_alerts")
    def test_dependabots_solucionados_y_no_solucionados(self, mock_get_alerts):
        """
        Verifica que las alertas se clasifican correctamente entre solucionadas
        y no solucionadas, según su estado.
        """

        # Mock de las alertas en distintos estados
        mock_get_alerts.side_effect = [
            [  # Estado "open"
                {
                    "state": "open",
                    "dependency": {"package": {"name": "paquete1"}},
                    "security_advisory": {
                        "severity": "high", "ghsa_id": "GHSA-abc"
                    },
                    "created_at": "2024-01-01T00:00:00Z"
                }
            ],
            [  # Estado "dismissed"
                {
                    "state": "dismissed",
                    "dependency": {"package": {"name": "paquete2"}},
                    "security_advisory": {
                        "severity": "medium", "ghsa_id": "GHSA-def"
                    },
                    "created_at": "2024-01-02T00:00:00Z"
                }
            ],
            [  # Estado "fixed"
                {
                    "state": "fixed",
                    "dependency": {"package": {"name": "paquete3"}},
                    "security_advisory": {
                        "severity": "low", "ghsa_id": "GHSA-xyz"
                    },
                    "created_at": "2024-01-03T00:00:00Z"
                }
            ]
        ]

        # Llamar a la función bajo prueba
        result = obtener_dependabots_solucionados_y_no_solucionados(
            repo_owner="mi-org",
            repo_name="mi-repo",
            start_date="2024-01-01",
            end_date="2024-01-31"
        )

        # Aserciones principales
        self.assertEqual(result["total_alertas"], 3)  # Debe haber 3 alertas
        # 2 no solucionadas
        self.assertEqual(result["total_no_solucionadas"], 2)
        self.assertEqual(result["total_solucionadas"], 1)  # 1 solucionada

        # Verificar que las alertas no solucionadas tienen los campos correctos
        self.assertEqual(len(result["no_solucionadas"]), 2)
        self.assertEqual(result["no_solucionadas"][0]["paquete"], "paquete1")
        self.assertEqual(result["no_solucionadas"][1]["paquete"], "paquete2")

        # Verificar que la alerta solucionada tiene los campos correctos
        self.assertEqual(len(result["solucionadas"]), 1)
        self.assertEqual(result["solucionadas"][0]["paquete"], "paquete3")

        # Verificar que se devuelven los campos esperados para la tabla
        # o gráfica
        self.assertIn("paquete", result["solucionadas"][0])
        self.assertIn("paquete", result["no_solucionadas"][0])

    @patch("app.dependabots.dependabots_service.get_dependabot_alerts")
    def test_dependabots_sin_alertas(self, mock_get_alerts):
        """Debe manejar correctamente el caso sin alertas."""
        mock_get_alerts.side_effect = [[], [], []]  # No hay alertas

        result = obtener_dependabots_solucionados_y_no_solucionados(
            "mi-org", "mi-repo"
        )

        self.assertEqual(result["total_alertas"], 0)
        self.assertEqual(result["total_solucionadas"], 0)
        self.assertEqual(result["total_no_solucionadas"], 0)
        self.assertEqual(result["solucionadas"], [])
        self.assertEqual(result["no_solucionadas"], [])
