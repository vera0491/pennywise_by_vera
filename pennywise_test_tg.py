from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    MessageHandler, CommandHandler,
    CallbackQueryHandler, filters
)
import pennywise_tools


TOKEN = '8478481203:AAGYnBFuyOfMFXAtku-wechU5G-bIEPrEhI'  # noqa: S105

# --- /sum：原本的總覽報表（快速版）---
async def cmd_sum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('⏳ 讀取中...')
    await update.message.reply_text(pennywise_tools.get_summary_report())

# --- /report：跳出選單 ---
async def cmd_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton('📅 本月總覽',      callback_data='report_summary')],
        [InlineKeyboardButton('🍰 依分類',        callback_data='report_category')],
        [InlineKeyboardButton('📊 預算類別佔比',   callback_data='report_budget')],
    ]
    await update.message.reply_text(
        '請選擇報表類型：',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# --- 按鈕點擊後的處理 ---
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # 消除 loading 動畫

    data = query.data
    await query.edit_message_text('⏳ 讀取中...')

    if data == 'report_summary':
        text = pennywise_tools.get_summary_report()
    elif data == 'report_category':
        text = pennywise_tools.get_category_report()
    elif data == 'report_budget':
        text = pennywise_tools.get_budget_report()
    else:
        text = '❌ 未知選項'

    await query.edit_message_text(text)

# --- 記帳處理（不變）---
async def process_data(update: Update, is_edit=False):
    msg = update.edited_message if is_edit else update.message
    if not msg or not msg.text:
        return

    raw_input = msg.text
    msg_id = msg.message_id

    try:
        parts = raw_input.split(' ')
        if len(parts) < 3:
            return
        if not parts[1].isdigit():
            return  # 第二段不是數字，不是記帳格式

        item, amount, code = parts[0], parts[1], parts[2]
        who     = 'Vera' if 'v' in code else ('Shen' if 's' in code else 'N/A')
        payment = '信用卡' if 'cc' in code else ('現金' if 'c' in code else 'N/A')

        keyword_config = pennywise_tools.load_keywords_from_sheet()
        category, budget, attr = pennywise_tools.classify_item(item, keyword_config)

        if is_edit:
            result = pennywise_tools.update_expense(item, amount, category, budget, attr, who, payment, msg_id)
        else:
            result = pennywise_tools.save_expense(item, amount, category, budget, attr, who, payment, msg_id)

        await msg.reply_text(
            f"{'✏️ 編輯成功' if is_edit else '✅ 記帳成功'}！\n"
            f"項目：{item}\n"
            f"金額：{amount}\n"
            f"分類：{category}（{attr}）\n"
            f"付款人：{who}\n"
            f"方式：{payment}\n\n"
            f"{result}"
        )
    except Exception as e:
        await msg.reply_text(f'❌ 解析失敗：{e}')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await process_data(update, is_edit=False)

async def handle_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await process_data(update, is_edit=True)

if __name__ == '__main__':
    from telegram.request import HTTPXRequest
    my_request = HTTPXRequest(connect_timeout=30, read_timeout=30)
    app = ApplicationBuilder().token(TOKEN).request(my_request).build()

    app.add_handler(CommandHandler('sum',    cmd_sum))
    app.add_handler(CommandHandler('report', cmd_report))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE & filters.TEXT, handle_edit))

    print('🚀 機器人上線！/sum 快速報表，/report 選單報表')
    app.run_polling()