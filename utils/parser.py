import aiohttp
from bs4 import BeautifulSoup
import json

LINKS = [
    "https://eora.ru/cases/promyshlennaya-bezopasnost",
    "https://eora.ru/cases/lamoda-systema-segmentacii-i-poiska-po-pohozhey-odezhde",
    "https://eora.ru/cases/navyki-dlya-golosovyh-assistentov/karas-golosovoy-assistent",
    # Добавь остальные ссылки
]


async def fetch_page(url, session):
    """
    Асинхронная загрузка страницы по URL с использованием aiohttp.
    """
    async with session.get(url) as response:
        return await response.text()


async def parse_page(url, session):
    """
    Парсинг страницы и получение контента.
    """
    try:
        html_content = await fetch_page(url, session)
        soup = BeautifulSoup(html_content, 'html.parser')
        content = soup.find("div", {"class": "content"})
        return content.get_text(separator="\n").strip() if content else ""
    except Exception as e:
        print(f"Ошибка при парсинге страницы {url}: {e}")
        return ""


async def parse_and_save_sources():
    """
    Асинхронный парсинг всех страниц и сохранение данных в файл JSON.
    """
    async with aiohttp.ClientSession() as session:
        sources_data = {}
        for url in LINKS:
            content = await parse_page(url, session)
            if content:
                sources_data[url] = content
                print(f"Успешно распарсено: {url}")

        with open("data/sources.json", "w", encoding="utf-8") as file:
            json.dump(sources_data, file, ensure_ascii=False, indent=4)


# Этот блок нужен для самостоятельного запуска парсера
if __name__ == "__main__":
    import asyncio

    asyncio.run(parse_and_save_sources())
