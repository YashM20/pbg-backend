import logging
import sentry_sdk
from app.core.config import settings

logger = logging.getLogger(__name__)


def init_sentry() -> None:
    """Initialize Sentry SDK with settings configuration."""
    if not settings.sentry_dsn:
        logger.info("Sentry DSN is not set. Sentry monitoring is disabled.")
        return

    try:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            send_default_pii=settings.sentry_send_default_pii,
            enable_logs=settings.sentry_enable_logs,
            traces_sample_rate=settings.sentry_traces_sample_rate,
            profile_session_sample_rate=settings.sentry_profile_session_sample_rate,
            profile_lifecycle=settings.sentry_profile_lifecycle,
        )
        logger.info("Sentry SDK initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Sentry SDK: {e}", exc_info=True)
