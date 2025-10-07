from __future__ import annotations
from typing import Dict
import datetime, calendar, re

def parse_key_date_suffix(key: str):
    m = re.match(r"^\s*(\d{2})/(\d{2})/(\d{4})\s*-\s*(.+)\s*$", key or "")
    if not m:
        return None, None
    d, mth, y, suf = m.groups()
    try:
        dt = datetime.date(int(y), int(mth), int(d))
        return dt, suf.strip()
    except Exception:
        return None, None

def suffix_letter(suffix_full: str) -> str:
    return (suffix_full or " ").strip()[0].upper()

def last_day_of_month(year: int, month: int) -> int:
    return calendar.monthrange(year, month)[1]

def add_months(dt: datetime.date, n: int) -> datetime.date:
    y = dt.year + (dt.month - 1 + n) // 12
    m = (dt.month - 1 + n) % 12 + 1
    d = min(dt.day, last_day_of_month(y, m))
    return datetime.date(y, m, d)

def add_years(dt: datetime.date, n: int) -> datetime.date:
    y = dt.year + n
    m = dt.month
    d = min(dt.day, last_day_of_month(y, m))
    return datetime.date(y, m, d)

def format_key(dt: datetime.date, suffix: str) -> str:
    return f"{dt.strftime('%d/%m/%Y')} -{suffix}"

def shift_value_map(value_map: Dict[str, str], unit: str, amount: int, filter_mode: str):
    """Retorna (new_map, stats). filter_mode: 'Todas' | 'Só T (Teóricas)' | 'Só P (Práticas)'."""
    result_map: Dict[str, str] = {}
    changed = 0
    invalid = 0
    skipped_filter = 0
    overwritten_lote = 0

    for key, text in list(value_map.items()):
        dt, suf_full = parse_key_date_suffix(key)
        if not dt:
            result_map[key] = text
            invalid += 1
            continue

        suf_letter = suffix_letter(suf_full)  # P/T/…
        if filter_mode.startswith("Só T") and suf_letter != "T":
            result_map[key] = text
            skipped_filter += 1
            continue
        if filter_mode.startswith("Só P") and suf_letter != "P":
            result_map[key] = text
            skipped_filter += 1
            continue

        if unit == "Dias":
            new_dt = dt + datetime.timedelta(days=amount)
        elif unit == "Meses":
            new_dt = add_months(dt, amount)
        else:
            new_dt = add_years(dt, amount)

        new_key = format_key(new_dt, suf_full)
        if new_key in result_map:
            overwritten_lote += 1
        result_map[new_key] = text
        changed += 1

    stats = {
        "changed": changed,
        "invalid": invalid,
        "filtered": skipped_filter,
        "overwritten_in_lot": overwritten_lote,
    }
    return dict(sorted(result_map.items(), key=lambda kv: kv[0])), stats