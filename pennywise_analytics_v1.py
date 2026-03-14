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

print(f'📊 正在分析 {filename} ...\n')

# 3. 打開檔案 (這次用 mode='r' 讀取模式)
with open(filename, mode='r', encoding='utf-8') as f:
    reader = csv.reader(f)

    # ★ 關鍵動作：跳過第一列 (標題欄)
    header = next(reader)

    # 4. 一列一列讀出來分析
    for row in reader:
        # row 會長這樣：['飲食', '牛肉麵', '150', 'Vera', '現金']
        # 對應索引：     [0]      [1]      [2]    [3]     [4]

        category = row[3]
        amount_str = row[5]  # 注意：讀出來是文字
        who = row[6]

        # ★ 轉型：把文字轉成數字
        amount = int(amount_str)

        # --- 分析 A: 總金額 ---
        total_spend = total_spend + amount

        # --- 分析 B: 誰付的錢 ---
        if who == 'Vera':
            vera_paid += amount
        elif who == 'Shen':
            shen_paid += amount

        # --- 分析 C: 分類統計 (進階技巧: Dictionary) ---
        if category in category_stats:
            category_stats[category] += amount  # 如果字典裡有了，就累加
        else:
            category_stats[category] = amount   # 如果字典裡沒有，就新增一個


# 5. 印出漂亮報表
print('=' * 30)
print(f'💰 總消費金額： ${total_spend}')
print('=' * 30)

print('\n👤 付款人分析：')
print(f'   - Vera 付款：${vera_paid}')
print(f'   - Shen 付款：${shen_paid}')

print('\n🍰 分類消費排行榜：')
# 把字典拿出來跑迴圈
for cat, cost in category_stats.items():
    print(f'   - {cat}: ${cost}')

print('\n' + '=' * 30)
