import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

def get_expense_report():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open('Pennywise記帳本').sheet1
        all_data = sheet.get_all_values()
        if len(all_data) <= 1: return "⚠️ 目前帳本是空的喔！"
        
        total_spend, vera_paid, shen_paid = 0, 0, 0
        cat_stats = {}

        for row in all_data[1:]:
            if not row or len(row) < 6: continue
            cat, item, amount, who = row[3], row[4], int(row[5]), row[6]
            total_spend += amount
            if who == 'Vera': vera_paid += amount
            elif who == 'Shen': shen_paid += amount
            cat_stats[cat] = cat_stats.get(cat, 0) + amount

        res = f"📊 **Pennywise 分析報表**\n{'='*20}\n💰 總支出: ${total_spend}\n👩‍💻 Vera: ${vera_paid}\n👨‍💻 Shen: ${shen_paid}\n"
        res += "\n🍰 分類排行:\n" + "\n".join([f"- {k}: ${v}" for k, v in cat_stats.items()])
        return res
    except Exception as e: return f"❌ 報表錯誤: {e}"

def update_expense(item, amount, category, who, payment, msg_id):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open('Pennywise記帳本').sheet1
        cell = sheet.find(str(msg_id))
        if cell:
            sheet.update(f'D{cell.row}:H{cell.row}', [[category, item, amount, who, payment]])
            return f"✏️ 已修正: {item} ${amount}"
        return save_expense(item, amount, category, who, payment, msg_id)
    except Exception as e: return f"❌ 修正失敗: {e}"

def save_expense(item, amount, category, who, payment, msg_id):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open('Pennywise記帳本').sheet1
        now = datetime.now()
        row = [now.strftime("%Y-%m-%d"), f"週{['一','二','三','四','五','六','日'][now.weekday()]}", now.strftime("%H:%M:%S"), category, item, amount, who, payment, str(msg_id)]
        sheet.append_row(row)
        return f"☁️ ✅ 記帳成功: {item} ${amount}"
    except Exception as e: return f"❌ 存檔失敗: {e}"