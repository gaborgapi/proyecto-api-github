import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from typing import Dict
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

ELASTIC_HOST = os.getenv("ELASTIC_HOST")
ELASTIC_PORT = int(os.getenv("ELASTIC_PORT"))
ELASTIC_SCHEME = os.getenv("ELASTIC_SCHEME")
ELASTIC_USER = os.getenv("ELASTIC_USER")
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")

# Conexión a Elasticsearch
es = Elasticsearch(
    [{'host': ELASTIC_HOST, 'port': ELASTIC_PORT, 'scheme': ELASTIC_SCHEME}],
    basic_auth=(ELASTIC_USER, ELASTIC_PASSWORD), #Establecer la autenticación básica
)  

if es.ping():
    logger.info("Conexión exitosa con Elasticsearch")
else:
    logger.error("Error al conectar con Elasticsearch")


# Función para indexar un documento
async def indexar_documento_elasticsearch(index_name: str, documento: Dict):
    """
    Envía un documento al índice especificado en Elasticsearch de manera asincrónica.
    
    Args:
        index_name (str): Nombre del índice en Elasticsearch.
        documento (dict): Documento a indexar.
    
    Returns:
        dict: Respuesta de Elasticsearch con los detalles de la operación.
    """
    try:
        # Agregar un timestamp al documento
        documento["timestamp"] = datetime.now(timezone.utc).isoformat()

        # Indexar el documento
        response = es.index(index=index_name, document=documento)

        # Validar la respuesta
        if response.get("result") in ["created", "updated"]:
            logger.info(f"Documento indexado correctamente: {response}")
        else:
            logger.warning(f"Documento no indexado correctamente: {response}")

        return response

    except Exception as e:
        logger.error(f"Error al indexar el documento en Elasticsearch: {e}", exc_info=True)
        return {"error": str(e)}