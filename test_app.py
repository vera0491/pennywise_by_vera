import pennywise_tools

print("🚀 準備發射資料到 Google 雲端...")

# 呼叫雲端記帳工具 (我們來買個雲端測試蛋糕！)
result = pennywise_tools.save_expense(item="雲端測試蛋糕", amount=120, category="飲食", who="Vera", payment="現金")

# 印出機器人的回報結果
print(result)