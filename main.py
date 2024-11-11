import asyncio
import multiprocessing
import message_handler
from throttle import AntiFloodMiddleware
from database import Base, engine, create_config, add_admin
from init import bot, dp
from admin_list import update_admin_list


async def main_bot():
    await create_config()
    await add_admin(1805327769)
    asyncio.create_task(update_admin_list())
    dp.message.middleware(AntiFloodMiddleware(0.5))

    dp.include_router(
        message_handler.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

def start_bot():
    asyncio.run(main_bot())

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)

    bot_process = multiprocessing.Process(target=start_bot)
    bot_process.start()
    bot_process.join()
