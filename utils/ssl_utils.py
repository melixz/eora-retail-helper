import ssl
import os
import logging

# Получение данных из переменных окружения
COMBINED_CA_PATH = os.getenv('COMBINED_CA_PATH')

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Функция для создания SSL контекста
def create_ssl_context():
    ssl_context = ssl.create_default_context()
    ssl_context.load_verify_locations(cafile=COMBINED_CA_PATH)
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    logger.info(f"SSL context created: {ssl_context}")
    logger.info(f"Combined CA path: {COMBINED_CA_PATH}")
    return ssl_context
