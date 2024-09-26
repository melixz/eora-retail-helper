import asyncio
from data.database import setup_db  # Добавлено импорт функции setup_db
from utils.parser import parse_all_urls


async def main():
    print("Initializing database...")
    await setup_db()  # Добавлено вызов setup_db()
    print("Database initialized.")

    print("Starting data parsing...")
    await parse_all_urls()
    print("Parsing completed.")


if __name__ == "__main__":
    asyncio.run(main())
