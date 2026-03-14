# ==========================================
# [a] 全域設定與初始化 (Global Settings)
# ==========================================

# a.1 建立關鍵字清單 (List)

food_keywords = ['麵', '飯', '吧', '吃', '甜點', '咖啡']
traffic_keywords = ['車', 'uber', '油', '捷運', '高鐵']
home_keywords = ['家', '電', '租', '衛生紙']
pet_keywords = ['貓', '寵', '罐頭']

# a.2 顯示歡迎訊息 (System Start)
print('\n=== PennyWise 記帳小幫手 v1.3 ===')

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

    # --------------------------------------
    # 步驟 4: 輸出結果 (Output)
    # --------------------------------------
    print('\n--------------------------')
    print(f'✅ 記帳成功：[{category}] {item} ${amount} ({who}/{payment})')
    print('----------------------------')

    # (迴圈結束，自動跳回 步驟 1)
