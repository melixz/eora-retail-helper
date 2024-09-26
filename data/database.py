import asyncpg
import os
import logging

# Настройка логирования
logger = logging.getLogger(__name__)


async def setup_db():
    try:
        conn = await asyncpg.connect(
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB'),
            host=os.getenv('POSTGRES_HOST', 'db'),
            port=int(os.getenv('POSTGRES_PORT', 5432))
        )
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS sources (
                id SERIAL PRIMARY KEY,
                url TEXT,
                content TEXT
            );
        ''')
        await conn.close()
        logger.info("Database setup completed.")
    except Exception as e:
        logger.exception(f"Error setting up the database: {e}")


async def save_data_to_db(url, content):
    try:
        conn = await asyncpg.connect(
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB'),
            host=os.getenv('POSTGRES_HOST', 'db'),
            port=int(os.getenv('POSTGRES_PORT', 5432))
        )
        await conn.execute('INSERT INTO sources(url, content) VALUES($1, $2)', url, content)
        await conn.close()
        logger.info(f"Data saved to DB for URL: {url}")
    except Exception as e:
        logger.exception(f"Error saving data to DB for URL {url}: {e}")


async def fetch_context_from_db(question, limit=3):
    try:
        conn = await asyncpg.connect(
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB'),
            host=os.getenv('POSTGRES_HOST', 'db'),
            port=int(os.getenv('POSTGRES_PORT', 5432))
        )
        rows = await conn.fetch('SELECT content FROM sources ORDER BY id DESC LIMIT $1', limit)
        await conn.close()

        # Создаём контекст из данных
        context = "\n".join([row['content'] for row in rows])
        limited_context = context[:1000]  # Ограничиваем общую длину контекста до 1000 символов
        logger.debug(f"Fetched context (limited to 1000 chars): {limited_context}")
        return limited_context
    except Exception as e:
        logger.exception(f"Error fetching context from DB: {e}")
        return ""
