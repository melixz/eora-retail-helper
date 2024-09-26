import aiohttp
from bot.config import GIGACHAT_API_KEY


# Асинхронная функция для отправки запроса в GigaChat API
async def generate_answer(question, context):
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GIGACHAT_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "GigaChat",
        "messages": [
            {"role": "system", "content": f"Контекст: {context}"},
            {"role": "user", "content": question}
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            result = await response.json()
            return result["choices"][0]["message"]["content"]
