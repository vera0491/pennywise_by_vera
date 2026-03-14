import csv
import os


# 定義這是一個「功能」，以後只要呼叫 get_expense_report() 它就會開始工作
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
                vera_paid += amount  # noqa: E701
            elif who == 'Shen':
                shen_paid += amount

            # 字典統計 (使用 get 簡化寫法：如果沒有就給 0，有就 + amount)
            category_stats[category] = category_stats.get(category, 0) + amount
            month_stats[current_month] = month_stats.get(current_month, 0) + amount
            weekday_stats[weekday] = weekday_stats.get(weekday, 0) + amount
            hour_stats[current_hour] = hour_stats.get(current_hour, 0) + amount

            # ==========================================
            # 4. 製作報表 (這是跟之前最不一樣的地方！)
            # ==========================================

            # 準備一張空白紙 (空字串)
            result = ''

            # 開始一行一行寫進去 (+= 代表「接續寫在後面」)
            # 記得每一行後面都要加 "\n"，不然字會全部黏在一起

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

            # ★ 關鍵動作：把寫好的紙條交出去
            return result
