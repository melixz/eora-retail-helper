import logging
from aiogram import types
from aiogram.filters import Command
from bot.bot import router
from utils.gigachat_service import generate_answer
from utils.gigachat_auth import get_access_token
from data.database import fetch_context_from_db

# Настройка логирования
logger = logging.getLogger(__name__)


# Обработчик команды /start
async def start_command(message: types.Message):
    logger.info(f"Received /start command from user {message.from_user.id}")
    await message.answer("Привет! Я могу помочь ответить на вопросы о возможностях для ритейлеров.")


# Обработчик текстовых вопросов
async def handle_question(message: types.Message):
    user_question = message.text
    logger.info(f"Received question from user {message.from_user.id}: {user_question}")

    context = await fetch_context_from_db(user_question, limit=3)
    logger.debug(f"Fetched context for user {message.from_user.id}: {context}")

    # Получаем токен
    token = await get_access_token()

    # Генерируем ответ
    answer = await generate_answer(user_question, context)
    logger.info(f"Sending answer to user {message.from_user.id}")

    await message.answer(answer)


# Регистрируем обработчики команд и сообщений
router.message.register(start_command, Command(commands=['start']))
router.message.register(handle_question)
