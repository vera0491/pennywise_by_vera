from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    MessageHandler, CommandHandler,
    CallbackQueryHandler, filters
)
import pennywise_tools


TOKEN = '8478481203:AAGYnBFuyOfMFXAtku-wechU5G-bIEPrEhI'  # noqa: S105

# 暫存關鍵字新增狀態：{ msg_id: { keyword, categories } }
pending_keyword = {}


# --- /sum ---
async def cmd_sum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('⏳ 讀取中...')
    await update.message.reply_text(pennywise_tools.get_summary_report())


# --- /report ---
async def cmd_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton('📅 本月總覽',      callback_data='report_summary')],
        [InlineKeyboardButton('🍰 依分類',        callback_data='report_category')],
        [InlineKeyboardButton('📊 預算類別佔比',   callback_data='report_budget')],
    ]
    await update.message.reply_text('請選擇報表類型：', reply_markup=InlineKeyboardMarkup(keyboard))


# --- callback 處理 ---
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # 報表
    if data == 'report_summary':
        await query.edit_message_text('⏳ 讀取中...')
        await query.edit_message_text(pennywise_tools.get_summary_report())
        return
    if data == 'report_category':
        await query.edit_message_text('⏳ 讀取中...')
        await query.edit_message_text(pennywise_tools.get_category_report())
        return
    if data == 'report_budget':
        await query.edit_message_text('⏳ 讀取中...')
        await query.edit_message_text(pennywise_tools.get_budget_report())
        return

    # 略過
    if data == 'kw_skip':
        await query.edit_message_text('略過，保持 N/A 分類。')
        return

    # 第一步：選預算類別 → 格式 kw1|msg_id|預算類別
    if data.startswith('kw1|'):
        _, msg_id, budget = data.split('|', 2)
        state = pending_keyword.get(msg_id)
        if not state:
            await query.edit_message_text('❌ 狀態已過期，請重新記帳。')
            return

        # 過濾出這個預算類別的分類
        cats = [c for c in state['categories'] if c['budget'] == budget]
        keyboard = []
        for i, cat in enumerate(cats):
            label = f"{cat['category']}（{cat['attr']}）"
            cb = f"kw2|{msg_id}|{i}"  # 短！用索引
            keyboard.append([InlineKeyboardButton(label, callback_data=cb)])
        keyboard.append([InlineKeyboardButton('略過', callback_data='kw_skip')])

        # 把這個預算類別的 cats 存起來供第二步用
        state['filtered'] = cats
        pending_keyword[msg_id] = state

        await query.edit_message_text(
            f'「{state["keyword"]}」→ 【{budget}】\n請選擇細分類：',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # 第二步：選細分類 → 格式 kw2|msg_id|index
    if data.startswith('kw2|'):
        _, msg_id, idx_str = data.split('|')
        state = pending_keyword.get(msg_id)
        if not state:
            await query.edit_message_text('❌ 狀態已過期，請重新記帳。')
            return

        cat = state['filtered'][int(idx_str)]
        keyword  = state['keyword']
        budget   = cat['budget']
        category = cat['category']
        attr     = cat['attr']

        kw_result       = pennywise_tools.add_keyword_to_sheet(keyword, budget, category, attr)
        backfill_result = pennywise_tools.backfill_category(msg_id, category, budget, attr)

        del pending_keyword[msg_id]
        await query.edit_message_text(f'{kw_result}\n{backfill_result}')
        return

    await query.edit_message_text('❌ 未知選項')


# --- 解析記帳訊息 ---
def parse_expense(raw_input):
    parts = raw_input.strip().split()
    if len(parts) < 3:
        return None
    code       = parts[-1]
    amount_str = parts[-2]
    item       = ' '.join(parts[:-2])
    if not amount_str.isdigit():
        return None
    if 'v' not in code and 's' not in code:
        return None
    who     = 'Vera' if 'v' in code else 'Shen'
    payment = '信用卡' if 'cc' in code else '現金'
    return {'item': item, 'amount': amount_str, 'who': who, 'payment': payment}


# --- 記帳處理 ---
async def process_data(update: Update, is_edit=False):
    msg = update.edited_message if is_edit else update.message
    if not msg or not msg.text:
        return

    raw_input = msg.text
    msg_id    = str(msg.message_id)

    parsed = parse_expense(raw_input)
    if not parsed:
        return

    try:
        item    = parsed['item']
        amount  = parsed['amount']
        who     = parsed['who']
        payment = parsed['payment']

        keyword_config          = pennywise_tools.load_keywords_from_sheet()
        category, budget, attr  = pennywise_tools.classify_item(item, keyword_config)

        if is_edit:
            result = pennywise_tools.update_expense(item, amount, category, budget, attr, who, payment, msg_id)
        else:
            result = pennywise_tools.save_expense(item, amount, category, budget, attr, who, payment, msg_id)

        await msg.reply_text(
            f"{'✏️ 編輯成功' if is_edit else '✅ 記帳成功'}！\n"
            f"項目：{item}\n金額：{amount}\n"
            f"分類：{category}（{attr}）\n"
            f"付款人：{who}\n方式：{payment}\n\n{result}"
        )

        # 分類是 N/A，詢問新增關鍵字（兩步驟）
        if category == 'N/A' and not is_edit:
            keyword    = item.split()[-1]
            categories = pennywise_tools.get_all_categories()

            # 存狀態
            pending_keyword[msg_id] = {'keyword': keyword, 'categories': categories}

            # 第一步：列出預算類別
            budgets  = sorted(set(c['budget'] for c in categories))
            keyboard = []
            for b in budgets:
                cb = f"kw1|{msg_id}|{b}"
                keyboard.append([InlineKeyboardButton(b, callback_data=cb)])
            keyboard.append([InlineKeyboardButton('略過', callback_data='kw_skip')])

            await msg.reply_text(
                f'「{keyword}」找不到分類，要加入關鍵字清單嗎？\n請先選預算類別：',
                reply_markup=InlineKeyboardMarkup(keyboard)
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
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE & filters.TEXT, handle_edit))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print('🚀 機器人上線！')
    app.run_polling(allowed_updates=Update.ALL_TYPES)
