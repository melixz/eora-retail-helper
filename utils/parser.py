import asyncio
import aiohttp
import logging
from bs4 import BeautifulSoup
from data.database import save_data_to_db
import re

# Настройка логирования
logger = logging.getLogger(__name__)

# Список ссылок для парсинга
URLS_TO_PARSE = [
    "https://eora.ru/cases/promyshlennaya-bezopasnost",
    "https://eora.ru/cases/lamoda-systema-segmentacii-i-poiska-po-pohozhey-odezhde",
    "https://eora.ru/cases/navyki-dlya-golosovyh-assistentov/karas-golosovoy-assistent",
    "https://eora.ru/cases/assistenty-dlya-gorodov",
    "https://eora.ru/cases/avtomatizaciya-v-promyshlennosti/chemrar-raspoznovanie-molekul",
    "https://eora.ru/cases/zeptolab-skazki-pro-amnyama-dlya-sberbox",
    "https://eora.ru/cases/goosegaming-algoritm-dlya-ocenki-igrokov",
    "https://eora.ru/cases/dodo-pizza-robot-analitik-otzyvov",
    "https://eora.ru/cases/ifarm-nejroset-dlya-ferm",
    "https://eora.ru/cases/zhivibezstraha-navyk-dlya-proverki-rodinok",
    "https://eora.ru/cases/sportrecs-nejroset-operator-sportivnyh-translyacij",
    "https://eora.ru/cases/avon-chat-bot-dlya-zhenshchin",
    "https://eora.ru/cases/navyki-dlya-golosovyh-assistentov/navyk-dlya-proverki-loterejnyh-biletov",
    "https://eora.ru/cases/computer-vision/iss-analiz-foto-avtomobilej",
    "https://eora.ru/cases/purina-master-bot",
    "https://eora.ru/cases/skinclub-algoritm-dlya-ocenki-veroyatnostej",
    "https://eora.ru/cases/skolkovo-chat-bot-dlya-startapov-i-investorov",
    "https://eora.ru/cases/purina-podbor-korma-dlya-sobaki",
    "https://eora.ru/cases/purina-navyk-viktorina",
    "https://eora.ru/cases/dodo-pizza-pilot-po-avtomatizacii-kontakt-centra",
    "https://eora.ru/cases/dodo-pizza-avtomatizaciya-kontakt-centra",
    "https://eora.ru/cases/icl-bot-sufler-dlya-kontakt-centra",
    "https://eora.ru/cases/s7-navyk-dlya-podbora-aviabiletov",
    "https://eora.ru/cases/workeat-whatsapp-bot",
    "https://eora.ru/cases/absolyut-strahovanie-navyk-dlya-raschyota-strahovki",
    "https://eora.ru/cases/kazanexpress-poisk-tovarov-po-foto",
    "https://eora.ru/cases/kazanexpress-sistema-rekomendacij-na-sajte",
    "https://eora.ru/cases/intels-proverka-logotipa-na-plagiat",
    "https://eora.ru/cases/karcher-viktorina-s-voprosami-pro-uborku",
    "https://eora.ru/cases/chat-boty/purina-friskies-chat-bot-na-sajte",
    "https://eora.ru/cases/nejroset-segmentaciya-video",
    "https://eora.ru/cases/chat-boty/essa-nejroset-dlya-generacii-rolikov",
    "https://eora.ru/cases/qiwi-poisk-anomalij",
    "https://eora.ru/cases/frisbi-nejroset-dlya-raspoznavaniya-pokazanij-schetchikov",
    "https://eora.ru/cases/skazki-dlya-gugl-assistenta",
    "https://eora.ru/cases/chat-boty/hr-bot-dlya-magnit-kotoriy-priglashaet-na-sobesedovanie"
]


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
        tasks = [parse_and_save(session, url) for url in URLS_TO_PARSE]
        await asyncio.gather(*tasks)
    logger.info("Completed parsing all URLs")
