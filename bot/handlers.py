import logging
from aiogram import types
from aiogram.filters import Command
from bot.bot import router
from ml.gigachat_service import generate_answer
from data.database import fetch_context_from_db

# Настройка логирования
logger = logging.getLogger(__name__)

# Словарь для хранения сессий пользователей
user_sessions = {}


# Обработчик команды /start
async def start_command(message: types.Message):
    logger.info(f"Received /start command from user {message.from_user.id}")

    # Инициализация сессии пользователя
    user_sessions[message.from_user.id] = {"started": True, "context": [], "used_urls": []}

    await message.answer("Привет! Я могу помочь ответить на вопросы о наших проектах и возможностях для ритейлеров.")


# Обработчик текстовых вопросов
async def handle_question(message: types.Message):
    user_id = message.from_user.id

    # Проверяем, начал ли пользователь сессию с командой /start
    if user_id not in user_sessions or not user_sessions[user_id].get("started"):
        await message.answer("Пожалуйста, введите команду /start для начала сессии.")
        return

    user_question = message.text
    logger.info(f"Received question from user {user_id}: {user_question}")

    # Получаем контекст из БД
    context_with_urls = await fetch_context_from_db(user_question, limit=5)
    logger.debug(f"Fetched context for user {user_id}: {context_with_urls}")

    # Сохраняем контекст в сессии
    user_sessions[user_id]["context"].extend(context_with_urls)

    # Генерация ответа с учетом прикрепления ссылок и ранее использованных
    used_urls = user_sessions[user_id].get("used_urls", [])
    answer = await generate_answer(user_question, context_with_urls, used_urls)

    # Обновляем список использованных ссылок в сессии
    user_sessions[user_id]["used_urls"].extend(context_with_urls)

    logger.info(f"Sending answer to user {user_id}")

    await message.answer(answer)


# Регистрируем обработчики команд и сообщений
router.message.register(start_command, Command(commands=['start']))
router.message.register(handle_question)
