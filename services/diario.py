# services/diario.py
from __future__ import annotations
from typing import Dict
from selenium.webdriver.remote.webdriver import WebDriver
import re

# ---------- JS helpers em strings RAW (evita warnings por \s etc.) ----------
FIND_RELATED_TEXTAREA_JS = r"""
const label = arguments[0];

function* textNodesUnder(el) {
  const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null, false);
  let n;
  while (n = walker.nextNode()) { yield n; }
}
function normalize(s) { return (s || "").replace(/\s+/g, " ").trim(); }

let candidates = [];
for (const n of textNodesUnder(document.body)) {
  const text = normalize(n.textContent);
  if (text && text.includes(label)) {
    let el = n.parentElement;
    let depth = 0;
    while (el && depth < 6) {
      const ta = el.querySelector("textarea, [contenteditable='true']");
      if (ta) { candidates.push(ta); break; }
      el = el.parentElement;
      depth++;
    }
  }
}
if (!candidates.length) {
  const glob = document.querySelector("textarea, [contenteditable='true']");
  if (glob) candidates.push(glob);
}
return candidates.length ? candidates[0] : null;
"""

SET_TEXTAREA_VALUE_JS = r"""
const el = arguments[0];
const text = arguments[1];
function setValue(elem, value) {
  if (!elem) return;
  const isTA = elem.tagName && elem.tagName.toLowerCase() === "textarea";
  if (isTA) {
    elem.focus();
    elem.value = value;
    elem.dispatchEvent(new Event("input", { bubbles: true }));
    elem.dispatchEvent(new Event("change", { bubbles: true }));
  } else if (elem.isContentEditable) {
    elem.focus();
    elem.innerText = value;
    elem.dispatchEvent(new Event("input", { bubbles: true }));
    elem.dispatchEvent(new Event("change", { bubbles: true }));
  }
}
setValue(el, text);
return true;
"""

CLICK_SAVE_BUTTON_JS = r"""
const labels = ["Salvar", "Gravar", "Salvar/Gravar", "Salvar Diário", "Gravar Diário"];
function norm(s){ return (s||"").replace(/\s+/g," ").trim().toLowerCase(); }
function matchLabel(el){
  const t = norm(el.innerText || el.value || el.getAttribute("title") || "");
  return labels.map(x=>x.toLowerCase()).some(l => t.includes(l));
}
let btn = null;
const selectors = ["button", "input[type='button']", "input[type='submit']", "[role='button']"];
for (const sel of selectors) {
  for (const el of document.querySelectorAll(sel)) {
    if (matchLabel(el)) { btn = el; break; }
  }
  if (btn) break;
}
if (!btn) { btn = document.querySelector("button, [role='button'], input[type='submit']"); }
if (btn) { btn.click(); return true; }
return false;
"""

def get_current_turma_info(driver: WebDriver):
    """Tenta extrair (idTurma, tipo) pela URL ou por inputs hidden."""
    url = driver.current_url or ""
    m = re.search(r"[?&]idTurma=([^&#]+)", url)
    n = re.search(r"[?&]tipo=([^&#]+)", url)
    if m and n:
        return m.group(1), n.group(1)

    # fallback DOM seguro (sem quebrar aspas do Python)
    try:
        id_turma = driver.execute_script(
            r"""const el = document.querySelector('[name="idTurma"]'); return el ? el.value : null;"""
        )
        tipo = driver.execute_script(
            r"""const el = document.querySelector('[name="tipo"]'); return el ? el.value : null;"""
        )
        if id_turma and tipo:
            return str(id_turma), str(tipo)
    except Exception:
        pass

    return None

def fill_entries(driver: WebDriver, value_map: Dict[str, str], logger):
    """Percorre o dict {label: texto} e tenta preencher o textarea relacionado."""
    ok = 0
    fail = 0
    for label, text in value_map.items():
        logger(f"→ Preenchendo: {label}")
        try:
            el = driver.execute_script(FIND_RELATED_TEXTAREA_JS, label)
            if el:
                driver.execute_script(SET_TEXTAREA_VALUE_JS, el, text)
                logger("   ok")
                ok += 1
            else:
                logger(f"   não encontrei textarea para {label!r}")
                fail += 1
        except Exception as e:
            logger(f"   erro: {e}")
            fail += 1
    return ok, fail

def try_click_save(driver: WebDriver, logger):
    """Tenta localizar e clicar um botão de Salvar/Gravar."""
    try:
        res = driver.execute_script(CLICK_SAVE_BUTTON_JS)
        logger("Cliquei em Salvar/Gravar." if res else "Não localizei botão Salvar/Gravar.")
        return bool(res)
    except Exception as e:
        logger(f"Erro ao tentar salvar: {e}")
        return False