from typing import Optional, Tuple, List
from tkinter import Frame, Label, Entry, Button, StringVar
from tkinter import ttk
from .centerlevel import Centerlevel

def ask_edit_item(parent, initial_key: str, initial_text: str) -> Optional[Tuple[str, str]]:
    """Modal para editar chave e texto; retorna (new_key, new_text) ou None."""
    win = Centerlevel(parent)
    win.title("Editar item")

    Label(win, text="Chave (DD/MM/AAAA -X):").grid(row=0, column=0, sticky="w", padx=8, pady=(8, 4))
    var_key = StringVar(value=initial_key)
    ent_key = Entry(win, textvariable=var_key, width=40)
    ent_key.grid(row=1, column=0, sticky="we", padx=8)

    Label(win, text="Texto:").grid(row=2, column=0, sticky="w", padx=8, pady=(8, 4))
    var_txt = StringVar(value=initial_text)
    ent_txt = Entry(win, textvariable=var_txt, width=80)
    ent_txt.grid(row=3, column=0, sticky="we", padx=8)

    btns = Frame(win); btns.grid(row=4, column=0, sticky="e", padx=8, pady=8)
    result = [None]

    def _ok():
        result[0] = (var_key.get().strip(), var_txt.get())
        win.destroy()

    def _cancel():
        win.destroy()

    Button(btns, text="Cancelar", command=_cancel).pack(side="right", padx=4)
    Button(btns, text="OK", command=_ok).pack(side="right", padx=4)

    win.columnconfigure(0, weight=1)
    ent_key.focus_set()
    parent.wait_window(win)
    return result[0]  # type: ignore[return-value]

def choose_from_list(parent, title: str, options: List[str]) -> Optional[str]:
    """Modal simples para escolher 1 item de uma lista."""
    if not options:
        return None
    win = Centerlevel(parent)
    win.title(title)

    Label(win, text=title).grid(row=0, column=0, padx=8, pady=(8,4), sticky="w")
    var = StringVar(value=options[0])
    cb = ttk.Combobox(win, textvariable=var, values=options, state="readonly", width=40)
    cb.grid(row=1, column=0, padx=8, pady=4, sticky="we")

    res = [None]
    def _ok(): res[0] = var.get(); win.destroy()
    def _cancel(): win.destroy()

    btns = Frame(win); btns.grid(row=2, column=0, sticky="e", padx=8, pady=8)
    Button(btns, text="Cancelar", command=_cancel).pack(side="right", padx=4)
    Button(btns, text="OK", command=_ok).pack(side="right", padx=4)

    win.columnconfigure(0, weight=1)
    cb.focus_set()
    parent.wait_window(win)
    return res[0]  # type: ignore[return-value]

def ask_shift_params(parent) -> Optional[tuple[str, int, str]]:
    """Pergunta (unidade, valor, filtro). Retorna ('Dias'|'Meses'|'Anos', int, 'Todas'|'Só T (Teóricas)'|'Só P (Práticas)')."""
    from tkinter import messagebox
    win = Centerlevel(parent)
    win.title("Ajustar datas das chaves")

    # Unidade
    Label(win, text="Unidade:").grid(row=0, column=0, sticky="w", padx=8, pady=(8, 4))
    unit_var = StringVar(value="Dias")
    cbo_unit = ttk.Combobox(win, textvariable=unit_var,
                            values=["Dias", "Meses", "Anos"],
                            state="readonly", width=12)
    cbo_unit.grid(row=0, column=1, sticky="w", padx=8, pady=(8, 4))

    # Valor
    Label(win, text="Valor (inteiro, pode ser negativo):").grid(row=1, column=0, sticky="w", padx=8, pady=4)
    val_var = StringVar(value="1")
    ent_val = Entry(win, textvariable=val_var, width=12)
    ent_val.grid(row=1, column=1, sticky="w", padx=8, pady=4)

    # Filtro (Todas / T / P)
    Label(win, text="Aplicar em:").grid(row=2, column=0, sticky="w", padx=8, pady=4)
    filt_var = StringVar(value="Todas")
    cbo_filt = ttk.Combobox(win, textvariable=filt_var,
                            values=["Todas", "Só T (Teóricas)", "Só P (Práticas)"],
                            state="readonly", width=16)
    cbo_filt.grid(row=2, column=1, sticky="w", padx=8, pady=4)

    res = [None]
    def _ok():
        try:
            amount = int(val_var.get().strip())
        except ValueError:
            messagebox.showerror("Valor inválido", "Informe um inteiro (ex.: -7, 0, 15).", parent=parent)
            return
        res[0] = (unit_var.get(), amount, filt_var.get())
        win.destroy()

    def _cancel(): win.destroy()

    btns = Frame(win); btns.grid(row=3, column=0, columnspan=2, sticky="e", padx=8, pady=8)
    Button(btns, text="Cancelar", command=_cancel).pack(side="right", padx=4)
    Button(btns, text="Aplicar", command=_ok).pack(side="right", padx=4)

    win.columnconfigure(0, weight=0)
    win.columnconfigure(1, weight=1)
    cbo_unit.focus_set()
    parent.wait_window(win)
    return res[0]