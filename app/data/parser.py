import asyncio
import aiohttp
import logging
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.data.models.source import Source  # Импорт модели для таблицы sources
from app.data.session import engine  # Импорт сессии и функции для получения сессии
from app.utils.url_data import URLS_TO_PARSE  # Импорт списка URL для парсинга
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем фабрику для сессий
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def parse_and_save(session: aiohttp.ClientSession, db_session: AsyncSession, url: str):
    """
    Парсит страницу по заданному URL, очищает текст и сохраняет его в базу данных.
    """
    try:
        logger.info(f"Starting to parse {url}")  # Логирование начала парсинга
        async with session.get(url) as response:
            logger.info(f"Received response from {url} with status {response.status}")
            if response.status == 403:
                logger.warning(f"Access forbidden for URL {url}. Skipping.")
                return  # Пропускаем URL, если доступ запрещен

            if response.status == 200:
                content = await response.text()
                logger.info(f"Fetched content from {url}: {content[:100]}...")  # Ограничиваем вывод
                soup = BeautifulSoup(content, 'html.parser')
                parsed_text = soup.get_text(separator=' ', strip=True)
                cleaned_text = clean_text(parsed_text)
                logger.info(f"Cleaned content from {url}: {cleaned_text[:100]}...")  # Ограничиваем вывод
                await save_data_to_db(db_session, url, cleaned_text)
                logger.info(f"Successfully saved content from {url}")
            else:
                logger.warning(f"Failed to fetch data from {url}: Status {response.status}")
    except Exception as e:
        logger.error(f"Error fetching data from {url}: {e}")


def clean_text(text: str) -> str:
    """
    Очищает текст, удаляя лишние пробелы и символы переноса строки.
    """
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


async def save_data_to_db(db_session: AsyncSession, url: str, content: str):
    """
    Сохраняет данные в базу данных через SQLAlchemy.
    """
    try:
        existing_entry = await db_session.execute(
            select(Source).where(Source.url == url)
        )
        if existing_entry.scalars().first():
            logger.debug(f"URL {url} already exists in the database, skipping.")
            return

        new_source = Source(url=url, content=content)
        db_session.add(new_source)
        await db_session.commit()
        logger.info(f"Data saved for URL: {url}")
    except Exception as e:
        logger.error(f"Failed to save data for {url}: {e}")
        await db_session.rollback()


async def parse_all_urls():
    """
    Запускает процесс парсинга всех URL из списка.
    """
    logger.info("Starting parsing for all URLs")
    async with aiohttp.ClientSession() as session:
        async with SessionLocal() as db_session:
            tasks = [parse_and_save(session, db_session, url) for url in URLS_TO_PARSE]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Логируем только ошибки
            errors = [result for result in results if isinstance(result, Exception)]
            if errors:
                logger.error(f"Encountered {len(errors)} errors during parsing")

    logger.info("Completed parsing for all URLs")
