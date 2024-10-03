import ssl
import os
import logging

COMBINED_CA_PATH = os.getenv("COMBINED_CA_PATH")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_ssl_context():
    """
    Создает и возвращает SSL контекст для подключения к защищенным API.
    """
    ssl_context = ssl.create_default_context()
    ssl_context.load_verify_locations(cafile=COMBINED_CA_PATH)
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    logger.info(f"SSL контекст создан с использованием {COMBINED_CA_PATH}")
    return ssl_context
