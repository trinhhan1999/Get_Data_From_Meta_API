# -*- coding: utf-8 -*-
"""
Facebook Ads API Client - Multi Account Support
"""
import logging
from datetime import datetime
from typing import List, Dict, Any
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FacebookAdsClient:
    """Facebook Ads API Client"""
    
    def __init__(self, ad_account_id: str = None):
        Config.validate(ad_account_id)
        
        FacebookAdsApi.init(
            app_id=Config.FACEBOOK_APP_ID,
            app_secret=Config.FACEBOOK_APP_SECRET,
            access_token=Config.FACEBOOK_ACCESS_TOKEN
        )
        
        self.ad_account_id = ad_account_id or Config.AD_ACCOUNT_ID
        self.ad_account = AdAccount(self.ad_account_id)
        logger.info(f"Facebook Ads API initialized for account: {self.ad_account_id}")
    
    def get_ads_data(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch ads insights data"""
        logger.info(f"Fetching ads data from {start_date} to {end_date}")
        
        params = {
            'level': 'ad',
            'time_range': {
                'since': start_date,
                'until': end_date
            },
            'time_increment': 1,
            'fields': Config.INSIGHTS_FIELDS,
        }
        
        try:
            insights = self.ad_account.get_insights(params=params)
            
            results = []
            for insight in insights:
                parsed = self._parse_insight(insight)
                results.append(parsed)
            
            logger.info(f"Fetched {len(results)} records")
            return results
            
        except Exception as e:
            logger.error(f"Error fetching ads data: {e}")
            raise
    
    def _parse_insight(self, insight) -> Dict[str, Any]:
        """Parse insight data"""
        data = dict(insight)
        
        # Extract actions
        actions = {}
        if 'actions' in data:
            for action in data.get('actions', []):
                action_type = action.get('action_type', '')
                action_value = float(action.get('value', 0))
                actions[action_type] = action_value
        
        # Extract action values
        action_values = {}
        if 'action_values' in data:
            for av in data.get('action_values', []):
                action_type = av.get('action_type', '')
                action_value = float(av.get('value', 0))
                action_values[action_type] = action_value
        
        # Extract cost per action
        cost_per_action = {}
        if 'cost_per_action_type' in data:
            for cpa in data.get('cost_per_action_type', []):
                action_type = cpa.get('action_type', '')
                cost = float(cpa.get('value', 0))
                cost_per_action[action_type] = cost
        
        return {
            'account_id': data.get('account_id'),
            'account_name': data.get('account_name'),
            'campaign_name': data.get('campaign_name'),
            'adset_name': data.get('adset_name'),
            'ad_id': data.get('ad_id'),
            'ad_name': data.get('ad_name'),
            'day': data.get('date_start'),
            'amount_spent': float(data.get('spend', 0)),
            'impressions': int(data.get('impressions', 0)),
            'reach': int(data.get('reach', 0)),
            'frequency': float(data.get('frequency', 0)),
            'cpc_all': float(data.get('cpc', 0)),
            'cpc_link_click': float(data.get('cost_per_inline_link_click', 0)),
            'ctr_all': float(data.get('ctr', 0)),
            'ctr_link_click': float(data.get('inline_link_click_ctr', 0)),
            'cpm': float(data.get('cpm', 0)),
            'link_clicks': int(data.get('inline_link_clicks', 0)),
            'cost_per_result': cost_per_action.get('omni_purchase', cost_per_action.get('purchase', 0)),
            'landing_page_views': int(actions.get('landing_page_view', 0)),
            'cost_per_landing_page_view': cost_per_action.get('landing_page_view', 0),
            'leads': int(actions.get('lead', 0)),
            'leads_conversion_value': action_values.get('lead', 0),
            'messaging_conversations_started': int(actions.get('onsite_conversion.messaging_conversation_started_7d', 0)),
            'adds_to_cart': int(actions.get('omni_add_to_cart', 0)),
            'website_adds_to_cart': int(actions.get('add_to_cart', 0)),
            'adds_to_cart_conversion_value': action_values.get('omni_add_to_cart', 0),
            'checkouts_initiated': int(actions.get('omni_initiated_checkout', 0)),
            'checkouts_initiated_conversion_value': action_values.get('omni_initiated_checkout', 0),
            'purchases': int(actions.get('omni_purchase', 0)),
            'website_purchases': int(actions.get('purchase', 0)),
            'purchases_conversion_value': action_values.get('omni_purchase', 0),
            'website_purchases_conversion_value': action_values.get('purchase', 0),
            'post_comments': int(actions.get('post_comment', actions.get('comment', 0))),
        }
