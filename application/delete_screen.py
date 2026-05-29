"""VetPro - Delete Account Screen"""
import tkinter as tk
from tkinter import messagebox
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_setup import get_connection
from utils.ui_helpers import COLORS

class DeleteScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("VetPro - Διαγραφή Λογαριασμού")
        self.root.geometry("380x300")
        self.root.configure(bg="#FFCCCC")
        self._build()

    def _build(self):
        cf = tk.Frame(self.root, bg="#FFCCCC")
        cf.pack(expand=True)
        tk.Label(cf, text="⚠️ Διαγραφή", font=("Arial", 22, "bold"),
                 bg="#FFCCCC", fg="#CC0000").pack(pady=(0, 16))
        for lbl, attr, show in [
            ("Όνομα Χρήστη:", "u_entry", ""),
            ("Κωδικός:",      "p_entry", "*"),
        ]:
            tk.Label(cf, text=lbl, font=("Arial", 11), bg="#FFCCCC").pack(anchor="w", padx=20)
            e = tk.Entry(cf, font=("Arial", 11), width=26, show=show)
            e.pack(padx=20, pady=(0, 8))
            setattr(self, attr, e)

        tk.Button(cf, text="Οριστική Διαγραφή", command=self._delete,
                  bg="#CC0000", fg="white", font=("Arial", 11, "bold"),
                  width=22, bd=0, pady=7, cursor="hand2").pack(pady=10)

    def _delete(self):
        u = self.u_entry.get().strip()
        p = self.p_entry.get().strip()
        if not u or not p:
            messagebox.showwarning("Ελλιπή", "Συμπληρώστε στοιχεία.")
            return
        if not messagebox.askyesno("Επιβεβαίωση", "Σίγουρα θέλετε να διαγράψετε τον λογαριασμό;"):
            return
        conn = get_connection()
        user = conn.execute("SELECT id FROM users WHERE username=? AND password=?", (u, p)).fetchone()
        if user:
            conn.execute("DELETE FROM users WHERE id=?", (user["id"],))
            conn.commit()
            messagebox.showinfo("Επιτυχία", "Ο λογαριασμός διαγράφηκε.")
            self.root.destroy()
        else:
            messagebox.showerror("Σφάλμα", "Λάθος στοιχεία.")
        conn.close()
