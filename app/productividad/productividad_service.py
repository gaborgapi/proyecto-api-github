"""Este es el servicio del modulo productividad"""
from datetime import datetime, timedelta
import sys

sys.path.append('.')
from app.utils.github_utils import get_commits, get_pull_requests
from app.elasticsearch.conexion_elasticsearch import indexar_documento_elasticsearch

# Definimos los umbrales para clasificar la productividad
COMMIT_THRESHOLD = 1  # Al menos 1 commit en las últimas dos semanas
PR_THRESHOLD = 1  # Al menos 1 PR abierto en las últimas dos semanas


async def obtener_productividad_repositorio(repo_owner: str, repo_name: str):
    """Obtiene y clasifica la productividad de
    los usuarios de un repositorio específico."""

    # Obtener los commits y pull requests de este repositorio
    commits = await get_commits(repo_owner, repo_name)
    prs = await get_pull_requests(repo_owner, repo_name)

    # Definimos el rango de fechas para las últimas dos semanas
    fecha_limite_2_semanas = datetime.now() - timedelta(weeks=2)

    # Identificamos a los usuarios que han contribuido (por commit o PR)
    usuarios = set()

    # Agregar usuarios de los commits
    for commit in commits:
        usuario = commit['author']['login']
        usuarios.add(usuario)

    # Agregar usuarios de los pull requests
    for pr in prs:
        if pr['user']:
            usuario = pr['user']['login']
            usuarios.add(usuario)

    # Clasificamos la productividad de cada usuario
    productividad = []  # Lista para almacenar los resultados

    for usuario in usuarios:

        # Filtramos todos los commits de los últimos 30 días
        commits_recientes = [
            commit for commit in commits
            if commit['author']['login'] == usuario
            and datetime.strptime(
                commit['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ'
            ) > datetime.now() - timedelta(days=30)
        ]

        # Filtramos los commits recientes solo de las últimas dos semanas
        commits_en_ultimas_2_semanas = [
            commit for commit in commits_recientes
            if datetime.strptime(
                commit['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ'
            ) > fecha_limite_2_semanas
        ]

        # Filtrar los pull requests abiertos del
        # usuario en las últimas dos semanas
        pr_abiertos = [
            pr for pr in prs
            if pr['user']['login'] == usuario and pr['state'] == 'open' and
            datetime.strptime(pr['created_at'],
                              '%Y-%m-%dT%H:%M:%SZ') > fecha_limite_2_semanas
        ]

        # Filtrar los pull requests cerrados no fusionados del
        # usuario en las últimas dos semanas
        pr_no_fusionados_cerrados = [
            pr for pr in prs
            if pr['user']['login'] == usuario and pr['state'] == 'closed' and
            not pr.get('merged', False) and datetime.strptime(
                pr['created_at'], '%Y-%m-%dT%H:%M:%SZ'
            ) > fecha_limite_2_semanas
        ]

        # Definimos el estado del usuario para este repositorio
        if (len(commits_recientes) >= COMMIT_THRESHOLD and
                len(pr_abiertos) >= PR_THRESHOLD):
            status = "productivo"
        else:
            status = "improductivo"

        # Agregamos los datos del usuario a la lista de productividad
        productividad.append({
            "usuario": usuario,
            "status": status,
            "commits": len(commits_en_ultimas_2_semanas),
            "pull_requests_abiertos": len(pr_abiertos),
            "pull_requests_no_fusionados": len(pr_no_fusionados_cerrados)
        })

    return productividad


async def obtener_productividad_por_repositorio(repo_owner: str, repo_name: str):
    """Obtiene la productividad de los usuarios de un repositorio
    y retorna los datos en formato JSON."""

    productividad = await obtener_productividad_repositorio(repo_owner, repo_name)

    #Indexación de los documentos en Elasticsearch
    for usuario_data in productividad:
        documento = {
            "repo": repo_name,
            "usuario": usuario_data["usuario"],
            "status": usuario_data["status"],
            "commits": usuario_data["commits"],
            "pull_requests_abiertos": usuario_data["pull_requests_abiertos"],
            "pull_requests_no_fusionados": usuario_data["pull_requests_no_fusionados"]
        }

        # Indexar el documento en Elasticsearch
        response = await indexar_documento_elasticsearch("github_productividad_usuarios", documento)

        # Verificar y mostrar el resultado en consola
        if "result" in response and response["result"] == "created":
            print(f"Documento para el usuario {usuario_data['usuario']} indexado correctamente.")
        else:
            print(f"Error al indexar el documento para el usuario {usuario_data['usuario']}: {response}")

    # Devolvemos la estructura organizada para el frontend
    return {
        "repo": repo_name,
        "usuarios_productivos_improductivos": productividad
    }
