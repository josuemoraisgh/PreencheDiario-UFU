# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Callable, Tuple
from selenium.webdriver.remote.webdriver import WebDriver

# services/diario.py
# ---------- JS helpers (corrigidos) ----------
FIND_RELATED_TEXTAREA_JS = r"""
const KEY = arguments[0];

function norm(s){
  if(!s) return '';
  return s.toLowerCase()
          .normalize('NFD').replace(/[\u0300-\u036f]/g,'')   // remove acentos
          .replace(/[–—]/g,'-')                              // traços longos -> '-'
          .replace(/\s+/g,' ')                               // espaços duplicados
          .trim();
}
const key = norm(KEY);

// 1) Procurar *linhas* candidatas cujo texto contenha a chave
const rowSelectors = ['tr', '.row', '.linha', '.form-group', 'li', '.item'];
let rows = [];
for (const sel of rowSelectors) {
  rows = rows.concat(Array.from(document.querySelectorAll(sel)));
}
rows = rows.filter(el => {
  try{
    if (!el.offsetParent) return false;       // invisível
    return norm(el.textContent || '').includes(key);
  }catch(e){ return false; }
});

// 2) Dentro da própria linha, pegar o textarea
for (const row of rows){
  // caso simples: textarea dentro da mesma linha/bloco
  const taInRow = row.querySelector('textarea');
  if (taInRow) return taInRow;

  // caso mais comum em tabela: a célula com a data está numa <td>, textarea na <td> seguinte
  if (row.tagName === 'TR'){
    const tds = Array.from(row.children);
    // qual td contém a chave?
    let idx = -1;
    for (let i=0;i<tds.length;i++){
      if (norm(tds[i].textContent || '').includes(key)) { idx = i; break; }
    }
    if (idx >= 0){
      for (let j = idx+1; j < tds.length; j++){
        const ta = tds[j].querySelector('textarea');
        if (ta) return ta;
      }
    }
  }
}

// 3) Último recurso "perto da label": irmãos próximos (mas *não* sobe para table/tbody)
const allLabels = Array.from(document.querySelectorAll('body *')).filter(el=>{
  try{
    if (!el.offsetParent) return false;
    return norm(el.textContent || '').includes(key);
  }catch(e){ return false; }
});
function findTextareaNear(el){
  // procura nos irmãos diretos da label até uns passos
  let sib = el.nextElementSibling;
  for (let i=0; i<5 && sib; i++, sib = sib.nextElementSibling){
    if (sib.tagName === 'TEXTAREA') return sib;
    const inside = sib.querySelector ? sib.querySelector('textarea') : null;
    if (inside) return inside;
  }
  // filhos diretos
  const taChild = el.querySelector ? el.querySelector('textarea') : null;
  if (taChild) return taChild;
  return null; // sem fallback global
}
for (const el of allLabels){
  const ta = findTextareaNear(el);
  if (ta) return ta;
}

return null;
"""

FILL_TEXTAREA_JS = r"""
const ta = arguments[0];
const text = arguments[1] || '';
const highlight = !!arguments[2];

try { ta.scrollIntoView({behavior:'auto', block:'center', inline:'nearest'}); } catch(e) {}

ta.focus();
ta.value = text;
ta.dispatchEvent(new Event('input', {bubbles:true}));
ta.dispatchEvent(new Event('change', {bubbles:true}));

if (highlight){
  const oldOutline = ta.style.outline;
  ta.style.outline = '3px solid orange';
  setTimeout(()=>{ ta.style.outline = oldOutline; }, 800);
}
return true;
"""

CLICK_SAVE_BUTTON_JS = r"""
// (deixe sua lógica de localizar o botão Salvar/Gravar como já estava)
"""

# ---------- API usada pela UI ----------

def fill_entries(
    driver: WebDriver,
    value_map: dict[str, str],
    logger: Callable[[str], None],
    *,
    strict: bool = True,          # agora padrão estrito: NÃO usa fallback global
    require_empty: bool = False,  # se True, pula campos que já têm conteúdo
    highlight: bool = True,       # destaca o campo preenchido
) -> Tuple[int, int, int]:
    """
    Preenche item-a-item. Retorna (ok, nao_encontradas, pulado_ja_preenchido).
    - strict=True: não preenche se não localizar textarea relacionado.
    - require_empty=True: só preenche se o textarea estiver vazio (evita sobrescrever).
    """
    ok = 0
    not_found = 0
    skipped_filled = 0

    # IMPORTANTE: garantir ordem por chave já vem da UI; aqui iteramos na ordem recebida
    for k, v in value_map.items():
        logger(f"→ Preenchendo: {k}")
        try:
            # procura textarea relacionado à label/data
            textarea = driver.execute_script(FIND_RELATED_TEXTAREA_JS, k)
            if not textarea:
                logger(f"   não encontrei textarea para '{k}'")
                not_found += 1
                continue  # STRICT: não tenta fallback algum

            if require_empty:
                current = driver.execute_script("return arguments[0].value || '';", textarea) or ""
                if str(current).strip():
                    logger("   pulado (já havia conteúdo)")
                    skipped_filled += 1
                    continue

            # preencher + eventos + highlight
            driver.execute_script(FILL_TEXTAREA_JS, textarea, v, highlight)
            logger("   ok")
            ok += 1

        except Exception as e:
            # qualquer erro neste item não deve contaminar os demais
            logger(f"   erro: {e}")
            not_found += 1  # contabiliza como falho/não preenchido

    return ok, not_found, skipped_filled


def try_click_save(driver: WebDriver, logger: Callable[[str], None]) -> None:
    try:
        clicked = driver.execute_script(CLICK_SAVE_BUTTON_JS)
        if clicked:
            logger("Cliquei em Salvar/Gravar.")
        else:
            logger("Não localizei botão Salvar/Gravar.")
    except Exception as e:
        logger(f"Falha ao tentar salvar: {e}")
