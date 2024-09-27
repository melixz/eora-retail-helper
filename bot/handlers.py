import logging
from aiogram import types
from aiogram.filters import Command
from bot.bot import router
from llm.gigachat_service import generate_answer
from data.database import fetch_context_from_db

logger = logging.getLogger(__name__)
user_sessions = {}


async def start_command(message: types.Message):
    """
    Обрабатывает команду /start. Инициализирует сессию пользователя и отправляет приветственное сообщение.
    """
    logger.info(f"Received /start command from user {message.from_user.id}")
    user_sessions[message.from_user.id] = {"started": True, "context": [], "used_urls": []}
    await message.answer("Привет! Я могу помочь ответить на вопросы о наших проектах и возможностях для ритейлеров.")


async def help_command(message: types.Message):
    """
    Обрабатывает команду /help. Отправляет список вопросов, на которые бот может ответить.
    """
    logger.info(f"Received /help command from user {message.from_user.id}")
    await message.answer("Я могу помочь ответить на следующие вопросы:\n"
                         "1. Что вы можете сделать для ритейлеров?\n"
                         "2. Хочу с вами сотрудничать!\n"
                         "3. Как с вами связаться?")


async def contact_command(message: types.Message):
    """
    Обрабатывает команду /contact. Отправляет контактную информацию компании.
    """
    logger.info(f"Received /contact command from user {message.from_user.id}")
    contact_info = (
        "Свяжитесь с нами по следующему адресу:\n"
        "📧 Email: info@eora.ru\n"
        "📞 Телефон: +7 (495) 123-45-67\n"
        "🌍 Подробнее: https://eora.ru/contacts"
    )
    await message.answer(contact_info)


async def handle_question(message: types.Message):
    """
    Обрабатывает текстовые вопросы пользователя, извлекая релевантный контекст из базы данных и генерируя ответ.
    """
    user_id = message.from_user.id
    if user_id not in user_sessions or not user_sessions[user_id].get("started"):
        await message.answer("Пожалуйста, введите команду /start для начала сессии.")
        return

    user_question = message.text
    logger.info(f"Received question from user {user_id}: {user_question}")

    context_with_urls = await fetch_context_from_db(user_question, limit=5)
    logger.debug(f"Fetched context for user {user_id}: {context_with_urls}")

    user_sessions[user_id]["context"].extend(context_with_urls)

    used_urls = user_sessions[user_id].get("used_urls", [])
    answer = await generate_answer(user_question, context_with_urls, used_urls)

    user_sessions[user_id]["used_urls"].extend(context_with_urls)

    logger.info(f"Sending answer to user {user_id}")
    await message.answer(answer)


# Регистрируем обработчики команд и сообщений
router.message.register(start_command, Command(commands=['start']))
router.message.register(help_command, Command(commands=['help']))
router.message.register(contact_command, Command(commands=['contact']))
router.message.register(handle_question)
