import re
from datetime import timedelta, timezone
from email.utils import parsedate_to_datetime

BJ = timezone(timedelta(hours=8))


def conv(t):
    t = (t or "").replace("\\n", "\n")

    def rep(m):
        try:
            d = parsedate_to_datetime(m.group(1).strip())
            if d.tzinfo is None:
                d = d.replace(tzinfo=timezone.utc)
            bj = d.astimezone(BJ)
            return f"**Published Date:** {bj:%Y-%m-%d %H:%M}（北京时间）"
        except Exception:
            return m.group(0)

    return re.sub(r"\*\*Published Date:\*\*\s*([^\n]+)", rep, t)


# 主工作流：每路一个节点，输入 s（本路 Tavily text；企微接聚合器 output），输出 t（String）
def main(s: str) -> dict:
    return {"t": conv(s)}
