"""Esta es la configuración que carga las variables de entorno."""
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()


class Config:
    """Clase de configuración que carga las variables de entorno."""
    GITHUB_API_URL = os.getenv("GITHUB_API_URL")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
