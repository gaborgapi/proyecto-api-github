"""Este es el service del modulo dependabots"""
from typing import Dict
from app.utils.github_utils import get_dependabot_alerts


def obtener_dependabots_solucionados_y_no_solucionados(
    repo_owner: str,
    repo_name: str,
    start_date=None,
    end_date=None
) -> Dict:
    """
    Devuelve las alertas de Dependabot clasificadas
    como solucionadas o no solucionadas
    con nombre del paquete, severidad, y enlace.

    - No solucionadas: alertas con estado "open" o "dismissed".
    - Solucionadas: alertas con estado "fixed".

    Además, incluye la opción de filtrar por repositorio y rango de fechas.
    """

    # Estados de las alertas que vamos a consultar
    estados = ["open", "dismissed", "fixed"]
    alertas = []

    # Obtener todas las alertas para los estados especificados
    for estado in estados:
        alertas_estado = get_dependabot_alerts(
            repo_owner, repo_name, state=estado,
            start_date=start_date, end_date=end_date
        )
        alertas.extend(alertas_estado)

    # Clasificar las alertas en solucionadas y no solucionadas
    no_solucionadas = []
    solucionadas = []

    for alerta in alertas:
        detalle_alerta = {
            "paquete": alerta.get(
                "dependency", {}
                ).get("package", {}).get("name"),
            "estado": alerta.get("state"),
            "severidad": alerta.get("security_advisory", {}).get("severity"),
            "creado_en": alerta.get("created_at")
            }

        # Clasificación de la alerta según su estado
        if alerta["state"] in ["open", "dismissed"]:
            no_solucionadas.append(detalle_alerta)
        elif alerta["state"] == "fixed":
            solucionadas.append(detalle_alerta)

    # Resumen con los totales
    return {
        "repositorio": repo_name,
        "rango_fechas": {"desde": start_date, "hasta": end_date},
        "total_alertas": len(alertas),
        "total_no_solucionadas": len(no_solucionadas),
        "total_solucionadas": len(solucionadas),
        "no_solucionadas": no_solucionadas,
        "solucionadas": solucionadas,
    }
