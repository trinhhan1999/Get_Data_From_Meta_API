"""
Configuration module for Facebook Ads Data Pipeline
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for the application"""
    
    # Facebook API Configuration
    FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
    FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')
    FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')
    
    # Multiple Ad Accounts Configuration
    AD_ACCOUNTS = []
    
    # Load Ad Account 1
    if os.getenv('AD_ACCOUNT_ID_1'):
        AD_ACCOUNTS.append({
            'id': os.getenv('AD_ACCOUNT_ID_1'),
            'name': os.getenv('AD_ACCOUNT_NAME_1', 'Account1'),
            'table_name': 'facebook_ads_cpas_shopee',
            'excel_filename': 'CPAS_Shopee_Shondo.xlsx',
            'sheet_name': os.getenv('AD_ACCOUNT_SHEET_1', 'CPAS_Shopee_Shondo')
        })
    
    # Load Ad Account 2
    if os.getenv('AD_ACCOUNT_ID_2'):
        AD_ACCOUNTS.append({
            'id': os.getenv('AD_ACCOUNT_ID_2'),
            'name': os.getenv('AD_ACCOUNT_NAME_2', 'Account2'),
            'table_name': 'facebook_ads_onlinestore',
            'excel_filename': 'OnlineStore_Shondo.xlsx',
            'sheet_name': os.getenv('AD_ACCOUNT_SHEET_2', 'OnlineStore_Shondo')
        })
    
    # Backward compatibility
    AD_ACCOUNT_ID = os.getenv('AD_ACCOUNT_ID') or (AD_ACCOUNTS[0]['id'] if AD_ACCOUNTS else None)
    
    # PostgreSQL Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'facebook_ads_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    
    # Database URL
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Export Configuration
    EXPORT_FOLDER = Path(os.getenv('EXPORT_FOLDER', 'D:/Get_Data_From_Meta/exports'))
    EXCEL_FILENAME = os.getenv('EXCEL_FILENAME', 'facebook_ads_data.xlsx')
    
    # Google Sheets Configuration
    USE_GOOGLE_SHEETS = os.getenv('USE_GOOGLE_SHEETS', 'false').lower() == 'true'
    GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
    GOOGLE_SPREADSHEET_ID = os.getenv('GOOGLE_SPREADSHEET_ID', '')
    
    # Date Configuration
    DATE_PRESET = os.getenv('DATE_PRESET', 'last_30d')
    START_DATE = os.getenv('START_DATE')
    END_DATE = os.getenv('END_DATE')
    DEFAULT_DAYS_BACK = int(os.getenv('DEFAULT_DAYS_BACK', '7'))
    DAILY_RUN_TIME = os.getenv('DAILY_RUN_TIME', '06:00')
    
    # Facebook Ads API Fields - Tất cả fields cần fetch
    # Mapping: API Field -> Excel Column Name
    FIELDS_CONFIG = {
        # Account info
        'account_id': 'Account ID',
        'account_name': 'Account name',
        
        # Campaign, Adset, Ad info
        'campaign_name': 'Campaign name',
        'adset_name': 'Adset Name',
        'ad_id': 'ADS ID',
        'ad_name': 'Ad Name',
        'permalink': 'Permalink',
        'created_time': 'Created Time',
        'start_time': 'Start Time',
        
        # Date
        'date_start': 'Day',
        
        # Metrics cơ bản
        'spend': 'Amount spent',
        'impressions': 'Impressions',
        'reach': 'Reach',
        'frequency': 'Frequency',
        
        # Click metrics
        'clicks': 'Clicks (all)',
        'cpc': 'CPC (all)',
        'ctr': 'CTR (all)',
        'cpm': 'CPM (cost per 1,000 impressions)',
        'inline_link_clicks': 'Link clicks',
        'inline_link_click_ctr': 'CTR (link click-through rate)',
        'cost_per_inline_link_click': 'CPC (cost per link click)',
        
        # Actions (extracted from 'actions' field)
        'post_comment': 'Post comments',
        'link_click': 'Link clicks',
        'onsite_conversion.messaging_conversation_started_7d': 'Messaging conversations started',
        'landing_page_view': 'Landing page views',
        'cost_per_landing_page_view': 'Cost per landing page view',
        'omni_add_to_cart': 'Adds to cart',
        'add_to_cart': 'Website adds to cart',
        'omni_initiated_checkout': 'Checkouts Initiated',
        'omni_purchase': 'Purchases',
        'purchase': 'Website purchases',
        'lead': 'Leads',
        
        # Action values (conversion values)
        'lead_value': 'Leads Conversion Value',
        'omni_add_to_cart_value': 'Adds to cart conversion value',
        'omni_initiated_checkout_value': 'Checkouts initiated conversion value',
        'omni_purchase_value': 'Purchases conversion value',
        'purchase_value': 'Website purchases conversion value',
        
        # Cost per action
        'cost_per_result': 'Cost Per Result',
    }
    
    # Fields to request from Facebook API
    INSIGHTS_FIELDS = [
        'account_id', 'account_name',
        'campaign_name', 'adset_name', 'ad_id', 'ad_name',
        'date_start',
        'spend', 'impressions', 'reach', 'frequency',
        'clicks', 'cpc', 'ctr', 'cpm',
        'inline_link_clicks', 'inline_link_click_ctr', 'cost_per_inline_link_click',
        'actions', 'action_values', 'cost_per_action_type',
    ]
    
    @classmethod
    def validate(cls, ad_account_id=None):
        """Validate required configuration"""
        required_fields = [
            'FACEBOOK_ACCESS_TOKEN',
            'DB_PASSWORD'
        ]
        
        missing = []
        for field in required_fields:
            if not getattr(cls, field):
                missing.append(field)
        
        if not ad_account_id and not cls.AD_ACCOUNTS:
            missing.append('AD_ACCOUNT_ID')
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True
    
    @classmethod
    def ensure_export_folder(cls):
        """Create export folder if it doesn't exist"""
        cls.EXPORT_FOLDER.mkdir(parents=True, exist_ok=True)
        return cls.EXPORT_FOLDER
