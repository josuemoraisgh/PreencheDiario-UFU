from __future__ import annotations
from pathlib import Path
from typing import Optional, Callable

COOKIE_FILE = Path("cookie.txt")

def save_cookie_file(header: str, path: Path = COOKIE_FILE):
    path.write_text(header.strip() + "\n", encoding="utf-8")

def read_cookie_file(path: Path = COOKIE_FILE) -> Optional[str]:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8").strip()

def test_cookie_header(header: str, logger: Optional[Callable[[str], None]] = None) -> bool:
    ok = bool(header and "=" in header)
    if logger:
        logger(f"[cookies] Teste de cookie: {'ok' if ok else 'inválido'}")
    return ok
