import os, json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime


def _get_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    if creds_json:
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    return client.open('Pennywise記帳本')


def load_keywords_from_sheet():
    try:
        rows = _get_sheet().worksheet('keywords').get_all_values()
        result = []
        for row in rows[1:]:
            if len(row) < 4 or not row[1]:
                continue
            result.append({
                'budget':   row[0].strip(),
                'category': row[1].strip(),
                'attr':     row[2].strip(),
                'keywords': [k.strip() for k in row[3].split(',') if k.strip()],
            })
        return result
    except Exception as e:
        print(f'⚠️ 無法讀取關鍵字設定: {e}')
        return []

def classify_item(item, keyword_config):
    item_lower = item.lower()
    for cfg in keyword_config:
        for kw in cfg['keywords']:
            if kw.lower() in item_lower:
                return cfg['category'], cfg['budget'], cfg['attr']
    return 'N/A', 'N/A', 'N/A'

def _get_rows(month=None):
    """讀取所有資料列，month 為 int 時只回傳該月"""
    sheet = _get_sheet().sheet1
    all_data = sheet.get_all_values()
    if len(all_data) <= 1:
        return []
    rows = []
    for row in all_data[1:]:
        if len(row) < 6:
            continue
        try:
            amount = int(row[5])
        except ValueError:
            continue
        if month:
            try:
                row_month = int(row[0].split('-')[1])
                if row_month != month:
                    continue
            except Exception:
                continue
        rows.append(row)
    return rows

def get_summary_report(month=None):
    """本月總覽（或指定月份）"""
    try:
        label = f'{month}月' if month else '本月'
        m = month or datetime.now().month
        rows = _get_rows(month=m)
        if not rows:
            return f'⚠️ {label}還沒有資料喔！'

        total, by_payer, by_owner = 0, {}, {}
        for row in rows:
            amount = int(row[5])
            payer  = row[6]
            owner  = row[11] if len(row) > 11 and row[11].strip() else payer
            total += amount
            by_payer[payer] = by_payer.get(payer, 0) + amount
            by_owner[owner] = by_owner.get(owner, 0) + amount

        lines = [
            f'📅 {label}總覽',
            '=' * 22,
            f'💰 總支出: ${total}',
            '',
            '💳 付款人（誰付的錢）:',
        ]
        for who, amt in sorted(by_payer.items(), key=lambda x: -x[1]):
            emoji = '👩‍💻' if who == 'Vera' else ('👨‍💻' if who == 'Shen' else '👤')
            pct = amt / total * 100
            lines.append(f'  {emoji} {who}: ${amt} ({pct:.0f}%)')

        lines += ['', '🎯 使用歸屬（花在誰身上）:']
        for who, amt in sorted(by_owner.items(), key=lambda x: -x[1]):
            emoji = '👩‍💻' if who == 'Vera' else ('👨‍💻' if who == 'Shen' else '👫')
            pct = amt / total * 100
            lines.append(f'  {emoji} {who}: ${amt} ({pct:.0f}%)')

        return '\n'.join(lines)
    except Exception as e:
        return f'❌ 報表錯誤: {e}'

def get_category_report(month=None):
    """依分類報表"""
    try:
        label = f'{month}月' if month else '本月'
        m = month or datetime.now().month
        rows = _get_rows(month=m)
        if not rows:
            return f'⚠️ {label}還沒有資料喔！'

        total, by_cat = 0, {}
        for row in rows:
            amount = int(row[5])
            cat    = row[3]
            total += amount
            by_cat[cat] = by_cat.get(cat, 0) + amount

        lines = [f'🍰 {label}分類報表', '=' * 22, f'💰 總支出: ${total}', '']
        for cat, amt in sorted(by_cat.items(), key=lambda x: -x[1]):
            pct = amt / total * 100
            bar = '█' * int(pct / 5)  # 每 5% 一格
            lines.append(f'  {cat}: ${amt} ({pct:.0f}%) {bar}')

        return '\n'.join(lines)
    except Exception as e:
        return f'❌ 報表錯誤: {e}'

def get_budget_report(month=None):
    """預算類別佔比（631 分析）"""
    try:
        label = f'{month}月' if month else '本月'
        m = month or datetime.now().month
        rows = _get_rows(month=m)
        if not rows:
            return f'⚠️ {label}還沒有資料喔！'

        total, by_budget = 0, {}
        for row in rows:
            amount = int(row[5])
            budget = row[9] if len(row) > 9 and row[9].strip() else 'N/A'
            if budget == '不列入分析':
                continue
            total += amount
            by_budget[budget] = by_budget.get(budget, 0) + amount

        # 631 理想佔比
        ideal = {'生活開銷': 60, '儲蓄投資': 30, '風險彈性': 10}

        lines = [f'📊 {label}預算類別佔比（631）', '=' * 22, f'💰 總支出（不含轉帳）: ${total}', '']
        for budget, amt in sorted(by_budget.items(), key=lambda x: -x[1]):
            pct    = amt / total * 100 if total else 0
            target = ideal.get(budget, 0)
            diff   = pct - target
            status = '✅' if abs(diff) <= 5 else ('⬆️' if diff > 0 else '⬇️')
            lines.append(f'  {status} {budget}')
            lines.append(f'     ${amt} ({pct:.0f}%) ／目標 {target}%')

        return '\n'.join(lines)
    except Exception as e:
        return f'❌ 報表錯誤: {e}'

def update_expense(item, amount, category, budget, attr, who, payment, msg_id):
    try:
        sheet = _get_sheet().sheet1
        cell = sheet.find(str(msg_id))
        if cell:
            sheet.update(
                f'D{cell.row}:K{cell.row}',
                [[category, item, amount, who, payment, str(msg_id), budget, attr]]
            )
            return f'✏️ 已修正: {item} ${amount}'
        return save_expense(item, amount, category, budget, attr, who, payment, msg_id)
    except Exception as e:
        return f'❌ 修正失敗: {e}'

def save_expense(item, amount, category, budget, attr, who, payment, msg_id):
    try:
        sheet = _get_sheet().sheet1
        now = datetime.now()
        row = [
            now.strftime('%Y-%m-%d'),
            f"週{['一','二','三','四','五','六','日'][now.weekday()]}",
            now.strftime('%H:%M:%S'),
            category, item, amount, who, payment, str(msg_id), budget, attr
        ]
        sheet.append_row(row)
        return '☁️ 已同步上雲端'
    except Exception as e:
        return f'❌ 存檔失敗: {e}'
