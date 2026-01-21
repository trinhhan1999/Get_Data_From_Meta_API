# Hướng dẫn cấu hình Google Sheets Export

## Bước 1: Tạo Google Cloud Project và Service Account

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới hoặc chọn project có sẵn
3. Enable **Google Sheets API** và **Google Drive API**:
   - Vào **APIs & Services** > **Library**
   - Tìm và enable "Google Sheets API"
   - Tìm và enable "Google Drive API"

## Bước 2: Tạo Service Account

1. Vào **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **Service Account**
3. Điền thông tin:
   - Service account name: `facebook-ads-exporter`
   - Service account ID: tự động generate
   - Click **Create and Continue**
4. Grant quyền: **Editor** role
5. Click **Done**

## Bước 3: Tạo JSON Key

1. Click vào service account vừa tạo
2. Vào tab **Keys**
3. Click **Add Key** > **Create new key**
4. Chọn **JSON** format
5. File JSON sẽ được download về máy
6. Rename file thành `credentials.json` và copy vào folder `D:\Get_Data_From_Meta\`

## Bước 4: Tạo Google Spreadsheet

1. Truy cập [Google Sheets](https://sheets.google.com)
2. Tạo spreadsheet mới
3. Copy **Spreadsheet ID** từ URL:
   ```
   https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit
   ```
4. **QUAN TRỌNG**: Share spreadsheet với service account email:
   - Click **Share** button
   - Paste service account email (có dạng: `xxx@xxx.iam.gserviceaccount.com`)
   - Chọn quyền **Editor**
   - Bỏ tick "Notify people"
   - Click **Share**

## Bước 5: Cấu hình .env

Mở file `.env` và thêm/sửa:

```env
# Enable Google Sheets export
USE_GOOGLE_SHEETS=true

# Path to credentials file
GOOGLE_CREDENTIALS_FILE=credentials.json

# Your Spreadsheet ID
GOOGLE_SPREADSHEET_ID=your_spreadsheet_id_here

# Sheet names (tên các sheet trong spreadsheet)
AD_ACCOUNT_SHEET_1=CPAS_Shopee_Shondo
AD_ACCOUNT_SHEET_2=OnlineStore_Shondo
```

## Bước 6: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

## Bước 7: Test

Chạy pipeline:
```bash
.\venv\Scripts\python.exe main.py --run-now --days 7
```

Kiểm tra Google Sheets xem có data được export lên không.

## Cấu trúc file trong folder

```
D:\Get_Data_From_Meta\
├── credentials.json       # Google Service Account key (KHÔNG commit lên Git!)
├── .env                  # Config với GOOGLE_SPREADSHEET_ID
└── google_sheets_exporter.py
```

## Lưu ý bảo mật

- ❌ **KHÔNG** commit file `credentials.json` lên Git
- ❌ **KHÔNG** share service account key công khai
- ✅ File `credentials.json` đã được thêm vào `.gitignore`

## Troubleshooting

### Lỗi "Permission denied"
- Kiểm tra đã share spreadsheet với service account email chưa
- Đảm bảo service account có quyền Editor

### Lỗi "API not enabled"
- Enable Google Sheets API và Drive API trong Google Cloud Console

### Lỗi "File not found: credentials.json"
- Đảm bảo file `credentials.json` nằm đúng folder `D:\Get_Data_From_Meta\`
- Hoặc cập nhật đường dẫn trong `.env`: `GOOGLE_CREDENTIALS_FILE=path/to/credentials.json`
