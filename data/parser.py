import asyncio
import aiohttp
import logging
from bs4 import BeautifulSoup
from data.database import save_data_to_db
from utils.url_data import URLS_TO_PARSE
import re

logger = logging.getLogger(__name__)


async def parse_and_save(session, url):
    """
    Парсит страницу по заданному URL, очищает текст и сохраняет его в базу данных.
    """
    try:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                parsed_text = soup.get_text(separator=' ', strip=True)
                cleaned_text = clean_text(parsed_text)
                await save_data_to_db(url, cleaned_text)
                logger.info(f"Сохранен контент с {url}")
            else:
                logger.warning(f"Не удалось получить данные с {url}: Статус {response.status}")
    except Exception as e:
        logger.error(f"Ошибка при получении данных с {url}: {e}")


def clean_text(text):
    """
    Очищает текст, удаляя лишние пробелы и символы переноса строки.
    """
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


async def parse_all_urls():
    """
    Запускает процесс парсинга всех URL из списка.
    """
    logger.info("Начало парсинга всех URL")
    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save(session, url) for url in URLS_TO_PARSE]
        await asyncio.gather(*tasks)
    logger.info("Парсинг всех URL завершен")
