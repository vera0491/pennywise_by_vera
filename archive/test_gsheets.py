import gspread
from oauth2client.service_account import ServiceAccountCredentials


print("正在嘗試與 Google 雲端連線...")

# 1. 設定機器人的通行證權限範圍 (Drive 和 Sheets)
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

try:
    # 2. 拿出我們剛剛下載的鑰匙
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

    # 3. 登入 Google
    client = gspread.authorize(creds)

    # 4. 嘗試打開你的記帳本 (⚠️ 如果你的試算表不叫這個名字，請改成你的檔名！)
    sheet = client.open("Pennywise記帳本").sheet1

    print("🎉 連線大成功！你的機器人已經順利走進雲端金庫了！")

except Exception as e:
    print(f"❌ 連線失敗，請檢查錯誤訊息：{e}")
