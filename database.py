# -*- coding: utf-8 -*-
"""
PostgreSQL Database Module - Multi Account Support
"""
import logging
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, BigInteger, Date, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()
metadata = MetaData()


def create_ads_table(table_name: str):
    """Create a table dynamically for each ad account"""
    return Table(
        table_name, metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('account_id', String(50)),
        Column('account_name', String(500)),
        Column('campaign_name', String(500)),
        Column('adset_name', String(500)),
        Column('ad_id', String(50), index=True),
        Column('ad_name', String(500)),
        Column('day', Date, index=True),
        Column('amount_spent', Float, default=0),
        Column('impressions', BigInteger, default=0),
        Column('reach', BigInteger, default=0),
        Column('frequency', Float, default=0),
        Column('cpc_all', Float, default=0),
        Column('cpc_link_click', Float, default=0),
        Column('ctr_all', Float, default=0),
        Column('ctr_link_click', Float, default=0),
        Column('cpm', Float, default=0),
        Column('link_clicks', BigInteger, default=0),
        Column('cost_per_result', Float, default=0),
        Column('landing_page_views', BigInteger, default=0),
        Column('cost_per_landing_page_view', Float, default=0),
        Column('leads', BigInteger, default=0),
        Column('leads_conversion_value', Float, default=0),
        Column('messaging_conversations_started', BigInteger, default=0),
        Column('adds_to_cart', BigInteger, default=0),
        Column('website_adds_to_cart', BigInteger, default=0),
        Column('adds_to_cart_conversion_value', Float, default=0),
        Column('checkouts_initiated', BigInteger, default=0),
        Column('checkouts_initiated_conversion_value', Float, default=0),
        Column('purchases', BigInteger, default=0),
        Column('website_purchases', BigInteger, default=0),
        Column('purchases_conversion_value', Float, default=0),
        Column('website_purchases_conversion_value', Float, default=0),
        Column('post_comments', BigInteger, default=0),
        Column('fetched_at', DateTime, default=datetime.utcnow),
        extend_existing=True
    )


# Create engine and session
engine = create_engine(Config.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


class DatabaseManager:
    """Database operations manager for specific table"""
    
    def __init__(self, table_name: str = 'facebook_ads_data'):
        self.table_name = table_name
        self.table = create_ads_table(table_name)
        self.session = SessionLocal()
        logger.info(f"Database connection established for table: {table_name}")
    
    def create_table(self):
        """Create table if not exists"""
        self.table.create(engine, checkfirst=True)
        logger.info(f"Table {self.table_name} created/verified")
    
    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()
    
    def insert_data(self, data_list: List[Dict[str, Any]]) -> int:
        """Insert data into table"""
        count = 0
        for data in data_list:
            try:
                insert_stmt = self.table.insert().values(
                    account_id=data.get('account_id'),
                    account_name=data.get('account_name'),
                    campaign_name=data.get('campaign_name'),
                    adset_name=data.get('adset_name'),
                    ad_id=data.get('ad_id'),
                    ad_name=data.get('ad_name'),
                    day=data.get('day'),
                    amount_spent=data.get('amount_spent', 0),
                    impressions=data.get('impressions', 0),
                    reach=data.get('reach', 0),
                    frequency=data.get('frequency', 0),
                    cpc_all=data.get('cpc_all', 0),
                    cpc_link_click=data.get('cpc_link_click', 0),
                    ctr_all=data.get('ctr_all', 0),
                    ctr_link_click=data.get('ctr_link_click', 0),
                    cpm=data.get('cpm', 0),
                    link_clicks=data.get('link_clicks', 0),
                    cost_per_result=data.get('cost_per_result', 0),
                    landing_page_views=data.get('landing_page_views', 0),
                    cost_per_landing_page_view=data.get('cost_per_landing_page_view', 0),
                    leads=data.get('leads', 0),
                    leads_conversion_value=data.get('leads_conversion_value', 0),
                    messaging_conversations_started=data.get('messaging_conversations_started', 0),
                    adds_to_cart=data.get('adds_to_cart', 0),
                    website_adds_to_cart=data.get('website_adds_to_cart', 0),
                    adds_to_cart_conversion_value=data.get('adds_to_cart_conversion_value', 0),
                    checkouts_initiated=data.get('checkouts_initiated', 0),
                    checkouts_initiated_conversion_value=data.get('checkouts_initiated_conversion_value', 0),
                    purchases=data.get('purchases', 0),
                    website_purchases=data.get('website_purchases', 0),
                    purchases_conversion_value=data.get('purchases_conversion_value', 0),
                    website_purchases_conversion_value=data.get('website_purchases_conversion_value', 0),
                    post_comments=data.get('post_comments', 0),
                    fetched_at=datetime.utcnow()
                )
                self.session.execute(insert_stmt)
                count += 1
            except Exception as e:
                logger.error(f"Error inserting record: {e}")
                continue
        
        self.session.commit()
        logger.info(f"Inserted {count} records into {self.table_name}")
        return count
    
    def get_all_data(self) -> List[Dict[str, Any]]:
        """Get all data from table"""
        result = self.session.execute(
            self.table.select().order_by(self.table.c.day.desc())
        )
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]
    
    def clear_all_data(self):
        """Clear all data from table"""
        self.session.execute(self.table.delete())
        self.session.commit()
        logger.info(f"Cleared all data from {self.table_name}")


def setup_all_tables():
    """Create tables for all configured ad accounts"""
    for account in Config.AD_ACCOUNTS:
        table = create_ads_table(account['table_name'])
        table.create(engine, checkfirst=True)
        logger.info(f"Table {account['table_name']} created for {account['name']}")
