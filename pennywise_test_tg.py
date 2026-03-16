import pennywise_tools
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# 🔑 你的機器人身分證
TOKEN = "8478481203:AAGYnBFuyOfMFXAtku-wechU5G-bIEPrEhI"

# --- [原始規則設定] ---
food_keywords = ['麵', '飯', '吧', '吃', '甜點', '咖啡', '冉冉', '茶', 'Mos', '摩斯', '漢堡', 'burger']
traffic_keywords = ['車', 'uber', '油', '捷運', '高鐵', 'Uber']
home_keywords = ['家', '電', '租', '衛生紙']
pet_keywords = ['貓', '寵', '罐頭']

# 📦 統一處理邏輯的箱子 (核心邏輯都在這)
async def process_data(update: Update, is_edit=False):
    # 判斷訊息來源：是新傳的 message 還是被編輯的 edited_message
    msg = update.edited_message if is_edit else update.message
    
    # 防呆：有時候編輯訊息會抓不到內容
    if not msg or not msg.text:
        return

    raw_input = msg.text
    msg_id = msg.message_id  # 拿到這則訊息的唯一身份證 (重要！)

    # --- [1] 報表指令判斷 ---
    if raw_input == "/report":
        await msg.reply_text("⏳ 正在分析雲端數據，請稍候...")
        report_msg = pennywise_tools.get_expense_report()
        await msg.reply_text(report_msg)
        return

    # --- [2] 記帳資料解析 ---
    try:
        parts = raw_input.split(' ')
        if len(parts) < 3:
            await msg.reply_text("❌ 格式不對喔！\n💡 範例: 牛肉麵 180 vc")
            return

        item = parts[0]
        amount = parts[1]
        code = parts[2]

        who = 'Vera' if 'v' in code else ('Shen' if 's' in code else 'N/A')
        payment = '信用卡' if 'cc' in code else ('現金' if 'c' in code else 'N/A')
        
        category = 'N/A'
        for k in food_keywords:
            if k in item: category = '飲食'; break
        if category == 'N/A':
            for k in traffic_keywords:
                if k in item: category = '交通'; break
        if category == 'N/A':
            for k in home_keywords:
                if k in item: category = '居家'; break
        if category == 'N/A':
            for k in pet_keywords:
                if k in item: category = '寵物'; break

        # --- [3] 決定要「新增」還是「更新」 ---
        if is_edit:
            # 如果是編輯，呼叫更新工具
            result = pennywise_tools.update_expense(item, amount, category, who, payment, msg_id)
        else:
            # 如果是新訊息，呼叫存檔工具 (我們幫 save_expense 多傳一個 msg_id)
            result = pennywise_tools.save_expense(item, amount, category, who, payment, msg_id)

        # --- [4] 回傳結果 ---
        await msg.reply_text(
            f"{'✏️ 編輯成功' if is_edit else '✅ 記帳成功'}！\n"
            f"項目：{item}\n"
            f"金額：{amount}\n"
            f"分類：{category}\n"
            f"付款人：{who}\n"
            f"方式：{payment}\n\n"
            f"{result}"
        )

    except Exception as e:
        await msg.reply_text(f"❌ 解析失敗：{e}")

# 收到新訊息時執行
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await process_data(update, is_edit=False)

# 偵測到編輯時執行
async def handle_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await process_data(update, is_edit=True)

if __name__ == '__main__':
    from telegram.request import HTTPXRequest
    my_request = HTTPXRequest(connect_timeout=30, read_timeout=30)
    app = ApplicationBuilder().token(TOKEN).request(my_request).build()
    
    # 註冊新訊息處理
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    # 註冊編輯訊息處理
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE & filters.TEXT, handle_edit))
    
    print("🚀 智慧型記帳機器人（支援編輯功能）已上線！")
    app.run_polling(poll_interval=1.0)