# -*- coding: utf-8 -*-
"""
Google Sheets Exporter Module
Export data to Google Sheets
"""
import logging
from typing import List, Dict, Any
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleSheetsExporter:
    """Export data to Google Sheets"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self, credentials_file: str = None, spreadsheet_id: str = None, sheet_name: str = None):
        """
        Initialize Google Sheets client
        
        Args:
            credentials_file: Path to service account JSON file
            spreadsheet_id: Google Spreadsheet ID
            sheet_name: Sheet name to write to
        """
        self.credentials_file = credentials_file or Config.GOOGLE_CREDENTIALS_FILE
        self.spreadsheet_id = spreadsheet_id or Config.GOOGLE_SPREADSHEET_ID
        self.sheet_name = sheet_name
        
        # Authenticate and get client
        self.client = self._authenticate()
        logger.info(f"Google Sheets client initialized")
    
    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            credentials = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=self.SCOPES
            )
            client = gspread.authorize(credentials)
            logger.info("Successfully authenticated with Google Sheets API")
            return client
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Sheets: {e}")
            raise
    
    def export_to_sheet(self, data: List[Dict[str, Any]], sheet_name: str = None) -> str:
        """
        Export data to Google Sheets
        
        Args:
            data: List of dictionaries containing data
            sheet_name: Sheet name (overrides init value)
            
        Returns:
            Sheet URL
        """
        sheet_name = sheet_name or self.sheet_name
        
        if not data:
            logger.warning("No data to export")
            return None
        
        try:
            # Open spreadsheet
            spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            logger.info(f"Opened spreadsheet: {spreadsheet.title}")
            
            # Try to get existing worksheet or create new one
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
                logger.info(f"Found existing worksheet: {sheet_name}")
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=50)
                logger.info(f"Created new worksheet: {sheet_name}")
            
            # Clear existing data
            worksheet.clear()
            logger.info(f"Cleared worksheet: {sheet_name}")
            
            # Prepare data for export
            headers = list(data[0].keys())
            rows = [[self._format_value(row.get(col)) for col in headers] for row in data]
            
            # Ensure worksheet has enough rows
            needed_rows = len(rows) + 1  # +1 for header
            if worksheet.row_count < needed_rows:
                worksheet.add_rows(needed_rows - worksheet.row_count)
                logger.info(f"Expanded worksheet to {needed_rows} rows")
            
            # Update header first
            worksheet.update('E1', [headers], value_input_option='USER_ENTERED')
            logger.info(f"Exported header row")
            
            # Update data in batches to avoid API limits (1000 rows per batch)
            batch_size = 1000
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i + batch_size]
                start_row = i + 2  # +2 because row 1 is header and rows are 1-indexed
                
                # Calculate end column letter dynamically
                # Column E is the 5th column (index 4), so end column is E + len(headers) - 1
                end_col_index = 4 + len(headers)  # 4 for column E (0-indexed: A=0, B=1, C=2, D=3, E=4)
                end_col_letter = self._column_index_to_letter(end_col_index)
                
                range_notation = f'E{start_row}:{end_col_letter}{start_row + len(batch) - 1}'
                worksheet.update(range_notation, batch, value_input_option='USER_ENTERED')
                logger.info(f"Exported rows {start_row} to {start_row + len(batch) - 1} ({len(batch)} rows)")
            
            logger.info(f"Exported total {len(rows)} data rows to {sheet_name} starting from column E")
            
            # Format header row
            self._format_header(worksheet, len(headers))
            
            # Format numeric columns
            self._format_numeric_columns(worksheet, headers, len(rows))
            
            # Auto-resize columns
            self._auto_resize_columns(worksheet, len(headers))
            
            sheet_url = worksheet.url
            logger.info(f"Data exported successfully to: {sheet_url}")
            return sheet_url
            
        except Exception as e:
            logger.error(f"Error exporting to Google Sheets: {e}")
            raise
    
    def _format_value(self, value):
        """Format value for Google Sheets"""
        if value is None:
            return ''
        elif isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(value, (int, float)):
            return value
        else:
            return str(value)
    
    def _column_index_to_letter(self, index):
        """Convert column index (0-based) to column letter (A, B, ..., Z, AA, AB, ...)"""
        result = ''
        while index >= 0:
            result = chr(65 + (index % 26)) + result
            index = index // 26 - 1
        return result
    
    def _format_header(self, worksheet, num_cols: int):
        """Format header row (bold, background color)"""
        try:
            # Start from column E (column index 4)
            start_col = 'E'
            end_col = chr(68 + num_cols)  # E is 69 (68+1), so 68+num_cols for end
            worksheet.format('{}1:{}1'.format(start_col, end_col), {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8}
            })
            logger.info("Header formatted successfully")
        except Exception as e:
            logger.warning(f"Failed to format header: {e}")
    
    def _auto_resize_columns(self, worksheet, num_cols: int):
        """Auto-resize columns to fit content"""
        try:
            # Get spreadsheet
            spreadsheet = worksheet.spreadsheet
            
            # Auto-resize request starting from column E (index 4)
            requests = [{
                'autoResizeDimensions': {
                    'dimensions': {
                        'sheetId': worksheet.id,
                        'dimension': 'COLUMNS',
                        'startIndex': 4,  # Column E is index 4
                        'endIndex': 4 + num_cols  # End at E + num_cols
                    }
                }
            }]
            
            spreadsheet.batch_update({'requests': requests})
            logger.info("Columns auto-resized successfully")
        except Exception as e:
            logger.warning(f"Failed to auto-resize columns: {e}")
    
    def _format_numeric_columns(self, worksheet, headers: list, num_rows: int):
        """Format numeric columns with thousand separators and decimal points"""
        try:
            spreadsheet = worksheet.spreadsheet
            
            # Numeric column names (adjust based on your data structure)
            numeric_columns = [
                'impressions', 'reach', 'frequency', 'clicks', 'cpc_all', 'cpc_link_click',
                'ctr_all', 'ctr_link_click', 'cpm', 'link_clicks', 'cost_per_result',
                'spend', 'actions', 'conversions', 'purchases', 'purchase_value',
                'roas', 'cpa', 'cpp', 'video_views', 'video_view_rate'
            ]
            
            requests = []
            
            # Find column indices for numeric columns
            for col_name in numeric_columns:
                if col_name in headers:
                    col_index = headers.index(col_name)
                    # Add 4 because we start from column E (index 4)
                    actual_col_index = col_index + 4
                    
                    # Format as number with thousand separator and 2 decimal places
                    requests.append({
                        'repeatCell': {
                            'range': {
                                'sheetId': worksheet.id,
                                'startRowIndex': 1,  # Skip header row
                                'endRowIndex': num_rows + 1,  # +1 for header
                                'startColumnIndex': actual_col_index,
                                'endColumnIndex': actual_col_index + 1
                            },
                            'cell': {
                                'userEnteredFormat': {
                                    'numberFormat': {
                                        'type': 'NUMBER',
                                        'pattern': '#,##0.00'
                                    }
                                }
                            },
                            'fields': 'userEnteredFormat.numberFormat'
                        }
                    })
            
            if requests:
                spreadsheet.batch_update({'requests': requests})
                logger.info(f"Formatted {len(requests)} numeric columns successfully")
        except Exception as e:
            logger.warning(f"Failed to format numeric columns: {e}")
    
    def append_to_sheet(self, data: List[Dict[str, Any]], sheet_name: str = None):
        """
        Append data to existing sheet (without clearing)
        
        Args:
            data: List of dictionaries containing data
            sheet_name: Sheet name
        """
        sheet_name = sheet_name or self.sheet_name
        
        if not data:
            logger.warning("No data to append")
            return
        
        try:
            spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)
            
            # Prepare data
            headers = list(data[0].keys())
            rows = [[self._format_value(row.get(col)) for col in headers] for row in data]
            
            # Append data
            worksheet.append_rows(rows, value_input_option='USER_ENTERED')
            logger.info(f"Appended {len(rows)} rows to {sheet_name}")
            
        except Exception as e:
            logger.error(f"Error appending to Google Sheets: {e}")
            raise
    
    def clear_sheet(self, sheet_name: str = None):
        """Clear all data from sheet"""
        sheet_name = sheet_name or self.sheet_name
        
        try:
            spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)
            worksheet.clear()
            logger.info(f"Cleared worksheet: {sheet_name}")
        except Exception as e:
            logger.error(f"Error clearing sheet: {e}")
            raise
