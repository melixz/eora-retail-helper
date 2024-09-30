import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from app.bot.config import BOT_TOKEN
from app.bot.handlers import router
from app.data.session import init_db
from aiogram.types import BotCommand
from app.data.parser import parse_all_urls  # Импортируем функцию парсинга

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def set_bot_commands(bot: Bot):
    """Регистрация команд для быстрого доступа в меню Telegram."""
    commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/help", description="Показать вопросы для бота"),
        BotCommand(command="/contact", description="Контактные данные компании")
    ]
    await bot.set_my_commands(commands)


async def start_bot():
    """Запускает Telegram-бота."""
    session = AiohttpSession()

    # Инициализация базы данных перед запуском бота
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized.")

    # Запуск процесса парсинга URL
    logger.info("Starting URL parsing...")
    await parse_all_urls()
    logger.info("URL parsing completed.")

    # Создание экземпляра бота
    bot = Bot(
        token=BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Создание диспетчера
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    # Регистрация быстрых команд в меню
    await set_bot_commands(bot)

    # Запуск бота
    logger.info("Starting polling...")
    await dp.start_polling(bot)


async def main():
    """Основная функция для запуска бота и парсера."""
    # Запуск базы данных и парсера
    await init_db()
    await parse_all_urls()  # Добавляем вызов парсинга перед запуском бота

    # Запуск бота
    await start_bot()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
