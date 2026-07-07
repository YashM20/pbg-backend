import logging
import asyncpg
from app.core.config import settings

logger = logging.getLogger(__name__)
pool: asyncpg.Pool | None = None


async def init_pool():
    global pool
    logger.info("Initializing database connection pool...")
    try:
        pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=5,
            max_size=20,
        )
        logger.info("Database connection pool initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database connection pool: {e}", exc_info=True)
        raise


async def close_pool():
    global pool
    if pool is not None:
        logger.info("Closing database connection pool...")
        await pool.close()
        logger.info("Database connection pool closed successfully.")

async def get_pool() -> asyncpg.Pool | None:
    return pool