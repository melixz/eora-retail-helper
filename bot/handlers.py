from aiogram import types
from aiogram.filters import Command
from utils.gigachat_service import generate_answer, load_sources
from bot.bot import router

# Загружаем базу данных при инициализации
sources_data = load_sources()


# Обработчик команды /start
async def start_command(message: types.Message):
    await message.answer("Привет! Я могу помочь ответить на вопросы о наших проектах.")


# Обработчик текстовых вопросов
async def handle_question(message: types.Message):
    user_question = message.text

    # Формируем контекст для ответа на основе источников
    context = ""
    for url, content in sources_data.items():
        if any(keyword in user_question.lower() for keyword in ["ритейлеры", "промышленность", "боты"]):
            context += f"{content}\n\n"

    # Если контекст найден, отправляем его в GigaChat для генерации ответа
    if context:
        answer = await generate_answer(user_question, context)
        await message.answer(answer)
    else:
        await message.answer("Извините, я не смог найти подходящий контекст для вашего вопроса.")


# Регистрируем обработчики команд и сообщений
router.message.register(start_command, Command(commands=['start']))
router.message.register(handle_question)
