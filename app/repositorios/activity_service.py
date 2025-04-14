"""Servicio para clasificar repositorios en activos e inactivos."""

from app.utils.github_utils import (
    get_repos,
    get_commits,
    get_pull_requests,
    GithubAPIException
)


def clasificar_repositorios(usuario: str):
    """
    Clasifica los repositorios del usuario en activos e inactivos.
    Un repositorio es activo si tiene commits en los últimos 30 días.
    Además, evalúa el estado del repositorio basado en pull requests.
    """
    repos = get_repos(usuario)
    repos_con_estado = []

    for repo in repos:
        nombre = repo["name"]
        url = repo.get("html_url", "")

        # Iniciamos los datos del repositorio
        repo_data = {
            "repo": nombre,
            "url": url,
            "status": "",  # Aquí vamos a poner el estado
            "pull_requests": {
                "abiertos": 0,
                "cerrados": 0,
                "resueltos": 0,
                "estado_repo": ""
            }
        }

        try:
            # Obtenemos los commits del repositorio
            commits = get_commits(usuario, nombre)

            if commits:
                # Si tiene commits recientes, lo marcamos como activo
                repo_data["status"] = "activo"
            else:
                # Si no tiene commits, lo marcamos como inactivo
                repo_data["status"] = "inactivo"

            # Obtener los pull requests del repositorio
            prs = get_pull_requests(usuario, nombre)
            abiertos = 0
            cerrados = 0
            resueltos = 0

            for pr in prs:
                if pr['state'] == 'open':
                    abiertos += 1
                elif pr['state'] == 'closed':
                    cerrados += 1
                    if pr.get('merged', True):  # Si el PR fue mergeado
                        resueltos += 1

            repo_data["pull_requests"]["abiertos"] = abiertos
            repo_data["pull_requests"]["cerrados"] = cerrados
            repo_data["pull_requests"]["resueltos"] = resueltos

            # Calcular el porcentaje de PRs cerrados
            total_prs = abiertos + cerrados
            if total_prs > 0:
                porcentaje_cerrados = cerrados / total_prs * 100
                if porcentaje_cerrados > 80:
                    repo_data["pull_requests"]["estado_repo"] = "Repo Estable"
                elif 60 <= porcentaje_cerrados <= 80:
                    repo_data["pull_requests"]["estado_repo"] = "Repo Dinámico"
                else:
                    repo_data["pull_requests"][
                        "estado_repo"
                    ] = "Repo Ineficiente"
            else:
                repo_data["pull_requests"]["estado_repo"] = "Repo Sin PRs"

        except GithubAPIException:
            repo_data["status"] = "inactivo"

        # Añadimos el repositorio con su estado a la lista
        repos_con_estado.append(repo_data)

    return {
        "total": len(repos),  # Número total de repos
        "repos_con_estado": repos_con_estado  # Todos los repos con su estado
    }
