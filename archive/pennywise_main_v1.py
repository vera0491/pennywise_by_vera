# --- 1. 輸入與切割 (Input & Split) ---
print("歡迎使用 PennyWise 破產版 v1.0")
raw_input = input("請輸入記帳 (格式: 用途 金額 代號): ")

# 切割字串
parts = raw_input.split(" ")
item = parts[0]  # 例如: "千層吧"
amount = parts[1]  # 例如: "1540"
code = parts[2]  # 例如: "vcc"

# --- 2. 變數命名 (Decoding Logic) ---
# 這些是「如果沒發生意外」或「沒偵測到」時的預設值
who = "未填寫"
payment = "現金"
category = "未分類"

# 判斷是誰 (檢查 code 裡面有沒有 "v")
if "v" in code:
    who = "Vera"
elif "s" in code:
    who = "Shen"
else:
    print("缺付款人")

# 判斷方式 (檢查 code 裡面有沒有 "cc" 或 "c")
if "cc" in code:
    payment = "信用卡"
elif "c" in code:  # 如果不是 cc，但有 c
    payment = "現金"
else:
    print("缺付款方式")

# --- 3. 判斷分類 (Categorization Logic) ---
# 因為還沒學到字典，我們用暴力 if 法！
# 只要用途裡包含關鍵字，就歸類

if "麵" in item:
    category = "飲食"
elif "飯" in item:
    category = "飲食"
elif "吧" in item:
    category = "飲食"
elif "車" in item:
    category = "交通"
elif "uber" in item:
    category = "交通"
elif "家" in item:
    category = "交通"
elif "貓" in item:
    category = "寵物"
# ...你可以在這裡一直無限加 elif 下去...


# --- 4. 顯示結果 (Output) ---
print("\n========== 記帳成功 ==========")
print(f"分類: {category}")
print(f"項目: {item}")
print(f"金額: ${amount}")
print(f"細節: {who} 使用 {payment}")
print("==============================")
