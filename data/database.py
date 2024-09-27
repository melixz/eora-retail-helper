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


async def fetch_context_from_db(question, limit=5):
    try:
        conn = await asyncpg.connect(
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB'),
            host=os.getenv('POSTGRES_HOST', 'db'),
            port=int(os.getenv('POSTGRES_PORT', 5432))
        )
        # Используем полнотекстовый поиск по вопросу
        rows = await conn.fetch('''
            SELECT content, url
            FROM sources
            WHERE to_tsvector('russian', content) @@ plainto_tsquery('russian', $1)
            LIMIT $2
        ''', question, limit)

        await conn.close()

        if not rows:
            # Если нет результатов, возвращаем последние добавленные источники
            logger.info("No relevant context found, fetching recent sources.")
            conn = await asyncpg.connect(
                user=os.getenv('POSTGRES_USER'),
                password=os.getenv('POSTGRES_PASSWORD'),
                database=os.getenv('POSTGRES_DB'),
                host=os.getenv('POSTGRES_HOST', 'db'),
                port=int(os.getenv('POSTGRES_PORT', 5432))
            )
            rows = await conn.fetch('SELECT content, url FROM sources ORDER BY id DESC LIMIT $1', limit)
            await conn.close()

        context_with_urls = [(row['content'][:500], row['url']) for row in rows]  # Ограничиваем длину контента
        return context_with_urls
    except Exception as e:
        logger.exception(f"Error fetching context from DB: {e}")
        return []
