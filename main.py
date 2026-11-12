from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers.router import router_bot, DEMO_MODE
from aiogram.types import BotCommand
from handlers import blocked_users, router
import asyncio, os, logging, sys

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout) # Вывод в консоль (и в логи Railway)
    ]
)

logger = logging.getLogger(__name__)

dp = Dispatcher()
dp.include_router(router_bot)

async def set_commands(bot: Bot):
    if DEMO_MODE:
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
    if DEMO_MODE:
        logger.info("DEMO-MODE IS ACTIVE")
    if not TOKEN:
        logger.critical("BOT_TOKEN не найден! Проверьте файл .env")
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