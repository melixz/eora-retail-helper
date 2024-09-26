import os
import aiohttp
import ssl
import logging
import base64
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Получение данных из переменных окружения
GIGACHAT_CLIENT_ID = os.getenv('GIGACHAT_CLIENT_ID')
GIGACHAT_CLIENT_SECRET = os.getenv('GIGACHAT_CLIENT_SECRET')
COMBINED_CA_PATH = os.getenv('COMBINED_CA_PATH')

# Проверка наличия необходимых данных
if not all([GIGACHAT_CLIENT_ID, GIGACHAT_CLIENT_SECRET, COMBINED_CA_PATH]):
    raise ValueError(
        "Необходимо указать GIGACHAT_CLIENT_ID, GIGACHAT_CLIENT_SECRET, COMBINED_CA_PATH в .env файле."
    )


# Функция для создания SSL контекста
def create_ssl_context():
    ssl_context = ssl.create_default_context()
    ssl_context.load_verify_locations(cafile=COMBINED_CA_PATH)
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    return ssl_context


# Функция для получения токена доступа
async def get_access_token():
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


# Асинхронная функция для отправки запроса в GigaChat API
async def generate_answer(question, context):
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    access_token = await get_access_token()
    if not access_token:
        return "Не удалось получить доступ к сервису."

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "GigaChat",
        "messages": [
            {"role": "system", "content": f"Контекст: {context}"},
            {"role": "user", "content": question}
        ]
    }

    ssl_context = create_ssl_context()

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, headers=headers, ssl=ssl_context) as response:
                if response.status != 200:
                    logger.error(f"Error: Received status code {response.status} from GigaChat API")
                    text = await response.text()
                    logger.error(f"Response: {text}")
                    return "Извините, произошла ошибка при обработке вашего запроса."
                result = await response.json()
                logger.info(f"GigaChat API response: {result}")
                return result["choices"][0]["message"]["content"]
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Connection error: {e}")
            return "Извините, не удалось подключиться к сервису обработки запросов."
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
            return "Извините, произошла ошибка при обработке вашего запроса."


# Пример использования функции
if __name__ == "__main__":
    import asyncio


    async def main():
        question = "Что такое искусственный интеллект?"
        context = "Вы - эксперт по искусственному интеллекту."
        answer = await generate_answer(question, context)
        print(f"Вопрос: {question}")
        print(f"Ответ: {answer}")


    asyncio.run(main())
