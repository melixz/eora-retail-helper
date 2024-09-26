from gigachat import GigaChat
from bot.config import GIGACHAT_API_KEY
import json


async def generate_answer(question, context):
    """
    Асинхронная генерация ответа с использованием GigaChat API.
    """
    async with GigaChat(credentials=GIGACHAT_API_KEY, verify_ssl_certs=False) as giga:
        prompt = f"Вопрос: {question}\nКонтекст: {context}"
        response = await giga.chat(prompt)
        return response.choices[0].message.content


def load_sources():
    """
    Загрузка контента из sources.json для формирования базы знаний.
    """
    with open("data/sources.json", "r", encoding="utf-8") as file:
        return json.load(file)
