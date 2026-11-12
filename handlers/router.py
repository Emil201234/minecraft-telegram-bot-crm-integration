import aiosqlite, hashlib, time, os, logging, asyncio
from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery
)
from handlers import block_user, blocked_left, keyboards, run_command
from handlers import blocked_users
from forms.user import Form_user
from config import DEMO_MODE
from dotenv import load_dotenv
from datetime import datetime



router_bot = Router()

# Переменные

load_dotenv()
if DEMO_MODE:
    LINKS_DB = "links.db"
    AUTH_ME_DB = "authme.db"
    USERS_DB = os.getenv("USERS_DB", "bot.db")
    ADMINS_env = os.getenv("ADMINS", "123456789")
    TECH_SUPPORT = "https://t.me"
    SUGGESTION = "https://t.me"
else:
    LINKS_DB = os.getenv("LINKS_DB")
    AUTH_ME_DB = os.getenv("AUTH_ME_DB")
    USERS_DB = os.getenv("USERS_DB")
    ADMINS_env = os.getenv("ADMINS")
    TECH_SUPPORT = os.getenv("TECH_SUPPORT")
    SUGGESTION = os.getenv("SUGGESTION")

ADMINS = []
for admin in (ADMINS_env or "").split(","):
    admin = admin.strip()
    if admin.isdigit():
        ADMINS.append(admin)

MAX_TRIES = 3
logger = logging.getLogger(__name__)

# Функции

