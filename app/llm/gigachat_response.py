import aiohttp
import html
import logging
from app.llm.gigachat_auth import get_access_token
from app.utils.ssl_utils import create_ssl_context
from app.llm.gigachat_formatting import format_answer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

used_urls_global = set()


async def generate_answer(question, context_with_urls, used_urls):
    global used_urls_global
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    access_token = await get_access_token()

    if not access_token:
        return "Не удалось получить доступ к сервису."

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    context_parts = [content for content, url in context_with_urls]
    context = "\n\n".join(context_parts)

    if not context:
        return "Ошибка: контекст пуст или некорректен."

    system_message = (
        "Ты — виртуальный помощник компании EORA. "
        "Твоя задача — предлагать услуги компании строго в рамках запроса, основываясь на предоставленном контексте. "
        "Предлагай услуги для розничных торговцев, избегая использования неподтверждённых данных или выдуманных предложений. "
        "Ответы должны быть краткими, точными и релевантными. "
        "Используй только релевантные ссылки на сайт EORA. Если таких ссылок нет — не добавляй их. "
        "Если подходящие ссылки или услуги отсутствуют, лучше пропустить это, чем добавлять нерелевантные данные."
    )

    payload = {
        "model": "GigaChat",
        "messages": [
            {"role": "system", "content": f"{system_message}\n\nКонтекст:\n{context}"},
            {"role": "user", "content": question},
        ],
    }

    ssl_context = create_ssl_context()

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                url, json=payload, headers=headers, ssl=ssl_context
            ) as response:
                if response.status != 200:
                    logger.error(f"Error: Received status code {response.status}")
                    text = await response.text()
                    logger.error(f"Response: {text}")
                    return "Извините, произошла ошибка при обработке вашего запроса."

                result = await response.json()
                answer = result["choices"][0]["message"]["content"]

                return format_answer(html.escape(answer), context_with_urls, used_urls)

        except aiohttp.ClientConnectorError as e:
            logger.error(f"Connection error: {e}")
            return "Извините, не удалось подключиться к сервису обработки запросов."
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
            return "Извините, произошла ошибка при обработке вашего запроса."
