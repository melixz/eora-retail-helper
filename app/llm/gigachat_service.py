import asyncio
from app.llm.gigachat_response import generate_answer


async def main():
    """
    Основная логика вызова функции генерации ответа от GigaChat API.
    """
    question = "Что вы можете предложить ритейлерам?"
    context = [
        ("Чат-боты для бизнеса могут быть полезны для общения с клиентами и автоматизации поддержки.",
         "https://eora.ru/cases/chat-boty/purina-friskies-chat-bot-na-sajte"),
        ("Автоматизация процессов с помощью нейросетей повышает эффективность работы.",
         "https://eora.ru/cases/qiwi-poisk-anomalij")
    ]

    used_urls = set()
    answer = await generate_answer(question, context, used_urls)

    print(f"Вопрос: {question}")
    print(f"Ответ: {answer}")


if __name__ == "__main__":
    asyncio.run(main())
