import asyncio

from src.telegram.bot import dp, bot
from src.db.database import create_tables, drop_tables


async def main():
    # await drop_tables()
    # await create_tables()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
