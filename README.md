# Facebook Ads Data Pipeline

Pipeline tự động lấy dữ liệu từ Facebook Ads, lưu vào PostgreSQL và export ra Excel.

## 📋 Tính năng

- ✅ Lấy dữ liệu campaigns từ Facebook Marketing API
- ✅ Lấy insights (metrics) của các chiến dịch quảng cáo
- ✅ Lưu trữ dữ liệu vào PostgreSQL
- ✅ Export dữ liệu ra file Excel với định dạng tiếng Việt
- ✅ Hỗ trợ chạy tự động hàng ngày (scheduled)
- ✅ Tự động xóa file Excel cũ và thay thế bằng file mới

## 📁 Cấu trúc Project

```
Get_Data_From_Meta/
├── config.py              # Cấu hình ứng dụng
├── facebook_ads_client.py # Module kết nối Facebook Ads API
├── database.py            # Module PostgreSQL
├── excel_exporter.py      # Module export Excel
├── main.py               # Script chính
├── requirements.txt      # Dependencies
├── .env.example          # Template file cấu hình
├── .env                  # File cấu hình (cần tạo)
└── exports/              # Thư mục chứa file Excel
```

## 🚀 Hướng dẫn cài đặt

### 1. Cài đặt Python Dependencies

```bash
cd D:\Get_Data_From_Meta
pip install -r requirements.txt
```

### 2. Tạo Database PostgreSQL

```sql
-- Kết nối PostgreSQL và tạo database
CREATE DATABASE facebook_ads_db;
```

### 3. Lấy Facebook Access Token

1. Truy cập [Facebook Developer](https://developers.facebook.com/)
2. Tạo App mới hoặc sử dụng App có sẵn
3. Vào **Tools** > **Graph API Explorer**
4. Chọn App của bạn
5. Thêm permissions:
   - `ads_read`
   - `ads_management`
   - `business_management`
6. Click **Generate Access Token**
7. Copy token

### 4. Lấy Ad Account ID

- Từ URL trong Facebook Ads Manager:
  `https://adsmanager.facebook.com/...&act=2920412648103333&...`
- Ad Account ID = `act_2920412648103333`

### 5. Cấu hình Environment Variables

Tạo file `.env` từ template:

```bash
copy .env.example .env
```

Chỉnh sửa file `.env`:

```env
# Facebook Ads Credentials
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_access_token
AD_ACCOUNT_ID=act_your_ad_account_id

# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=facebook_ads_db
DB_USER=postgres
DB_PASSWORD=your_password

# Export
EXPORT_FOLDER=D:\Get_Data_From_Meta\exports
EXCEL_FILENAME=facebook_ads_data.xlsx
```

## 📖 Cách sử dụng

### Chạy một lần

```bash
# Lấy dữ liệu 30 ngày gần nhất
python main.py --mode once --date-preset last_30d

# Lấy dữ liệu 7 ngày gần nhất
python main.py --mode once --date-preset last_7d

# Lấy dữ liệu theo khoảng thời gian cụ thể
python main.py --mode once --start-date 2025-11-25 --end-date 2025-12-24
```

### Chạy daily (xóa Excel cũ, tạo mới)

```bash
python main.py --mode daily
```

### Chạy theo lịch (mỗi ngày)

```bash
# Chạy lúc 6:00 sáng mỗi ngày
python main.py --mode schedule --schedule-time 06:00

# Chạy lúc 8:30 sáng mỗi ngày
python main.py --mode schedule --schedule-time 08:30
```

### Chỉ export từ Database (không gọi API)

```bash
python main.py --mode export-only
```

## 📊 Dữ liệu Export

File Excel được export với các sheets:

1. **Chiến dịch** - Thông tin campaigns
2. **Tổng hợp** - Metrics tổng hợp theo campaign
3. **Theo ngày** - Metrics chi tiết theo ngày
4. **Tóm tắt** - Báo cáo tổng quan

### Các metrics được lấy:

| Metric | Mô tả |
|--------|-------|
| Impressions | Lượt hiển thị |
| Reach | Số người tiếp cận |
| Frequency | Tần suất |
| Clicks | Lượt click |
| CTR | Tỷ lệ click |
| CPC | Chi phí mỗi click |
| CPM | Chi phí mỗi 1000 lượt hiển thị |
| Spend | Tổng chi phí |
| Results | Kết quả (theo mục tiêu) |
| Cost per Result | Chi phí trên mỗi kết quả |

## 🔄 Tự động hóa với Windows Task Scheduler

Để chạy tự động mỗi ngày trên Windows:

1. Mở **Task Scheduler**
2. Click **Create Basic Task**
3. Đặt tên: `Facebook Ads Data Pipeline`
4. Trigger: **Daily** → Chọn thời gian (VD: 6:00 AM)
5. Action: **Start a program**
   - Program: `python`
   - Arguments: `D:\Get_Data_From_Meta\main.py --mode daily`
   - Start in: `D:\Get_Data_From_Meta`
6. Finish

## 📝 Logs

Logs được lưu trong file `facebook_ads_pipeline.log`

## ⚠️ Lưu ý

1. **Access Token hết hạn**: Token thường hết hạn sau 60 ngày. Cần tạo System User Token cho long-term use.

2. **Rate Limiting**: Facebook API có giới hạn số requests. Pipeline đã được thiết kế để tuân thủ limits.

3. **Backup Database**: Nên backup PostgreSQL định kỳ.

4. **Bảo mật**: Không commit file `.env` lên Git. File đã được thêm vào `.gitignore`.

## 🔧 Troubleshooting

### Lỗi "Invalid OAuth access token"
- Token đã hết hạn, cần generate token mới

### Lỗi "Ad Account ID không hợp lệ"
- Kiểm tra format: phải có prefix `act_`

### Lỗi kết nối PostgreSQL
- Kiểm tra PostgreSQL service đang chạy
- Kiểm tra credentials trong `.env`

## 📞 Support

Nếu có vấn đề, kiểm tra logs trong `facebook_ads_pipeline.log`

## run
.\venv\Scripts\python.exe main.py --run-now --days 120