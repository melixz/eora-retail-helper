import aiohttp
import html
import re
import logging
from collections import Counter
from utils.gigachat_auth import get_access_token  # Импортируем функцию получения токена
from utils.ssl_utils import create_ssl_context  # Импортируем функцию для создания SSL контекста

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Функция для генерации ответа с гиперссылками
async def generate_answer(question, context_with_urls):
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    access_token = await get_access_token()
    if not access_token:
        return "Не удалось получить доступ к сервису."

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    context_parts = [content for content, url in context_with_urls]
    context = "\n\n".join(context_parts)

    if not context:
        return "Ошибка: контекст пуст или некорректен."

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
                answer = result["choices"][0]["message"]["content"]

                answer = html.escape(answer)
                sentences = re.split(r'(?<=[.!?])\s+', answer)

                context_urls = [url for content, url in context_with_urls]

                def extract_keywords(text):
                    words = re.findall(r'\w+', text.lower())
                    return Counter(words)

                new_sentences = []
                for idx, sentence in enumerate(sentences):
                    max_similarity = 0
                    best_url = None
                    sentence_keywords = extract_keywords(sentence)
                    for content, url in context_with_urls:
                        content_keywords = extract_keywords(content)
                        common_words = sentence_keywords & content_keywords
                        similarity = sum(common_words.values())
                        if similarity > max_similarity:
                            max_similarity = similarity
                            best_url = url
                    if best_url and max_similarity > 0:
                        escaped_url = html.escape(best_url, quote=True)
                        sentence = f'{sentence} <a href="{escaped_url}">[{idx + 1}]</a>'
                    new_sentences.append(sentence)

                answer_with_links = ' '.join(new_sentences)

                return answer_with_links

        except aiohttp.ClientConnectorError as e:
            logger.error(f"Connection error: {e}")
            return "Извините, не удалось подключиться к сервису обработки запросов."
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
            return "Извините, произошла ошибка при обработке вашего запроса."
