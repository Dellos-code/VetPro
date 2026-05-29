"""
VetPro - Shared UI Utilities
Κοινά widgets, χρώματα και helpers για όλες τις οθόνες.
"""
import tkinter as tk
from tkinter import font as tkfont

# ── Palette ──────────────────────────────────────────────────────────────────
COLORS = {
    "bg_main":    "#D3D3D3",
    "sidebar":    "#87CEEB",
    "logo_fg":    "#9932CC",
    "btn_blue":   "#4DA6FF",
    "btn_green":  "#28A745",
    "btn_red":    "#DC143C",
    "btn_gray":   "#6c757d",
    "white":      "#FFFFFF",
    "text":       "#333333",
}

def make_sidebar(root, buttons: list, width=220):
    """
    Δημιουργεί sidebar με λογότυπο και κουμπιά.
    buttons: [(label, command), ...]
    Επιστρέφει το Frame του sidebar.
    """
    frame = tk.Frame(root, bg=COLORS["sidebar"], width=width)
    frame.pack(side="left", fill="y")
    frame.pack_propagate(False)

    lf = tkfont.Font(family="Arial", size=20, weight="bold")
    tk.Label(frame, text="🐾 VetPro", font=lf,
             bg=COLORS["sidebar"], fg=COLORS["logo_fg"]).pack(pady=(18, 24))

    for label, cmd in buttons:
        tk.Button(
            frame, text=label,
            font=("Arial", 9, "bold"),
            bg=COLORS["sidebar"], fg=COLORS["text"],
            anchor="w", padx=14, pady=4,
            bd=1, relief="solid", cursor="hand2",
            command=cmd
        ).pack(fill="x", padx=8, pady=2)

    return frame


def make_main_frame(root):
    frame = tk.Frame(root, bg=COLORS["bg_main"])
    frame.pack(side="left", fill="both", expand=True)
    return frame


def clear_frame(frame):
    for w in frame.winfo_children():
        w.destroy()


def rounded_box(parent, x, y, w, h, bg, title, value, value_color="#0000FF", command=None):
    """Σχεδιάζει rounded πλαίσιο με τίτλο και αριθμό."""
    cursor = "hand2" if command else ""
    c = tk.Canvas(parent, width=w, height=h, bg=COLORS["bg_main"],
                  highlightthickness=0, cursor=cursor)
    c.place(x=x, y=y)
    r = 14
    for ax, ay in [(0,0),(w-2*r,0),(0,h-2*r),(w-2*r,h-2*r)]:
        starts = [90, 0, 180, 270]
        idx = [(0,0),(w-2*r,0),(0,h-2*r),(w-2*r,h-2*r)].index((ax,ay))
        c.create_arc(ax, ay, ax+2*r, ay+2*r, start=starts[idx], extent=90,
                     fill=bg, outline=bg)
    c.create_rectangle(r, 0, w-r, h, fill=bg, outline=bg)
    c.create_rectangle(0, r, w, h-r, fill=bg, outline=bg)
    c.create_text(10, 10, text=title, anchor="nw",
                  font=("Arial", 9, "bold"), fill="black")
    c.create_text(w-8, h-8, text=str(value), anchor="se",
                  font=("Arial", 13, "bold"), fill=value_color)
    if command:
        c.bind("<Button-1>", lambda e: command())
    return c


def action_btn(parent, text, command, bg=None, fg="white", width=18, pady=8):
    bg = bg or COLORS["btn_blue"]
    return tk.Button(parent, text=text, command=command,
                     bg=bg, fg=fg, font=("Arial", 10, "bold"),
                     width=width, pady=pady, bd=0, cursor="hand2",
                     activebackground=bg)


def section_title(parent, text, font_size=16):
    tk.Label(parent, text=text,
             font=("Arial", font_size, "bold"),
             bg=COLORS["bg_main"], fg=COLORS["text"]).pack(anchor="w", padx=16, pady=(14, 6))


def field_row(parent, label, var_or_widget=None, width=28):
    """
    Δημιουργεί μια γραμμή label + Entry.
    Αν δοθεί StringVar επιστρέφει Entry, αλλιώς μόνο label.
    """
    row = tk.Frame(parent, bg=COLORS["bg_main"])
    row.pack(fill="x", padx=16, pady=3)
    tk.Label(row, text=label, font=("Arial", 10),
             bg=COLORS["bg_main"], fg=COLORS["text"], width=22, anchor="w").pack(side="left")
    if var_or_widget is not None:
        e = tk.Entry(row, textvariable=var_or_widget,
                     font=("Arial", 10), width=width)
        e.pack(side="left")
        return e
    return None
