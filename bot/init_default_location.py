import asyncio
from bot.services.db import async_session
from bot.models import Location, Tariff

async def main():
    async with async_session() as session:
        # Проверка на наличие уже существующей default-локации
        existing = await session.execute(
            Location.__table__.select().where(Location.is_default == True)
        )
        if existing.first():
            print("⚠️ Default локация уже существует.")
            return

        # Создаём локацию США
        us = Location(name="🇺🇸 США", code="us", is_active=True, is_default=True)
        session.add(us)
        await session.flush()  # получаем us.id

        # Добавим тарифы
        session.add_all([
            Tariff(location_id=us.id, duration_days=30, price=100.00, title="1 месяц — 100₽"),
            Tariff(location_id=us.id, duration_days=90, price=200.00, title="3 месяца — 200₽"),
            Tariff(location_id=us.id, duration_days=180, price=300.00, title="6 месяцев — 300₽"),
        ])
        await session.commit()
        print("✅ Default location и тарифы успешно добавлены.")

if __name__ == "__main__":
    asyncio.run(main())
