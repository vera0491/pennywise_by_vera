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
    await query.answer()

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

# --- 解析記帳訊息 ---
# 格式規則：最後一段是 code（含 v/s/c/cc），倒數第二段是金額（數字），前面全是項目名稱
# 例如：「茅乃川 1098 vcc」→ item=茅乃川, amount=1098, code=vcc
# 例如：「out of office不在辦公室 拿鐵 180 vc」→ item=out of office不在辦公室 拿鐵, amount=180, code=vc
def parse_expense(raw_input):
    parts = raw_input.strip().split()

    if len(parts) < 3:
        return None  # 至少要有 item + amount + code 三段

    code = parts[-1]          # 最後一段是 code
    amount_str = parts[-2]    # 倒數第二段是金額
    item = ' '.join(parts[:-2])  # 前面所有的都是項目名稱（允許空格）

    # 驗證：金額必須是數字，code 必須含有 v 或 s
    if not amount_str.isdigit():
        return None
    if 'v' not in code and 's' not in code:
        return None

    who = 'Vera' if 'v' in code else ('Shen' if 's' in code else 'N/A')
    payment = '信用卡' if 'cc' in code else ('現金' if 'c' in code else 'N/A')

    return {
        'item': item,
        'amount': amount_str,
        'code': code,
        'who': who,
        'payment': payment,
    }

# --- 記帳處理 ---
async def process_data(update: Update, is_edit=False):
    msg = update.edited_message if is_edit else update.message
    if not msg or not msg.text:
        return

    raw_input = msg.text
    msg_id = msg.message_id

    parsed = parse_expense(raw_input)
    if not parsed:
        return  # 靜默忽略，不是記帳格式

    try:
        item    = parsed['item']
        amount  = parsed['amount']
        who     = parsed['who']
        payment = parsed['payment']

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

    # ⚠️ 修正順序：EDITED_MESSAGE 必須在一般 TEXT 之前註冊
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE & filters.TEXT, handle_edit))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print('🚀 機器人上線！/sum 快速報表，/report 選單報表')
    app.run_polling(allowed_updates=Update.ALL_TYPES)  # ✅ 必須加這個才能收到 edited_message
