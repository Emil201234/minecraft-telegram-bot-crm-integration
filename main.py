from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers.router import router_bot, DEMO_MODE
from aiogram.types import BotCommand
from handlers import blocked_users, router
import asyncio, os

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")


dp = Dispatcher()
dp.include_router(router_bot)

async def set_commands(bot: Bot):
    if DEMO_MODE == "True":
        await bot.set_my_commands([
            BotCommand(command="start", description="Запуск бота"),
            BotCommand(command="link", description="Привязать аккаунт"),
            BotCommand(command="unblock", description="Разблокировать")
        ])
    else:
        await bot.set_my_commands([
            BotCommand(command="start", description="Запуск бота"),
            BotCommand(command="link", description="Привязать аккаунт")
        ])

async def main():
    if DEMO_MODE == "True":
        print("DEMO-MODE IS ACTIVE")
    if not TOKEN:
        print("not bot_token")
        return
    else:
        bot = Bot(token=TOKEN)

    await blocked_users.init_db() # CREATE TABLE blocked_users
    await router.init_db()        # CREATE TABLE users

    await set_commands(bot)
    print("start-polling")
    await dp.start_polling(bot)


if __name__ == '__main__':
    # logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")