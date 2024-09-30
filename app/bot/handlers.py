import logging
from aiogram import types
from aiogram.filters import Command
from app.bot.bot import router
from app.llm.gigachat_service import generate_answer
from app.data.session import get_db, fetch_context_from_db

logger = logging.getLogger(__name__)

# Словарь для хранения сессий пользователей
user_sessions = {}


# Обработчик команды /start
async def start_command(message: types.Message):
    logger.info(f"Received /start command from user {message.from_user.id}")

    # Инициализация сессии пользователя
    user_sessions[message.from_user.id] = {
        "started": True,
        "context": [],
        "used_urls": set()
    }

    await message.answer("Привет! Я могу помочь ответить на вопросы о наших проектах и возможностях для ритейлеров.")


# Обработчик команды /help
async def help_command(message: types.Message):
    logger.info(f"Received /help command from user {message.from_user.id}")

    await message.answer(
        "Я могу помочь ответить на следующие вопросы:\n"
        "1. Что вы можете сделать для ритейлеров?\n"
        "2. Хочу с вами сотрудничать!\n"
        "3. Как с вами связаться?"
    )


# Обработчик команды /contact
async def contact_command(message: types.Message):
    logger.info(f"Received /contact command from user {message.from_user.id}")

    contact_info = (
        "Свяжитесь с нами по следующему адресу:\n"
        "📧 Email: info@eora.ru\n"
        "📞 Телефон: +7 (495) 123-45-67\n"
        "🌍 Подробнее: https://eora.ru/contacts"
    )
    await message.answer(contact_info)


# Обработчик текстовых вопросов
async def handle_question(message: types.Message):
    user_id = message.from_user.id

    # Проверяем, начал ли пользователь сессию с командой /start
    if user_id not in user_sessions or not user_sessions[user_id].get("started"):
        await message.answer("Пожалуйста, введите команду /start для начала сессии.")
        return

    user_question = message.text
    logger.info(f"Received question from user {user_id}: {user_question}")

    # Получаем контекст из базы данных
    context_with_urls = []
    async for db in get_db():
        fetched_context = await fetch_context_from_db(db, user_question, limit=5)
        context_with_urls.extend(fetched_context)
    logger.debug(f"Fetched context for user {user_id}: {context_with_urls}")

    # Обновляем контекст сессии
    current_session = user_sessions[user_id]
    current_session["context"].extend(context_with_urls)

    # Генерация ответа
    used_urls = current_session["used_urls"]
    answer = await generate_answer(user_question, context_with_urls, list(used_urls))

    # Обновляем список использованных ссылок
    new_urls = [url for _, url in context_with_urls]
    current_session["used_urls"].update(new_urls)

    logger.info(f"Sending answer to user {user_id}")

    # Отправляем ответ с режимом HTML для корректного отображения ссылок
    await message.answer(answer, parse_mode='HTML')


# Регистрируем обработчики команд и сообщений
router.message.register(start_command, Command(commands=['start']))
router.message.register(help_command, Command(commands=['help']))
router.message.register(contact_command, Command(commands=['contact']))
router.message.register(handle_question)
