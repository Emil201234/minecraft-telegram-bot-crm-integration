import time, aiosqlite

DB = "bot.db"

async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS blocked_users (user_id INTEGER PRIMARY KEY, until REAL NOT NULL)")
        await db.commit()

async def block_user(user_id: int, seconds: int):
    async with aiosqlite.connect(DB) as db:
        await db.execute("INSERT OR REPLACE INTO blocked_users (user_id, until) VALUES (?, ?)", (user_id, time.time() + seconds))
        await db.commit()

async def blocked_left(user_id: int):
    async with aiosqlite.connect(DB) as db:
        cursor = await db.execute("SELECT until FROM blocked_users WHERE user_id = ?", (user_id, ))
        row = await cursor.fetchone()
    if row is None:
        return 0
    return max(0, int(row[0] - time.time()))


