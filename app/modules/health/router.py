import logging
from fastapi import APIRouter, HTTPException, status
from app.core.db import get_pool

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("", tags=["health"])
async def health_check():
    try:
        db_pool = await get_pool()
        if db_pool is None:
            logger.error("Database pool is not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection is not initialized"
            )
        
        # Test connection with a timeout of 2.0 seconds
        val = await db_pool.fetchval("SELECT 1", timeout=2.0)
        if val != 1:
            logger.error(f"Database health check returned unexpected value: {val}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unexpected response from database"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database health check failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failure"
        )
    return {"status": "healthy", "database": "connected"}
