import asyncpg
from app.core.config import settings

pool: asyncpg.Pool | None = None

async def init_pool():
    global pool
    pool = await asyncpg.create_pool(
        settings.database_url,
        min_size=5,
        max_size=20,
    )

async def close_pool():
    await pool.close()

async def get_pool() -> asyncpg.Pool:
    return pool