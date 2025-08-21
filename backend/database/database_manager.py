import logging
from sqlalchemy import create_engine

from .models import Base
from config.settings import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(
            settings.database_url
        )

    def init_db(self):
        """Initialize database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise


db_manager = DatabaseManager()