async def init_db():
    async with aiosqlite.connect(USERS_DB) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id   INTEGER PRIMARY KEY,   
                nick      TEXT NOT NULL,         
                joined_at INTEGER NOT NULL       
            )
        """)
        await db.commit()

async def save_user(user_id: int, nick: str):
    async with aiosqlite.connect(USERS_DB) as db:
        await db.execute(
            "INSERT OR REPLACE INTO users (user_id, nick, joined_at) VALUES (?, ?, ?)",
            (user_id, nick.lower(), int(time.time()))
        )
        await db.commit()

async def get_nick(user_id: int):
    async with aiosqlite.connect(USERS_DB) as db:
        cur = await db.execute("SELECT nick FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        return row[0] if row else None

async def demote(nick: str, new_group: str, duration: str) -> bool:
    # --- ДЕМО-РЕЖИМ ---
    if DEMO_MODE:
        await asyncio.sleep(0.5)
        return True
    # --- ---------- ---

    if await run_command("list") is None:
        return False

    await run_command(f"lp user {nick} parent addtemp {new_group} {duration}")
    for group in ["vip", "premium", "admin"]:
        if group != new_group:
            await run_command(f"lp user {nick} parent remove {group}")
            await run_command(f"lp user {nick} parent removetemp {group}")
    return True

def check_sha256(password: str, stored: str) -> bool:
    parts = stored.split("$")
    if len(parts) != 4 or parts[1] != "SHA":
        return False
    _, _, salt, hashed = parts
    first = hashlib.sha256(password.encode()).hexdigest()
    return hashlib.sha256((first + salt).encode()).hexdigest() == hashed

async def check_login(nick: str, password: str) -> bool:
    # --- ДЕМО-РЕЖИМ ---
    if DEMO_MODE:
        return nick.lower() in ["steve", "alex", "herobrine", "notch"] and password == "123456"
    # --- ---------- ---

    async with aiosqlite.connect(AUTH_ME_DB) as db:
        row = await (
            await db.execute(
                "SELECT password FROM authme WHERE username = ?", (nick.lower(),)
            )
        ).fetchone()
    return row is not None and check_sha256(password, row[0])

async def unblock_user(user_id: int):
    async with aiosqlite.connect(USERS_DB) as db:
        await db.execute("DELETE FROM blocked_users WHERE user_id = ?", (user_id,))
        await db.commit()

async def redeem_code(code: str):
    code_hash = hashlib.sha256(code.encode("utf-8")).hexdigest()
    async with aiosqlite.connect(LINKS_DB) as db:
        row = await (await db.execute(
            "SELECT nickname FROM link_codes WHERE code_hash = ? AND expires_at > ?",
            (code_hash, int(time.time()))
        )).fetchone()
        if row is None:
            return None
        await db.execute("DELETE FROM link_codes WHERE code_hash = ?", (code_hash,))
        await db.commit()
        return row[0]

async def check_nickname(nick: str) -> bool:
    # --- ДЕМО-РЕЖИМ ---
    if DEMO_MODE:
        return nick.lower() in ["steve", "alex", "herobrine", "notch"]
    # --- ---------- ---

    async with aiosqlite.connect(AUTH_ME_DB) as db:
        nick_lower = nick.lower()
        row = await (await db.execute("SELECT 1 FROM authme WHERE username = ?", (nick_lower, ))).fetchone()
        if row is None:
            return False
        return True

def format_russian_date(raw_date) -> str:
    if isinstance(raw_date, str):
        dt = datetime.strptime(raw_date.split(".")[0], "%Y-%m-%d %H:%M:%S")
    else:
        dt = datetime.fromtimestamp(raw_date)

    months = {
        1: "января", 2: "февраля", 3: "марта", 4: "апреля",
        5: "мая", 6: "июня", 7: "июля", 8: "августа",
        9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
    }

    return f"{dt.day} {months[dt.month]} {dt.year} года в {dt.strftime('%H:%M')}"

async def clear_database() -> bool:
    try:
        async with aiosqlite.connect(USERS_DB) as db:
            await db.execute("PRAGMA foreign_keys = OFF;")

            async with db.execute("SELECT name FROM sqlite_master WHERE type='table';") as cursor:
                tables = await cursor.fetchall()

            for table in tables:
                table_name = table[0]
                if table_name != "sqlite_sequence":
                    await db.execute(f"DROP TABLE IF EXISTS {table_name}")

            await db.commit()

        await init_db()
        await blocked_users.init_db()

        return True

    except Exception as e:
        logger.error(f"Ошибка при чистке таблиц БД: {e}")
        return False

# Обработчики

@router_bot.message(Command("start"))
async def start(message: Message):
    await message.answer(f"Привет я бот-магазин OurVillage! 🛍️", reply_markup=keyboards.keyboard_reg_inline)

@router_bot.callback_query(F.data == keyboards.btn_reg_inline.callback_data)
async def choose_auth(callback: CallbackQuery):
    async with aiosqlite.connect(USERS_DB) as db:
        cur = await db.execute("SELECT 1 FROM users WHERE user_id = ? LIMIT 1", (callback.from_user.id, ))
        row = await cur.fetchone()
    if row is not None:
        await callback.message.answer("Вы уже вошли в аккаунт, главное меню:", reply_markup=keyboards.keyboard_menu_reply)
        await callback.answer()
        return
    await callback.message.edit_text("Выберите способ авторизации:", reply_markup=keyboards.keyboard_choose_auth_inline)
    await callback.answer()

@router_bot.callback_query(F.data == keyboards.btn_auth_link_inline.callback_data)
async def auth_link(callback: CallbackQuery):
    await callback.message.answer(
        "Зайди на сервер, напиши /link и пришли сюда код командой:\n/link 123456"
    )
    await callback.answer()

@router_bot.message(Command("link"))
async def link_cmd(message: Message, command: CommandObject):
    code = (command.args or "").strip()  # всё, что после /link
    if not (code.isdigit() and len(code) == 6):
        await message.answer("Напиши код после команды, например: /link 123456")
        return

    nick = await redeem_code(code)
    if nick is None:
        await message.answer("Код неверный или устарел. Напиши /link на сервере ещё раз.")
        return

    await save_user(message.from_user.id, nick)
    await message.answer(f"Готово! Аккаунт {nick} привязан ✅")
    await message.answer("Главное меню:", reply_markup=keyboards.keyboard_menu_reply)

@router_bot.callback_query(F.data == keyboards.btn_auth_password_inline.callback_data)
async def auth_password(callback: CallbackQuery, state: FSMContext):
    left = await blocked_left(callback.from_user.id)
    if DEMO_MODE and left > 0:
        minutes = (left + 59) // 60
        await callback.message.answer(f"Слишком много попыток. Подождите {minutes} мин. Пропишите /unblock для сброса попыток")
        await callback.answer()
        return
    elif left > 0:
        minutes = (left + 59) // 60
        await callback.message.answer(f"Слишком много попыток. Подождите {minutes} мин.")
        await callback.answer()
        return

    await callback.message.answer("Введите ваш игровой никнейм:")
    await state.set_state(Form_user.nickname)
    await callback.answer()

@router_bot.message(Form_user.nickname, F.text)
async def nickname(message: Message, state: FSMContext):
    nick = message.text
    if await check_nickname(nick):
        await state.update_data(nickname=nick)
        msg = await message.answer("Отлично, теперь введите пароль:")
        await state.update_data(bot_msg_id_password=msg.message_id)
        await state.set_state(Form_user.password)
        return

    tries = await state.get_value("tries_nick", 0) + 1
    left = MAX_TRIES - tries
    if DEMO_MODE and left <= 0:
        await message.answer("Попытки закончились. Попробуйте позже. Пропишите /unblock для сброса попыток")
        await block_user(message.from_user.id, 5 * 60)
        await state.clear()
    elif left <= 0:
        await message.answer("Попытки закончились. Попробуйте позже.")
        await block_user(message.from_user.id, 5 * 60)
        await state.clear()
    elif left == 1:
        await message.answer("Игрок с таким ником не зарегистрирован на сервере.\nОсталась 1 попытка.")
        await state.update_data(tries_nick=tries)
    else:
        await message.answer("Игрок с таким ником не зарегистрирован на сервере.\nПопробуйте ещё раз.")
        await state.update_data(tries_nick=tries)


@router_bot.message(Form_user.password, F.text)
async def password(message: Message, state: FSMContext, bot: Bot):
    user_password = message.text
    previous_msg = await state.get_value("bot_msg_id_password")
    await message.delete()
    nick = await state.get_value("nickname")
    if await check_login(nick, user_password):
        await save_user(message.from_user.id, nick=nick)
        await bot.edit_message_text(
            text=f"Готово! Аккаунт {nick} привязан ✅",
            chat_id=message.chat.id,
            message_id=previous_msg
        )
        await message.answer("Главное меню:", reply_markup=keyboards.keyboard_menu_reply)
        await state.clear()
        return

    tries = await state.get_value("tries", 0) + 1
    left = MAX_TRIES - tries
    if left <= 0:
        if DEMO_MODE:
            await bot.edit_message_text(
                text="Попытки закончились. Попробуйте позже. Пропишите /unblock для сброса попыток",
                chat_id=message.chat.id,
                message_id=previous_msg
            )
            await block_user(message.from_user.id, 15 * 60)
            await state.clear()
        else:
            await bot.edit_message_text(
                text="Попытки закончились. Попробуйте позже.",
                chat_id=message.chat.id,
                message_id=previous_msg
            )
            await block_user(message.from_user.id, 15 * 60)
            await state.clear()
    elif left == 1:
        await bot.edit_message_text(
            text="Неверный пароль! Осталась 1 попытка.",
            chat_id=message.chat.id,
            message_id=previous_msg
        )
        await state.update_data(tries=tries)
    else:
        await bot.edit_message_text(
            text="Неверный пароль! Попробуйте ещё раз.",
            chat_id=message.chat.id,
            message_id=previous_msg
        )
        await state.update_data(tries=tries)

@router_bot.callback_query(F.data == keyboards.btn_shop_return_inline.callback_data)
async def return_into_shop(callback: CallbackQuery):
    await callback.message.edit_text("Вот список товаров, возможные для покупки на нашем сервере: ", reply_markup=keyboards.keyboard_shop_menu_inline)
    await callback.answer()

@router_bot.message(Command("unblock"))
async def unblock(message: Message, command: CommandObject):
    if DEMO_MODE:
        await unblock_user(message.from_user.id)
        await message.answer("Вы успешно разблокированы! Попробуйте ввести никнейм или пароль снова /start.")
        return
    if message.from_user.id not in ADMINS:
        return
    await unblock_user(message.from_user.id)
    await message.answer("Вы разблокированы.")

@router_bot.message(Command("reset_db"))
async def cmd_reset_db(message: Message):
    if message.from_user.id not in ADMINS:
        return

    await message.answer("⏳ Начинаю очистку таблиц базы данных...")

    is_success = await clear_database()

    if is_success:
        await message.answer("✅ База данных успешно очищена! Все таблицы пересозданы с нуля.")
    else:
        await message.answer("❌ Произошла ошибка при очистке базы данных. Проверьте логи в Railway.")


# ------ Меню ------

@router_bot.message(F.text == keyboards.btn_shop.text)
async def shop(message: Message):
    await message.answer("Вот список товаров, возможные для покупки на нашем сервере: ", reply_markup=keyboards.keyboard_shop_menu_inline)


@router_bot.message(F.text == keyboards.btn_about_me.text)
async def about_me(message: Message):
    user_id = message.from_user.id

    async with aiosqlite.connect(USERS_DB) as db:
        async with db.execute(
                "SELECT joined_at, nick FROM users WHERE user_id = ? LIMIT 1",
                (user_id,)
        ) as cursor:
            row = await cursor.fetchone()

    if row is not None:
        joined_at, nick = row
        joined_date = format_russian_date(joined_at)
        connected_account = "Не подключен"

        if nick:
            # --- ДЕМО-РЕЖИМ ---
            if DEMO_MODE:
                connected_account = nick.capitalize()
            # --- ---------- ---
            else:
                async with aiosqlite.connect(AUTH_ME_DB) as db:
                    async with db.execute(
                            "SELECT realname FROM authme WHERE username = ? LIMIT 1",
                            (nick,)
                    ) as auth_cursor:
                        auth_row = await auth_cursor.fetchone()
                        if auth_row:
                            connected_account = auth_row[0]

        await message.answer(
            f"📋 Информация о пользователе с ID - {user_id}:\n"
            f"📅 Присоединился - {joined_date}\n"
            f"🎮 Подключенный аккаунт - {connected_account}"
        )
    else:
        await message.answer("Профиль не найден.")

@router_bot.message(F.text == keyboards.btn_tech_support.text)
async def tech_support(message: Message):
    await message.answer(f"Тех. поддержка - {TECH_SUPPORT}")

@router_bot.message(F.text == keyboards.btn_suggestions.text)
async def suggestion(message: Message):
    await message.answer(f"Предложить идею - {SUGGESTION}")

# ------ Привилегии ------

@router_bot.callback_query(F.data == keyboards.btn_privileges_inline.callback_data)
async def privileges(callback: CallbackQuery):
    await callback.message.edit_text("Вот привилегии, доступные для покупки:", reply_markup=keyboards.keyboard_shop_privileges_inline)
    await callback.answer()

@router_bot.callback_query(F.data == keyboards.btn_privileges_vip_inline.callback_data)
async def vip(callback: CallbackQuery):
    nick = await get_nick(callback.from_user.id)
    if nick is None:
        await callback.message.answer("Вы не привязали игровой аккаунт!", reply_markup=keyboards.keyboard_reg_inline)
        await callback.answer()
        return

    if await demote(nick, "vip", "1m"):
        await callback.message.answer("Готово ✅")
    else:
        await callback.message.answer("Сервер сейчас выключен, попробуй позже 🔴")
    await callback.answer()

@router_bot.callback_query(F.data == keyboards.btn_privileges_premium_inline.callback_data)
async def premium(callback: CallbackQuery):
    nick = await get_nick(callback.from_user.id)
    if nick is None:
        await callback.message.answer("Вы не привязали игровой аккаунт!", reply_markup=keyboards.keyboard_reg_inline)
        await callback.answer()
        return

    if await demote(nick, "premium", "1m"):
        await callback.message.answer("Готово ✅")
    else:
        await callback.message.answer("Сервер сейчас выключен, попробуй позже 🔴")
    await callback.answer()


@router_bot.callback_query(F.data == keyboards.btn_privileges_elite_inline.callback_data)
async def elite(callback: CallbackQuery):
    nick = await get_nick(callback.from_user.id)
    if nick is None:
        await callback.message.answer("Вы не привязали игровой аккаунт!", reply_markup=keyboards.keyboard_reg_inline)
        await callback.answer()
        return

    if await demote(nick, "elite", "1m"):
        await callback.message.answer("Готово ✅")
    else:
        await callback.message.answer("Сервер сейчас выключен, попробуй позже 🔴")
    await callback.answer()

# ------ Токены ------

@router_bot.callback_query(F.data == keyboards.btn_tokens_inline.callback_data)
async def tokens(callback: CallbackQuery):
    await callback.message.edit_text("Выберите кол-во токенов, которое вы хотите приобрести: ", reply_markup=keyboards.keyboard_shop_tokens_inline)
    await callback.answer()

@router_bot.callback_query(F.data.startswith("tokens_"))
async def buy_tokens(callback: CallbackQuery):
    amount = int(callback.data.split("_")[1])   # "tokens_500" -> 500
    await callback.message.answer(f"На счёт Вашего игрового аккаунта успешно пополнено {amount} токенов!")
    await callback.answer()

# ------ Кейсы ------

@router_bot.callback_query(F.data == keyboards.btn_donat_boxs_inline.callback_data)
async def donat_boxs(callback: CallbackQuery):
    await callback.message.edit_text("Вот кейсы, доступные для покупки:", reply_markup=keyboards.keyboard_shop_boxs_inline)
    await callback.answer()

@router_bot.callback_query(F.data == keyboards.btn_boxs_privileges_inline.callback_data)
async def boxs_privileges(callback: CallbackQuery):
    await callback.message.answer("На счёт Вашего игрового аккаунта успешно добавлен 1 кейс с привилегиями!")
    await callback.answer()

@router_bot.callback_query(F.data == keyboards.btn_boxs_tokens_inline.callback_data)
async def boxs_tokens(callback: CallbackQuery):
    await callback.message.answer("На счёт Вашего игрового аккаунта успешно добавлен 1 кейс с токенами!")
    await callback.answer()

@router_bot.callback_query(F.data == keyboards.btn_boxs_money_inline.callback_data)
async def boxs_money(callback: CallbackQuery):
    await callback.message.answer("На счёт Вашего игрового аккаунта успешно добавлен 1 кейс с монетами!")
    await callback.answer()