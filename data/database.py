import asyncpg
import os


async def setup_db():
    conn = await asyncpg.connect(
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        database=os.getenv('POSTGRES_DB'),
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=5432
    )
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS sources (
            id SERIAL PRIMARY KEY,
            url TEXT,
            content TEXT
        );
    ''')
    await conn.close()


async def save_data_to_db(url, content):
    conn = await asyncpg.connect(
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        database=os.getenv('POSTGRES_DB'),
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=5432
    )
    await conn.execute('INSERT INTO sources(url, content) VALUES($1, $2)', url, content)
    await conn.close()


async def fetch_context_from_db(question):
    conn = await asyncpg.connect(
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        database=os.getenv('POSTGRES_DB'),
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=5432
    )
    rows = await conn.fetch('SELECT content FROM sources')
    await conn.close()

    # Пример логики для создания контекста из данных
    context = "\n".join([row['content'] for row in rows])
    return context
