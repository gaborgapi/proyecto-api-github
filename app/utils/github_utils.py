"""Este es el util que hace las peticiones a la api de GitHub."""

from datetime import datetime, timedelta
import requests
from config import Config  # Importamos la clase Config de config.py

TIMEOUT = 10


class GithubAPIException(Exception):
    """Excepción personalizada para errores de la API de GitHub."""


def get_repos(usuario: str):
    """Obtiene los repositorios de un usuario u organización de GitHub."""
    url = f"{Config.GITHUB_API_URL}/users/{usuario}/repos"
    headers = {"Authorization": f"Bearer {Config.GITHUB_TOKEN}"}
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout as e:
        raise GithubAPIException(
            f"La solicitud a {url}"
            + f"ha superado el tiempo de espera de {TIMEOUT} segundos."
        ) from e
    except requests.exceptions.RequestException as e:
        raise GithubAPIException(f"Error en la solicitud a {url}: {e}") from e


def get_commits(repo_owner: str, repo_name: str):
    """Obtiene los commits recientes de un repositorio."""
    url = f"{Config.GITHUB_API_URL}/repos/{repo_owner}/{repo_name}/commits"
    headers = {"Authorization": f"Bearer {Config.GITHUB_TOKEN}"}
    params = {"since": (datetime.now() - timedelta(days=30)).isoformat()}
    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout as e:
        raise GithubAPIException(
            f"La solicitud a {url}"
            + f"ha superado el tiempo de espera de {TIMEOUT} segundos."
        ) from e
    except requests.exceptions.RequestException as e:
        raise GithubAPIException(f"Error en la solicitud a {url}: {e}") from e


def get_pull_requests(repo_owner: str, repo_name: str):
    """Obtiene los pull requests de un repositorio de GitHub."""
    url = f"{Config.GITHUB_API_URL}/repos/{repo_owner}/{repo_name}/pulls?state=all"
    headers = {"Authorization": f"Bearer {Config.GITHUB_TOKEN}"}
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout as e:
        raise GithubAPIException(
            f"La solicitud a {url}"
            + f"ha superado el tiempo de espera de {TIMEOUT} segundos."
        ) from e
    except requests.exceptions.RequestException as e:
        raise GithubAPIException(f"Error en la solicitud a {url}: {e}") from e


def get_dependabot_alerts(
        repo_owner: str,
        repo_name: str,
        state="open",
        start_date=None,
        end_date=None):
    """
    Obtiene las alertas de seguridad de Dependabot para un repositorio,
    con un filtro opcional por rango de fechas de creación.
    """
    url = (
        f"{Config.GITHUB_API_URL}/repos/"
        f"{repo_owner}/{repo_name}/dependabot/alerts"
    )
    headers = {
        "Authorization": f"Bearer {Config.GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    # Parámetros adicionales para filtrar por fechas si se proporcionan
    params = {"state": state}
    if start_date:
        params["created"] = f">={start_date}"
    if end_date:
        params["created"] = f"<={end_date}"

    try:
        response = requests.get(
            url, headers=headers, params=params, timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout as e:
        raise GithubAPIException(
            f"La solicitud a {url} superó los {TIMEOUT} segundos."
        ) from e
    except requests.exceptions.RequestException as e:
        raise GithubAPIException(
            f"Error en la solicitud a {url}: {e}"
        ) from e
