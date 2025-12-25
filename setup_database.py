"""
Setup Database
Script d? t?o table trong PostgreSQL
"""
import logging
from database import Base, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_database():
    """T?o table trong database"""
    logger.info("Creating database tables...")
    
    # Drop all tables first (if needed for fresh start)
    # Base.metadata.drop_all(engine)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    logger.info("Database tables created successfully!")
    logger.info("Table created: facebook_ads_data")


if __name__ == "__main__":
    setup_database()
