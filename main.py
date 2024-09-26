import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from bot.config import BOT_TOKEN
from bot.handlers import router
from utils.parser import parse_all_urls


async def start_parsing():
    """Функция для старта асинхронного парсинга в фоне"""
    print("Starting data parsing in background...")
    await parse_all_urls()  # Асинхронно выполняем парсинг


async def main():
    """Запуск бота и диспетчера"""
    logging.basicConfig(level=logging.INFO)
    session = AiohttpSession()

    # Используем DefaultBotProperties для указания parse_mode
    bot = Bot(
        token=BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    # Запускаем парсинг данных как фоновую задачу
    asyncio.create_task(start_parsing())

    # Запускаем бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
