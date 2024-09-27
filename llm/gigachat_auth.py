import os
import aiohttp
import ssl
import logging
import base64
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GIGACHAT_CLIENT_ID = os.getenv('GIGACHAT_CLIENT_ID')
GIGACHAT_CLIENT_SECRET = os.getenv('GIGACHAT_CLIENT_SECRET')
COMBINED_CA_PATH = os.getenv('COMBINED_CA_PATH')

if not all([GIGACHAT_CLIENT_ID, GIGACHAT_CLIENT_SECRET, COMBINED_CA_PATH]):
    raise ValueError(
        "Необходимо указать GIGACHAT_CLIENT_ID, GIGACHAT_CLIENT_SECRET, COMBINED_CA_PATH в .env файле."
    )


def create_ssl_context():
    """
    Создает и возвращает SSL-контекст с загруженным сертификатом.
    """
    ssl_context = ssl.create_default_context()
    ssl_context.load_verify_locations(cafile=COMBINED_CA_PATH)
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    return ssl_context


async def get_access_token():
    """
    Получает токен доступа для API GigaChat с использованием аутентификации OAuth2.
    """
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    auth = base64.b64encode(f"{GIGACHAT_CLIENT_ID}:{GIGACHAT_CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "RqUID": "123e4567-e89b-12d3-a456-426655440000",  # Уникальный идентификатор запроса
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = "scope=GIGACHAT_API_PERS"
    ssl_context = create_ssl_context()

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data, ssl=ssl_context) as response:
            if response.status != 200:
                logger.error(f"Error getting access token: {response.status}")
                logger.error(f"Response: {await response.text()}")
                return None
            result = await response.json()
            return result.get('access_token')
