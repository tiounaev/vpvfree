from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from bot.config import settings

# 1) Базовый класс для ваших моделей
Base = declarative_base()

# 2) Асинхронный движок
#    Убедитесь, что в .env у вас DSN вида:
#    postgresql+asyncpg://user:pass@db:5432/base
engine = create_async_engine(
    settings.DB_DSN,
    echo=False,
    future=True,
)

# 3) factory для сессий
async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
