import re
import json
from datetime import timedelta, timezone
from email.utils import parsedate_to_datetime

BJ = timezone(timedelta(hours=8))


def norm(u):
    return (u or '').strip().rstrip('/')


def parse_results(text):
    # 从 Tavily 的 text 里取出 {url: Published Date}
    text = (text or '').replace('\\n', '\n')
    res = {}
    for block in text.split('# Result ')[1:]:
        u = re.search(r'\*\*URL:\*\*\s*(\S+)', block)
        d = re.search(r'\*\*Published Date:\*\*\s*(.+)', block)
        if u:
            res[norm(u.group(1))] = d.group(1).strip() if d else ''
    return res


def main(draft, s1: str, s2: str, s3: str, today: str) -> dict:
    if isinstance(draft, str):
        draft = json.loads(draft)
    src = {}
    for s in (s1, s2, s3):
        src.update(parse_results(s))

    issues = []
    for it in draft.get('items', []):
        t = it.get('title', '')
        url = norm(it.get('url'))
        if not url:
            issues.append(f'《{t}》缺少链接')
            continue
        if not re.sub(r'^https?://[^/]+', '', url).strip('/'):
            issues.append(f'《{t}》链接是网站首页')
        if url not in src:
            issues.append(f'《{t}》链接不在原始搜索结果中')
            continue
        raw = src[url]
        if not raw:
            issues.append(f'《{t}》搜索结果没有发布日期')
            continue
        try:
            dt = parsedate_to_datetime(raw)
        except Exception:
            issues.append(f'《{t}》发布日期无法解析：{raw}')
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        day = dt.astimezone(BJ).strftime('%Y-%m-%d')
        if day != today:
            issues.append(f'《{t}》发布日期是 {day}（北京时间），不是今天 {today}')

    return {'hard_issues': '；'.join(issues) if issues else '无'}
