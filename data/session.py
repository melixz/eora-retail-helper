from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from bot.config import DATABASE_URL  # Импортируем строку подключения
from data.models.base import Base
from data.models.source import Source

# Создание движка для асинхронной работы с базой данных
engine = create_async_engine(DATABASE_URL, echo=True)

# Создание фабрики сессий
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def get_db():
    """Генератор для получения сессии базы данных."""
    async with SessionLocal() as session:
        yield session


async def init_db():
    """Функция для инициализации базы данных и создания таблиц."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Функция для сохранения данных
async def save_data_to_db(db: AsyncSession, url: str, content: str):
    """Сохраняет данные в базу данных (ссылка и контент страницы)."""
    new_source = Source(url=url, content=content)
    db.add(new_source)
    await db.commit()


# Функция для извлечения контекста
async def fetch_context_from_db(db: AsyncSession, question: str, limit: int = 5):
    """Извлекает контекст из базы данных на основе запроса пользователя."""
    query = select(Source).limit(limit)
    result = await db.execute(query)
    sources = result.scalars().all()

    context_with_urls = [(source.content[:500], source.url) for source in sources]
    return context_with_urls
