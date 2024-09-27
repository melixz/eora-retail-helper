import asyncio
import aiohttp
import logging
from bs4 import BeautifulSoup
from data.database import save_data_to_db
from utils.url_data import URLS_TO_PARSE  # Импортируем URL для парсинга
import re

# Настройка логирования
logger = logging.getLogger(__name__)


# Асинхронная функция для парсинга страницы и сохранения данных
async def parse_and_save(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                # Извлечение текста со страницы
                parsed_text = soup.get_text(separator=' ', strip=True)
                cleaned_text = clean_text(parsed_text)
                await save_data_to_db(url, cleaned_text)
                logger.info(f"Saved content from {url}")
            else:
                logger.warning(f"Failed to fetch {url}: Status {response.status}")
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")


# Функция для очистки текста
def clean_text(text):
    # Удаляем лишние пробелы и символы переноса строки
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# Асинхронная функция для парсинга всех ссылок из списка
async def parse_all_urls():
    logger.info("Starting to parse all URLs")
    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save(session, url) for url in URLS_TO_PARSE]  # Используем URL из url_data.py
        await asyncio.gather(*tasks)
    logger.info("Completed parsing all URLs")
