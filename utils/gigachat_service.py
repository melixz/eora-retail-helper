import asyncio
from utils.gigachat_response import generate_answer  # Импортируем функцию генерации ответа


# Основная логика, вызов необходимых функций
async def main():
    question = "Что такое искусственный интеллект?"
    context = [("Вы - эксперт по искусственному интеллекту.", "https://example.com/ai_article")]
    answer = await generate_answer(question, context)
    print(f"Вопрос: {question}")
    print(f"Ответ: {answer}")


if __name__ == "__main__":
    asyncio.run(main())
