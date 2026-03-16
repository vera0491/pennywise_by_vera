import csv
import os
from datetime import datetime


# ==========================================
# [a] 全域設定與初始化 (Global Settings)
# ==========================================

# a.1 建立關鍵字清單 (List)

food_keywords = ['麵', '飯', '吧', '吃', '甜點', '咖啡', '冉冉', '茶']
traffic_keywords = ['車', 'uber', '油', '捷運', '高鐵']
home_keywords = ['家', '電', '租', '衛生紙']
pet_keywords = ['貓', '寵', '罐頭']

# a.2 顯示歡迎訊息 (System Start)
print('\n=== PennyWise 記帳小幫手 v1.6 ===')

# ==========================================
# [b] 主程式迴圈 (Main Loop)
# ==========================================
while True:
    # --------------------------------------
    # 步驟 1: 狀態歸零 (Reset State)
    # --------------------------------------
    who = 'N/A'
    payment = 'N/A'
    category = 'N/A'
    # --------------------------------------
    # 步驟 2: 獲取輸入與檢查 (Input & Validation)
    # --------------------------------------
    print('\n')
    raw_input = input('請輸入 (用途 金額 代號) 或輸入 q 離開: ')

    # 2-1. 檢查是否登出
    if raw_input == 'q':
        print('👋 記帳結束，下次見！')
        break

    # 2-2. 資料切割與防呆
    try:
        parts = raw_input.split(' ')
        item = parts[0]
        amount = parts[1]
        code = parts[2]
    except IndexError:
        print('❌ 格式錯誤')
        print('💡 範例: 午餐 100 c ')
        continue # 重來一次

    # --------------------------------------
    # 步驟 3: 邏輯判斷 (Business Logic)
    # --------------------------------------

    # --- 3.1 解碼付款人 ---
    if 'v' in code:
        who = 'Vera'
    elif 's' in code:
        who = 'Shen'

    # --- 3.2 解碼付款方式 ---
    if 'cc' in code:
        payment = '信用卡'
    elif 'c' in code:
        payment = '現金'

    # --- 3.3 解碼付款分類 ---
    for k in food_keywords:
        if k in item:
            category = '飲食'
            break

    # 邏輯 B: 檢查交通
    for k in traffic_keywords:
        if k in item:
            category = '交通'
            break

    # 邏輯 C: 檢查居家
    for k in home_keywords:
        if k in item:
            category = '居家'
            break

    # 邏輯 D: 檢查寵物
    for k in pet_keywords:
        if k in item:
            category = '寵物'
            break

    # ---  3.4 時間戳記生成 (Data Enrichment) ---
    now = datetime.now()
    current_date = now.strftime('%Y-%m-%d')
    current_time = now.strftime('%H:%M:%S')

    # ------  3.4.1 算星期幾 (可以順便放在這) ---
    week_days = ['一', '二', '三', '四', '五', '六', '日']
    current_weekday = f'週{week_days[now.weekday()]}'

    # --------------------------------------
    # 步驟 4: 輸出結果 (Output)
    # --------------------------------------
    print('\n--------------------------')
    print(f'\n{current_date} {current_time[:5]} {category} {item} ${amount} {who} {payment}')
    print('----------------------------')

    # ==========================================
    # 步驟 5: 寫入檔案 (Save to File)
    # ==========================================

    # 1. 設定檔案名稱 (會存在跟程式同一個資料夾)
    filename = 'pennywise.csv'

    # 2. 檢查檔案是否存在
    file_exists = os.path.isfile(filename)

    # 3. 打開檔案
    with open(filename, mode='a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)

        # --- 1. 時間處理區 (大改版) ---
        now = datetime.now() # 先抓當下的時間點物件

        # A. 拆出日期 (例如 2026-01-28)
        current_date = now.strftime('%Y-%m-%d')

        # B. 拆出時間 (例如 17:30:00)
        current_time = now.strftime('%H:%M:%S')

        # C. 星期幾
        # now.weekday() 會回傳 0~6 的數字，我們拿去查上面的表
        day_index = now.weekday()
        current_weekday = f'週{week_days[day_index]}'

        # 抓現在時間，並轉成文字格式 (例如 "2026-01-28 15:30:00")
        current_time = datetime.now().strftime('%H:%M:%S')

        # 4. 如果是新檔案，先寫第一列的標題 (Header)
        if not file_exists:
            writer.writerow(['日期', '星期', '時間', '分類', '項目', '金額', '付款人', '付款方式'])

        # 5. 寫入這一筆記帳資料
        writer.writerow([current_date, current_weekday, current_time, category, item, amount, who, payment])

    print(f'💾 已儲存至 {filename}')
