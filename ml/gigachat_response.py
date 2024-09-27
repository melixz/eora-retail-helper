import aiohttp
import html
import re
import logging
from collections import Counter
from ml.gigachat_auth import get_access_token  # Импортируем функцию получения токена
from utils.ssl_utils import create_ssl_context  # Импортируем функцию для создания SSL контекста

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Функция для генерации ответа с гиперссылками
async def generate_answer(question, context_with_urls, used_urls):
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
        "Ты — помощник по продуктам компании EORA. "
        "Отвечай на вопросы пользователей только на основе предоставленного контекста. "
        "Когда тебя спрашивают о дополнительных примерах (такие как 'еще', 'а еще?'), всегда давай 2 новых примера услуг и связанных с ними ссылок. "
        "Ты не должен добавлять информацию, отсутствующую в контексте. "
        "Не повторяй уже показанные примеры. "
        "Сохраняй последовательность и структуру, не больше 3 примеров за ответ."
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

                # Сюда будем сохранять ссылки, которые еще не использовались
                new_urls = []

                def extract_keywords(text):
                    words = re.findall(r'\w+', text.lower())
                    return Counter(words)

                new_sentences = []
                for idx, sentence in enumerate(sentences):
                    if len(new_urls) >= 3:  # Ограничиваем количество ссылок до 3
                        break

                    max_similarity = 0
                    best_url = None
                    sentence_keywords = extract_keywords(sentence)
                    for content, url in context_with_urls:
                        content_keywords = extract_keywords(content)
                        common_words = sentence_keywords & content_keywords
                        similarity = sum(common_words.values())
                        if similarity > max_similarity and url not in used_urls:
                            max_similarity = similarity
                            best_url = url

                    if best_url and max_similarity > 0 and best_url not in new_urls:
                        escaped_url = html.escape(best_url, quote=True)
                        sentence = f'{sentence} <a href="{escaped_url}">[{len(new_urls) + 1}]</a>'
                        new_urls.append(best_url)
                    new_sentences.append(sentence)

                answer_with_links = ' '.join(new_sentences)

                return answer_with_links

        except aiohttp.ClientConnectorError as e:
            logger.error(f"Connection error: {e}")
            return "Извините, не удалось подключиться к сервису обработки запросов."
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
            return "Извините, произошла ошибка при обработке вашего запроса."
