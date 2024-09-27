import os
import aiohttp
import ssl
import logging
import base64
import html
import re
from dotenv import load_dotenv
from collections import Counter

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
    raise ValueError("Необходимо указать GIGACHAT_CLIENT_ID, GIGACHAT_CLIENT_SECRET, COMBINED_CA_PATH в .env файле.")


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
        "RqUID": "123e4567-e89b-12d3-a456-426655440000",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = "scope=GIGACHAT_API_PERS"

    ssl_context = create_ssl_context()
    logger.info(f"SSL context created: {ssl_context}")
    logger.info(f"Combined CA path: {COMBINED_CA_PATH}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, data=data, ssl=ssl_context) as response:
                if response.status != 200:
                    logger.error(f"Error getting access token: {response.status}")
                    text = await response.text()
                    logger.error(f"Response: {text}")
                    return None
                result = await response.json()
                return result.get('access_token')
        except Exception as e:
            logger.error(f"Exception when getting access token: {e}")
            return None


# Новая улучшенная функция для генерации ответа с гиперссылками в тексте
async def generate_answer(question, context_with_urls):
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    access_token = await get_access_token()
    if not access_token:
        return "Не удалось получить доступ к сервису."

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Формируем контекст для LLM
    context_parts = [content for content, url in context_with_urls]
    context = "\n\n".join(context_parts)

    if not context:
        return "Ошибка: контекст пуст или некорректен."

    # Формируем системное сообщение для LLM
    system_message = (
        "Ты — помощник по продуктам компании EORA. Используя только предоставленный контекст ниже, ответь на вопрос пользователя. "
        "Ты не должен добавлять информацию, отсутствующую в контексте. "
        "Не вставляй ссылки или номера источников в ответе; просто предоставь информативный ответ."
    )

    payload = {
        "model": "GigaChat",
        "messages": [
            {"role": "system", "content": f"{system_message}\n\nКонтекст:\n{context}"},
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

                # Получаем ответ от LLM
                answer = result["choices"][0]["message"]["content"]

                # Экранируем специальные символы в ответе
                answer = html.escape(answer)

                # Разбиваем ответ на предложения
                sentences = re.split(r'(?<=[.!?])\s+', answer)

                # Подготавливаем контент и URL из контекста
                context_urls = [url for content, url in context_with_urls]

                # Функция для нахождения ключевых слов в контексте
                def extract_keywords(text):
                    words = re.findall(r'\w+', text.lower())
                    return Counter(words)

                # Улучшенная логика привязки предложений к контекстам
                new_sentences = []
                for idx, sentence in enumerate(sentences):
                    max_similarity = 0
                    best_url = None
                    sentence_keywords = extract_keywords(sentence)  # Извлекаем ключевые слова из предложения
                    for content, url in context_with_urls:
                        content_keywords = extract_keywords(content)  # Извлекаем ключевые слова из контента
                        common_words = sentence_keywords & content_keywords
                        similarity = sum(common_words.values())  # Суммируем количество совпадающих ключевых слов
                        if similarity > max_similarity:
                            max_similarity = similarity
                            best_url = url
                    if best_url and max_similarity > 0:
                        # Добавляем гиперссылку вместо номера
                        escaped_url = html.escape(best_url, quote=True)
                        sentence = f'{sentence} <a href="{escaped_url}">[{idx + 1}]</a>'
                    new_sentences.append(sentence)

                # Воссоздаем ответ с гиперссылками
                answer_with_links = ' '.join(new_sentences)

                return answer_with_links

        except aiohttp.ClientConnectorError as e:
            logger.error(f"Connection error: {e}")
            return "Извините, не удалось подключиться к сервису обработки запросов."
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
            return "Извините, произошла ошибка при обработке вашего запроса."


async def check_gigachat_credentials():
    try:
        ssl_context = create_ssl_context()
        token = await get_access_token()
        return token is not None
    except Exception as e:
        logger.error(f"Error checking GigaChat credentials: {e}")
        return False


if __name__ == "__main__":
    import asyncio


    async def main():
        question = "Что такое искусственный интеллект?"
        context = "Вы - эксперт по искусственному интеллекту."
        answer = await generate_answer(question, context)
        print(f"Вопрос: {question}")
        print(f"Ответ: {answer}")


    asyncio.run(main())
