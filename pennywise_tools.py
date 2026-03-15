import csv
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ==========================================
# 工具 1：算報表 (get_expense_report)
# ==========================================
def get_expense_report():
    filename = 'pennywise.csv'

    # 1. 檢查檔案
    if not os.path.isfile(filename):
        return '❌ 找不到記帳檔案！請先記幾筆帳吧。'

    # 2. 初始化變數
    total_spend = 0
    vera_paid = 0
    shen_paid = 0
    category_stats = {}
    weekday_stats = {}
    hour_stats = {}
    month_stats = {}

    # 3. 讀取與計算
    with open(filename, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            _ = next(reader) # 跳過標題

        except StopIteration:
            return '⚠️ 檔案是空的，沒有資料可以分析。'

        for row in reader:
            # 防呆：避免讀到空行報錯
            if not row:
                continue

            # [0]日期, [1]星期, [2]時間, [3]分類, [4]項目, [5]金額, [6]付, [7]方式
            date = row[0]
            weekday = row[1]
            time_full = row[2]
            category = row[3]
            amount = int(row[5])
            who = row[6]

            current_month = date[:7]
            current_hour = time_full[:2]

            # --- 開始統計 ---
            total_spend += amount

            if who == 'Vera':
                vera_paid += amount
            elif who == 'Shen':
                shen_paid += amount

            # 字典統計
            category_stats[category] = category_stats.get(category, 0) + amount
            month_stats[current_month] = month_stats.get(current_month, 0) + amount
            weekday_stats[weekday] = weekday_stats.get(weekday, 0) + amount
            hour_stats[current_hour] = hour_stats.get(current_hour, 0) + amount

    # 4. 製作報表
    result = ''

    result += '=' * 30 + '\n'
    result += f'💰 總消費金額： ${total_spend}\n'
    result += '=' * 30 + '\n'

    result += '\n👤 付款人分析：\n'
    result += f'   - Vera 付款：${vera_paid}\n'
    result += f'   - Shen 付款：${shen_paid}\n'

    result += '\n🍰 分類消費排行：\n'
    for cat, cost in category_stats.items():
        result += f'   - {cat}: ${cost}\n'

    result += '\n🗓️  月份收支表：\n'
    for m in sorted(month_stats.keys()):
        result += f'   - {m}: ${month_stats[m]}\n'

    result += '\n📅 週間消費習慣：\n'
    days_order = ['週一', '週二', '週三', '週四', '週五', '週六', '週日']
    for day in days_order:
        if day in weekday_stats:
            result += f'   - {day}: ${weekday_stats[day]}\n'

    result += '\n⏰ 花錢時段分析：\n'
    for hour in sorted(hour_stats.keys()):
        result += f'   - {hour}點: ${hour_stats[hour]}\n'

    result += '\n' + '=' * 30

    return result

# ==========================================
# 工具 2：雲端記帳 (save_expense)
# ==========================================
def save_expense(item, amount, category, who, payment):
    # 1. 準備時間戳記
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")
    week_days = ["一", "二", "三", "四", "五", "六", "日"]
    current_weekday = f"週{week_days[now.weekday()]}"

    try:
        # 2. 拿出鑰匙，連線 Google Sheets
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        
        # 打開記帳本
        sheet = client.open('Pennywise記帳本').sheet1

        # 3. 準備要寫入的資料
        row_data = [current_date, current_weekday, current_time, category, item, amount, who, payment]

        # 4. 寫入雲端試算表
        sheet.append_row(row_data)

        return f"☁️ ✅ 雲端記帳成功！已儲存：{item} ${amount}"

    except Exception as e:
        return f"❌ 雲端存檔失敗：{e}"