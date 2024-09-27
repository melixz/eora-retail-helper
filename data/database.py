import asyncpg
import os
import logging

logger = logging.getLogger(__name__)


async def setup_db():
    """
    Инициализация базы данных. Создает таблицы, если их еще не существует.
    """
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
        logger.info("Инициализация базы данных завершена.")
    except Exception as e:
        logger.exception(f"Ошибка при инициализации базы данных: {e}")


async def save_data_to_db(url, content):
    """
    Сохраняет данные в базу данных (ссылка и контент страницы).
    """
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
        logger.info(f"Данные сохранены в базу для URL: {url}")
    except Exception as e:
        logger.exception(f"Ошибка при сохранении данных в базу для URL {url}: {e}")


async def fetch_context_from_db(question, limit=5):
    """
    Извлекает контекст из базы данных на основе запроса пользователя.
    Возвращает наиболее релевантные результаты, используя полнотекстовый поиск.
    """
    try:
        conn = await asyncpg.connect(
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB'),
            host=os.getenv('POSTGRES_HOST', 'db'),
            port=int(os.getenv('POSTGRES_PORT', 5432))
        )
        rows = await conn.fetch('''
            SELECT content, url
            FROM sources
            WHERE to_tsvector('russian', content) @@ plainto_tsquery('russian', $1)
            LIMIT $2
        ''', question, limit)
        await conn.close()

        if not rows:
            logger.info("Не найдено релевантного контекста, возвращаем последние источники.")
            conn = await asyncpg.connect(
                user=os.getenv('POSTGRES_USER'),
                password=os.getenv('POSTGRES_PASSWORD'),
                database=os.getenv('POSTGRES_DB'),
                host=os.getenv('POSTGRES_HOST', 'db'),
                port=int(os.getenv('POSTGRES_PORT', 5432))
            )
            rows = await conn.fetch('SELECT content, url FROM sources ORDER BY id DESC LIMIT $1', limit)
            await conn.close()

        context_with_urls = [(row['content'][:500], row['url']) for row in rows]
        return context_with_urls
    except Exception as e:
        logger.exception(f"Ошибка при извлечении контекста из базы данных: {e}")
        return []
