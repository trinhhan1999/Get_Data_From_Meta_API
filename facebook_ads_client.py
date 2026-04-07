# -*- coding: utf-8 -*-
"""
Facebook Ads API Client - Multi Account Support
"""
import logging
from datetime import datetime, timedelta
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
        """Fetch ads insights data with automatic chunking for large date ranges"""
        logger.info(f"Fetching ads data from {start_date} to {end_date}")
        
        # Convert to datetime objects
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Calculate date range in days
        date_range_days = (end - start).days
        
        # If date range > 30 days, split into chunks
        if date_range_days > 30:
            logger.info(f"Large date range detected ({date_range_days} days). Splitting into 30-day chunks...")
            return self._fetch_data_in_chunks(start_date, end_date)
        else:
            return self._fetch_single_range(start_date, end_date)
    
    def _fetch_data_in_chunks(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch data in 30-day chunks to avoid API limits"""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        all_results = []
        current_start = start
        chunk_num = 0
        
        while current_start <= end:
            chunk_num += 1
            # Calculate chunk end (30 days from start or final end date)
            current_end = min(current_start + timedelta(days=29), end)
            
            chunk_start_str = current_start.strftime('%Y-%m-%d')
            chunk_end_str = current_end.strftime('%Y-%m-%d')
            
            logger.info(f"  Chunk {chunk_num}: Fetching {chunk_start_str} to {chunk_end_str}")
            
            try:
                chunk_results = self._fetch_single_range(chunk_start_str, chunk_end_str)
                all_results.extend(chunk_results)
                logger.info(f"  Chunk {chunk_num}: Got {len(chunk_results)} records")
            except Exception as e:
                logger.error(f"  Chunk {chunk_num}: Error - {e}")
                # Continue with next chunk even if one fails
            
            # Move to next chunk
            current_start = current_end + timedelta(days=1)
        
        logger.info(f"Total fetched: {len(all_results)} records from {chunk_num} chunks")
        return all_results
    
    def _fetch_single_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch data for a single date range"""
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
            ad_ids = set()
            for insight in insights:
                parsed = self._parse_insight(insight)
                results.append(parsed)
                if parsed.get('ad_id'):
                    ad_ids.add(parsed['ad_id'])
            
            # Fetch extra details for the unique ad_ids
            extra_details = self._fetch_ad_extra_details(list(ad_ids))
            for res in results:
                # Add the extra fields into the result
                ad_id = res.get('ad_id')
                details = extra_details.get(ad_id, {})
                res['permalink'] = details.get('permalink', '')
                res['created_time'] = details.get('created_time', '')
                res['start_time'] = details.get('start_time', '')
            
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
            'clicks': int(data.get('clicks', 0)),
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
        
    def _fetch_ad_extra_details(self, ad_ids: List[str]) -> Dict[str, Dict[str, str]]:
        """Fetch permalink, created_time, and start_time for a list of Ad IDs"""
        if not ad_ids:
            return {}
            
        details = {}
        # Get unique IDs to minimize calls
        unique_ad_ids = list(set(ad_ids))
        
        # API requires explicit fields
        chunk_size = 50
        api = FacebookAdsApi.get_default_api()
        
        for i in range(0, len(unique_ad_ids), chunk_size):
            chunk = unique_ad_ids[i:i+chunk_size]
            try:
                # Request multiple nodes at once using '?ids='
                response = api.call(
                    method='GET',
                    path=('?', ),
                    params={
                        'ids': ','.join(chunk),
                        'fields': 'preview_shareable_link,created_time,adset{start_time}'
                    }
                )
                if response.json():
                    for ad_id, ad_data in response.json().items():
                        adset_data = ad_data.get('adset', {})
                        
                        created_time = ad_data.get('created_time', '')
                        if created_time and 'T' in created_time:
                            created_time = created_time.split('T')[0]
                            
                        start_time = adset_data.get('start_time', '')
                        if start_time and 'T' in start_time:
                            start_time = start_time.split('T')[0]
                            
                        details[ad_id] = {
                            'permalink': ad_data.get('preview_shareable_link', ''),
                            'created_time': created_time,
                            'start_time': start_time
                        }
            except Exception as e:
                logger.error(f"Error fetching extra details for chunk: {e}")
                
        return details
