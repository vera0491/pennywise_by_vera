import csv
import os


filename = 'pennywise.csv'

# 1. 檢查檔案在不在，不在就沒得分析了
if not os.path.isfile(filename):
    print('❌ 找不到記帳檔案！請先執行主程式記幾筆帳吧。')
    exit()

# 2. 初始化統計變數 (歸零)
total_spend = 0            # 總花費
vera_paid = 0              # Vera 付了多少
shen_paid = 0              # Shen 付了多少
category_stats = {}        # 分類統計 (用字典 Dictionary 來存)
month_stats = {}
weekday_stats = {}         # 統計星期
hour_stats = {}            # 統計小時

print(f'📊 正在分析 {filename} ...\n')

# 3. 打開檔案 (這次用 mode='r' 讀取模式)
with open(filename, mode='r', encoding='utf-8') as f:
    reader = csv.reader(f)

    # ★ 關鍵動作：跳過第一列 (標題欄)
    header = next(reader)

    # 4. 一列一列讀出來分析
    for row in reader:
        # ==============================================================================
        # 新版 CSV 結構 (v1.6+)：
        # row 排序：['2026-01-28', '週三', '18:06', '飲食', '牛肉麵', '150', 'Vera', '現金']
        # 索引：     [0]           [1]     [2]      [3]     [4]       [5]    [6]     [7]
        # ==============================================================================
        # 4.1 抓出資料
        date = row[0]          # 日期 (例如 "2026-01-28")
        weekday = row[1]       # 星期 (例如 "週三")
        time_full = row[2]     # 時間 (例如 "18:06")
        category = row[3]      # 分類
        item = row[4]          # 項目 (雖然沒用到，但知道它在 4)
        amount_str = row[5]    # 金額
        who = row[6]           # 付款人

        # 4.2 轉型：把文字轉成數字
        amount = int(amount_str)

        # 4.3 資料加工 (切出我們要的月份跟小時)
        current_month = date[:7]      # "2026-01-28" -> "2026-01"
        current_hour = time_full[:2]  # "18:06" -> "18"

       # --- 分析 A: 總金額 ---
        total_spend += amount

        # --- 分析 B: 誰付的錢 ---
        if who == 'Vera':
            vera_paid += amount
        elif who == 'Shen':
            shen_paid += amount

        # --- 分析 C: 分類統計 ---
        if category in category_stats:
            category_stats[category] += amount
        else:
            category_stats[category] = amount

        # --- 分析 D: 月份統計 (New!) ---
        if current_month in month_stats:
            month_stats[current_month] += amount
        else:
            month_stats[current_month] = amount

        # --- 分析 E: 週間統計 (New!) ---
        if weekday in weekday_stats:
            weekday_stats[weekday] += amount
        else:
            weekday_stats[weekday] = amount

        # --- 分析 F: 時段統計 (New!) ---
        if current_hour in hour_stats:
            hour_stats[current_hour] += amount
        else:
            hour_stats[current_hour] = amount


# ==========================================
# 5. 印出漂亮報表
# ==========================================
print('=' * 30)
print(f'💰 總消費金額： ${total_spend}')
print('=' * 30)

print('\n👤 付款人分析：')
print(f'   - Vera 付款：${vera_paid}')
print(f'   - Shen 付款：${shen_paid}')

print('\n🍰 分類消費排行榜：')
# items() 會同時拿出 key (分類) 和 value (金額)
for cat, cost in category_stats.items():
    print(f'   - {cat}: ${cost}')

# --- 新增：時間維度分析 ---

print('\n🗓️  月份收支表：')
# 使用 sorted() 確保月份由小到大 (01月, 02月...)
for m in sorted(month_stats.keys()):
    cost = month_stats[m]
    print(f'   - {m}: ${cost}')

print('\n📅 週間消費習慣：')
# 自定義順序：告訴電腦「週一」要在「週二」前面
days_order = ['週一', '週二', '週三', '週四', '週五', '週六', '週日']
for day in days_order:
    # 檢查：只有當那天有花費紀錄時才印出來 (避免報錯)
    if day in weekday_stats:
        cost = weekday_stats[day]
        print(f'   - {day}: ${cost}')

print('\n⏰ 敗家時段分析：')
# 使用 sorted() 確保時間由 00 點排到 23 點
for hour in sorted(hour_stats.keys()):
    cost = hour_stats[hour]
    print(f'   - {hour}點: ${cost}')

print('\n' + '=' * 30)
