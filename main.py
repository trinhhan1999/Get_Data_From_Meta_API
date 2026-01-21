# -*- coding: utf-8 -*-
"""
Main Pipeline Module - Multi Account Support
"""
import logging
import time
from datetime import datetime, timedelta
import schedule
from facebook_ads_client import FacebookAdsClient
from database import DatabaseManager, setup_all_tables
from config import Config

# Conditional import for Google Sheets
if Config.USE_GOOGLE_SHEETS:
    from google_sheets_exporter import GoogleSheetsExporter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_pipeline_for_account(account: dict, days_back: int = 7):
    """Run pipeline for a single account - returns data for combined export"""
    account_id = account['id']
    account_name = account['name']
    table_name = account['table_name']
    
    logger.info(f"Processing account: {account_name} ({account_id})")
    
    try:
        # 1. Fetch data from Facebook Ads
        logger.info(f"  Step 1: Fetching data from Facebook Ads API...")
        fb_client = FacebookAdsClient(ad_account_id=account_id)
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        ads_data = fb_client.get_ads_data(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        
        logger.info(f"  Fetched {len(ads_data)} records")
        
        if not ads_data:
            logger.warning(f"  No data fetched for {account_name}")
            return []
        
        # 2. Save to PostgreSQL (clear date range first)
        logger.info(f"  Step 2: Saving data to PostgreSQL table: {table_name}...")
        db_manager = DatabaseManager(table_name=table_name)
        db_manager.create_table()
        
        # Clear only the date range we're fetching (not all data)
        logger.info(f"  Clearing data from {start_date} to {end_date} in {table_name}...")
        db_manager.clear_date_range(start_date, end_date)
        
        inserted_count = db_manager.insert_data(ads_data)
        logger.info(f"  Inserted {inserted_count} records")
        
        # Get all data from database for combined Google Sheets export
        all_data = db_manager.get_all_data()
        logger.info(f"  Total {len(all_data)} records in database")
        
        logger.info(f"  Account {account_name} completed successfully!")
        
        # Return all data for combined Google Sheets export
        return all_data
        
    except Exception as e:
        logger.error(f"  Error processing {account_name}: {e}")
        return []


def run_pipeline(days_back: int = 7):
    """Run pipeline for all accounts and combine data in Google Sheets"""
    logger.info("=" * 60)
    logger.info("STARTING FACEBOOK ADS DATA PIPELINE (MULTI-ACCOUNT)")
    logger.info("=" * 60)
    
    if not Config.AD_ACCOUNTS:
        logger.error("No ad accounts configured!")
        return
    
    logger.info(f"Found {len(Config.AD_ACCOUNTS)} ad accounts to process")
    
    combined_data = []
    
    for i, account in enumerate(Config.AD_ACCOUNTS, 1):
        logger.info("-" * 40)
        logger.info(f"Account {i}/{len(Config.AD_ACCOUNTS)}")
        try:
            account_data = run_pipeline_for_account(account, days_back)
            if account_data:
                combined_data.extend(account_data)
        except Exception as e:
            logger.error(f"Failed to process account: {e}")
            continue
    
    # Export combined data to single Google Sheet
    if Config.USE_GOOGLE_SHEETS and combined_data:
        logger.info("=" * 60)
        logger.info("EXPORTING COMBINED DATA TO GOOGLE SHEETS")
        logger.info("=" * 60)
        
        try:
            gs_exporter = GoogleSheetsExporter(sheet_name="Facebook Ads Data")
            sheet_url = gs_exporter.export_to_sheet(combined_data, sheet_name="Facebook Ads Data")
            logger.info(f"Successfully exported {len(combined_data)} total records to Google Sheets")
            logger.info(f"Sheet URL: {sheet_url}")
        except Exception as e:
            logger.error(f"Failed to export to Google Sheets: {e}")
    
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETED")
    logger.info(f"Total records processed: {len(combined_data)}")
    logger.info("=" * 60)


def run_daily_job():
    """Daily job"""
    logger.info("Running daily job...")
    run_pipeline(days_back=Config.DEFAULT_DAYS_BACK)


def schedule_daily_run():
    """Schedule daily run"""
    run_time = Config.DAILY_RUN_TIME
    logger.info(f"Scheduling daily run at {run_time}")
    
    schedule.every().day.at(run_time).do(run_daily_job)
    
    logger.info("Scheduler started. Press Ctrl+C to stop.")
    
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Facebook Ads Data Pipeline (Multi-Account)')
    parser.add_argument('--run-now', action='store_true', help='Run pipeline immediately')
    parser.add_argument('--schedule', action='store_true', help='Run scheduler for daily execution')
    parser.add_argument('--days', type=int, default=7, help='Number of days to fetch (default: 7)')
    parser.add_argument('--setup', action='store_true', help='Setup database tables only')
    
    args = parser.parse_args()
    
    if args.setup:
        setup_all_tables()
    elif args.run_now:
        run_pipeline(days_back=args.days)
    elif args.schedule:
        run_daily_job()
        schedule_daily_run()
    else:
        print("Usage:")
        print("  python main.py --setup            # Setup database tables")
        print("  python main.py --run-now          # Run pipeline immediately")
        print("  python main.py --run-now --days 30    # Run with 30 days of data")
        print("  python main.py --schedule         # Run scheduler for daily execution")
