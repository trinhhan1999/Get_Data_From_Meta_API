# -*- coding: utf-8 -*-
"""
Add clicks column to existing tables
"""
import logging
from sqlalchemy import create_engine, text
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_clicks_column():
    """Add clicks column to all ad account tables"""
    engine = create_engine(Config.DATABASE_URL, echo=False)
    
    tables = []
    for account in Config.AD_ACCOUNTS:
        tables.append(account['table_name'])
    
    with engine.connect() as conn:
        for table_name in tables:
            try:
                # Check if column already exists
                check_sql = text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='{table_name}' AND column_name='clicks'
                """)
                result = conn.execute(check_sql)
                
                if result.fetchone():
                    logger.info(f"Column 'clicks' already exists in {table_name}")
                    continue
                
                # Add clicks column after frequency
                alter_sql = text(f"""
                    ALTER TABLE {table_name} 
                    ADD COLUMN clicks BIGINT DEFAULT 0
                """)
                conn.execute(alter_sql)
                conn.commit()
                logger.info(f"Added 'clicks' column to {table_name}")
                
            except Exception as e:
                logger.error(f"Error adding column to {table_name}: {e}")
                conn.rollback()
    
    logger.info("Migration completed")


if __name__ == '__main__':
    add_clicks_column()
