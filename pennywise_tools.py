import csv
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ==========================================
# 工具 1：算報表 (get_expense_report)
# ==========================================
def get_expense_report():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open('Pennywise記帳本').sheet1

        all_data = sheet.get_all_values()
        
        if len(all_data) <= 1:
            return "⚠️ 目前雲端帳本是空的喔！"

        total_spend = 0
        vera_paid = 0
        shen_paid = 0
        category_stats = {}
        weekday_stats = {}
        hour_stats = {}
        month_stats = {}

        for row in all_data[1:]:
            if not row or len(row) < 6: continue # 基本防呆

            # 欄位對應：[0]日期, [1]星期, [2]時間, [3]分類, [4]項目, [5]金額, [6]付
            date = row[0]
            weekday = row[1]
            time_full = row[2]
            category = row[3]
            amount = int(row[5]) if row[5].isdigit() else 0
            who = row[6] if len(row) > 6 else "N/A"

            current_month = date[:7]
            current_hour = time_full[:2]

            total_spend += amount
            if who == 'Vera': vera_paid += amount
            elif who == 'Shen': shen_paid += amount

            category_stats[category] = category_stats.get(category, 0) + amount
            month_stats[current_month] = month_stats.get(current_month, 0) + amount
            weekday_stats[weekday] = weekday_stats.get(weekday, 0) + amount
            hour_stats[current_hour] = hour_stats.get(current_hour, 0) + amount

        result = '📊 **Pennywise 雲端分析報表**\n'
        result += '=' * 25 + '\n'
        result += f'💰 總消費金額： ${total_spend}\n'
        result += '=' * 25 + '\n'
        result += f'\n👤 付款人分析：\n   - Vera 付款：${vera_paid}\n   - Shen 付款：${shen_paid}\n'
        result += '\n🍰 分類消費排行：\n'
        for cat, cost in category_stats.items():
            result += f'   - {cat}: ${cost}\n'
        result += '\n🗓️ 月份收支表：\n'
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
        result += '\n' + '=' * 25
        return result

    except Exception as e:
        return f"❌ 報表生成失敗：{e}"

# ==========================================
# 工具 2：更新記帳 (update_expense)
# ==========================================
def update_expense(item, amount, category, who, payment, msg_id):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open('Pennywise記帳本').sheet1

        # 搜尋訊息 ID
        cell = sheet.find(str(msg_id))
        
        if cell:
            row_idx = cell.row
            # 更新 D(分類), E(項目), F(金額), G(付款人), H(方式) 
            sheet.update(f'D{row_idx}:H{row_idx}', [[category, item, amount, who, payment]])
            return f"✏️ 已同步修正雲端資料：{item} ${amount}"
        else:
            return save_expense(item, amount, category, who, payment, msg_id)

    except Exception as e:
        return f"❌ 修正失敗：{e}"

# ==========================================
# 工具 3：儲存記帳 (save_expense)
# ==========================================
def save_expense(item, amount, category, who, payment, msg_id):
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")
    week_days = ["一", "二", "三", "四", "五", "六", "日"]
    current_weekday = f"週{week_days[now.weekday()]}"

    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open('Pennywise記帳本').sheet1

        # 寫入時包含 msg_id (第 I 欄)
        row_data = [current_date, current_weekday, current_time, category, item, amount, who, payment, str(msg_id)]
        sheet.append_row(row_data)
        return f"☁️ ✅ 雲端記帳成功！已儲存：{item} ${amount}"
    except Exception as e:
        return f"❌ 雲端存檔失敗：{e}"