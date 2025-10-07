from tkinter import Toplevel

def Centerlevel(parent, *, transient=True, grab=True, center_on_parent=True, topmost_pulse=True, **kwargs):
    """Drop-in helper: use Centerlevel(self) instead of Toplevel(self) to open centered."""
    win = Toplevel(parent, **kwargs)

    if transient:
        try: win.transient(parent)
        except Exception: pass

    try: win.withdraw()
    except Exception: pass

    def _center_once():
        try:
            win.update_idletasks()
            try:
                win.eval(f'tk::PlaceWindow {win.winfo_pathname(win.winfo_id())} center')
                if center_on_parent:
                    raise Exception("force-manual-parent-center")
            except Exception:
                if center_on_parent and parent is not None:
                    parent.update_idletasks()
                    px, py = parent.winfo_rootx(), parent.winfo_rooty()
                    pw, ph = parent.winfo_width(), parent.winfo_height()
                    w, h = win.winfo_reqwidth(), win.winfo_reqheight()
                    if pw <= 1 or ph <= 1:
                        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
                        x, y = (sw - w)//2, (sh - h)//2
                    else:
                        x, y = px + (pw - w)//2, py + (ph - h)//2
                else:
                    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
                    w, h = win.winfo_reqwidth(), win.winfo_reqheight()
                    x, y = (sw - w)//2, (sh - h)//2
                win.geometry(f"+{x}+{y}")

            try: win.deiconify()
            except Exception: pass

            if topmost_pulse:
                try:
                    win.lift()
                    win.attributes("-topmost", True)
                    win.after(10, lambda: win.attributes("-topmost", False))
                except Exception:
                    pass

            if grab:
                try: win.grab_set()
                except Exception: pass

        except Exception:
            try: win.deiconify()
            except Exception: pass

    win.after(0, _center_once)
    win.after(120, _center_once)
    return win