import aiohttp
import html
import re
import logging
from collections import Counter
from llm.gigachat_auth import get_access_token
from utils.ssl_utils import create_ssl_context

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Глобальные переменные для отслеживания использованных ссылок
used_urls_global = set()


def remove_extra_digits_around_links(formatted_answer):
    """
    Удаляет лишние цифры перед и после гиперссылок, сохраняя корректные ссылки с нумерацией внутри.
    """
    formatted_answer = re.sub(r'\d+\s*(<a href="[^"]+">\[\d+\]</a>)', r'\1', formatted_answer)
    return formatted_answer


def validate_formatting(text):
    """
    Проверяет, чтобы после каждого номера услуги текст начинался с заглавной буквы и не было лишних цифр перед ссылками.
    """
    # Удаляем лишние пробелы перед и после ссылок
    text = re.sub(r'\s*\[\d+\]\s*', lambda match: match.group().strip(), text)
    # Преобразуем текст после номеров 1, 2, 3 в заглавную букву
    text = re.sub(r'(\d\.\s*)([a-zа-яё])', lambda m: m.group(1) + m.group(2).upper(), text)
    return text


async def generate_answer(question, context_with_urls, used_urls):
    global used_urls_global
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
        "Ты — виртуальный помощник компании EORA. "
        "Твоя задача — предлагать услуги компании для ритейлеров, основываясь на имеющемся контексте. "
        "Ограничь количество услуг до трех в одном ответе."
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
                    logger.error(f"Error: Received status code {response.status}")
                    text = await response.text()
                    logger.error(f"Response: {text}")
                    return "Извините, произошла ошибка при обработке вашего запроса."
                result = await response.json()
                answer = result["choices"][0]["message"]["content"]

                # Экранируем специальные HTML-символы
                answer = html.escape(answer)
                sentences = re.split(r'(?<=[.!?])\s+', answer)

                new_urls = []

                def extract_keywords(text):
                    words = re.findall(r'\w+', text.lower())
                    return Counter(words)

                new_sentences = []
                for idx, sentence in enumerate(sentences):
                    if len(new_urls) >= 3:
                        break

                    max_similarity = 0
                    best_url = None
                    sentence_keywords = extract_keywords(sentence)

                    for content, url in context_with_urls:
                        content_keywords = extract_keywords(content)
                        common_words = sentence_keywords & content_keywords
                        similarity = sum(common_words.values())
                        if similarity > max_similarity and url not in used_urls_global:
                            max_similarity = similarity
                            best_url = url

                    if best_url and max_similarity > 0 and best_url not in new_urls:
                        escaped_url = html.escape(best_url, quote=True)
                        # Вставляем ссылку только один раз
                        if f'<code>[{len(new_urls) + 1}]</code>' not in sentence:
                            sentence = f'{sentence} <code>[{len(new_urls) + 1}]</code>'
                        new_urls.append((len(new_urls) + 1, escaped_url))
                        used_urls_global.add(best_url)

                    new_sentences.append(sentence)

                formatted_answer = ' '.join(new_sentences)

                # Удаляем лишние цифры перед и после гиперссылок
                formatted_answer = remove_extra_digits_around_links(formatted_answer)

                # Применяем валидацию форматирования текста
                formatted_answer = validate_formatting(formatted_answer)

                # Удаляем заголовки, оформленные жирным текстом
                formatted_answer = re.sub(r'\*\*(.*?)\*\*', r'\1', formatted_answer)
                formatted_answer = re.sub(r'<b>(.*?)</b>', r'\1', formatted_answer)

                for i, url in new_urls:
                    formatted_answer = formatted_answer.replace(f'<code>[{i}]</code>', f'<a href="{url}">[{i}]</a>')

                return formatted_answer

        except aiohttp.ClientConnectorError as e:
            logger.error(f"Connection error: {e}")
            return "Извините, не удалось подключиться к сервису обработки запросов."
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
            return "Извините, произошла ошибка при обработке вашего запроса."
