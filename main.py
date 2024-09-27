import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from bot.config import BOT_TOKEN
from bot.handlers import router
from data.parser import parse_all_urls
from data.database import setup_db
from aiogram.types import BotCommand  # Для регистрации команд

# Настройка логирования
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


async def start_parsing():
    """Функция для запуска асинхронного парсинга в фоне"""
    logger.info("Starting data parsing in background...")
    await parse_all_urls()
    logger.info("Data parsing completed.")


async def main():
    """Запуск бота и диспетчера"""
    session = AiohttpSession()

    # Инициализация базы данных перед запуском бота
    logger.info("Initializing database...")
    await setup_db()
    logger.info("Database initialized.")

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

    # Запуск парсинга данных как фоновую задачу
    await asyncio.create_task(start_parsing())

    # Запуск бота
    logger.info("Starting polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
