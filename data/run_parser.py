import asyncio
from data.session import init_db
from data.parser import parse_all_urls


async def run_parser():
    """Запускает парсер с предварительной инициализацией базы данных."""
    print("Initializing database...")
    await init_db()
    print("Database initialized.")

    print("Starting data parsing...")
    await parse_all_urls()
    print("Parsing completed.")


if __name__ == "__main__":
    asyncio.run(run_parser())
