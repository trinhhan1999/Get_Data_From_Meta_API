# -*- coding: utf-8 -*-
"""
Excel Export Module - Multi Account Support
"""
import logging
import os
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExcelExporter:
    """Class to export data to Excel"""
    
    def __init__(self, export_folder: Path = None, filename: str = None):
        self.export_folder = Path(export_folder or Config.EXPORT_FOLDER)
        self.filename = filename or Config.EXCEL_FILENAME
        self.export_folder.mkdir(parents=True, exist_ok=True)
        logger.info(f"Excel exporter initialized. Export folder: {self.export_folder}")
    
    def get_export_path(self) -> Path:
        return self.export_folder / self.filename
    
    def delete_existing_file(self) -> bool:
        file_path = self.get_export_path()
        if file_path.exists():
            os.remove(file_path)
            logger.info(f"Deleted existing file: {file_path}")
            return True
        return False
    
    def export_to_excel(self, data: List[Dict[str, Any]]) -> Path:
        """Export data to Excel"""
        self.delete_existing_file()
        file_path = self.get_export_path()
        
        if not data:
            logger.warning("No data to export")
            return file_path
        
        df = pd.DataFrame(data)
        
        column_mapping = {
            'account_id': 'Account ID',
            'account_name': 'Account name',
            'campaign_name': 'Campaign name',
            'adset_name': 'Adset Name',
            'ad_id': 'ADS ID',
            'ad_name': 'Ad Name',
            'day': 'Day',
            'amount_spent': 'Amount spent',
            'impressions': 'Impressions',
            'reach': 'Reach',
            'frequency': 'Frequency',
            'cpc_all': 'CPC (all)',
            'cpc_link_click': 'CPC (cost per link click)',
            'ctr_all': 'CTR (all)',
            'ctr_link_click': 'CTR (link click-through rate)',
            'cpm': 'CPM (cost per 1,000 impressions)',
            'link_clicks': 'Link clicks',
            'cost_per_result': 'Cost Per Result',
            'landing_page_views': 'Landing page views',
            'cost_per_landing_page_view': 'Cost per landing page view',
            'leads': 'Leads',
            'leads_conversion_value': 'Leads Conversion Value',
            'messaging_conversations_started': 'Messaging conversations started',
            'adds_to_cart': 'Adds to cart',
            'website_adds_to_cart': 'Website adds to cart',
            'adds_to_cart_conversion_value': 'Adds to cart conversion value',
            'checkouts_initiated': 'Checkouts Initiated',
            'checkouts_initiated_conversion_value': 'Checkouts initiated conversion value',
            'purchases': 'Purchases',
            'website_purchases': 'Website purchases',
            'purchases_conversion_value': 'Purchases conversion value',
            'website_purchases_conversion_value': 'Website purchases conversion value',
            'post_comments': 'Post comments',
        }
        
        df = df.rename(columns=column_mapping)
        
        desired_order = [
            'ADS ID', 'Day', 'Campaign name', 'Amount spent', 'CPC (all)',
            'CPC (cost per link click)', 'CTR (all)', 'CPM (cost per 1,000 impressions)',
            'Post comments', 'Link clicks', 'Messaging conversations started',
            'Landing page views', 'Cost per landing page view', 'Website adds to cart',
            'Checkouts Initiated', 'Website purchases conversion value', 'Impressions',
            'Website purchases', 'Leads', 'Leads Conversion Value', 'Reach',
            'Purchases conversion value', 'Cost Per Result', 'Purchases',
            'Adds to cart conversion value', 'Checkouts initiated conversion value',
            'Adds to cart', 'Frequency', 'CTR (link click-through rate)',
            'Account ID', 'Account name', 'Adset Name', 'Ad Name'
        ]
        
        existing_cols = [col for col in desired_order if col in df.columns]
        other_cols = [col for col in df.columns if col not in desired_order and col != 'id' and col != 'fetched_at']
        df = df[existing_cols + other_cols]
        
        if 'Day' in df.columns:
            df = df.sort_values('Day', ascending=False)
        
        df.to_excel(file_path, index=False, sheet_name='Facebook Ads Data')
        
        logger.info(f"Exported {len(data)} records to {file_path}")
        return file_path
