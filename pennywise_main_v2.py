# ==========================================
# Phase 1: 設定與初始化 (Configuration)
# ==========================================

# 1.1 建立關鍵字清單 (List)
# 好處：想要新增或刪除，只要在這裡改，下面的程式碼完全不用動！
# 格式：變數名稱 = ["關鍵字1", "關鍵字2", "關鍵字3"...]

food_keywords = ['麵', '飯', '吧', '吃', '甜點', '咖啡']
traffic_keywords = ['車', 'uber', '油', '捷運', '高鐵']
home_keywords = ['家', '電', '租', '衛生紙']
pet_keywords = ['貓', '寵', '罐頭']

# 1.2 初始化預設值
who = 'N/A'
payment = 'N/A'
category = 'N/A'

# ==========================================
# Phase 2: 輸入與前處理 (Input)
# ==========================================
print('\n=== PennyWise v1.2 ===')
raw_input = input('請輸入 (用途 金額 代號): ')

try:
    # 2.1 嘗試做危險動作 (切割 + 取值)
    parts = raw_input.split(' ')
    item = parts[0]
    amount = parts[1]
    code = parts[2]

except IndexError:
    # 2.2 如果上面發生「拿不到東西」的錯誤，就會跳來這裡
    print('❌ 格式錯誤')
    print('💡 範例: 午餐 100 c ')

    # 強制結束程式 (不然程式會繼續往下跑，導致後面變數是空的又報錯)
    exit()

# ==========================================
# Phase 3: 核心邏輯 (Logic)
# ==========================================

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

# 邏輯 A: 檢查飲食
# 翻譯：對於(for) food_keywords 清單裡的每一個關鍵字(k)...
for k in food_keywords:
    if k in item:           # 如果這個關鍵字(k) 出現在用途(item)裡
        category = '飲食'    # 歸類為飲食
        break               # 找到了就停止，不用再往下找了 (優化效能)

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

# ==========================================
# Phase 4: 輸出結果 (Output)
# ==========================================
print('\n--------- 記帳確認 ---------')
print(f'📂 分類: {category}')
print(f'📝 項目: {item}')
print(f'💰 金額: ${amount}')
print(f'👀 付款: {who} ({payment})')
print('----------------------------')
