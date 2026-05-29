"""
VetPro - Login Screen
"""
import tkinter as tk
from tkinter import messagebox
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_setup import get_connection
from utils.ui_helpers import COLORS

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("VetPro - Σύνδεση")
        self.root.geometry("420x460")
        self.root.configure(bg=COLORS["sidebar"])
        self.root.resizable(False, False)
        self._build()

    def _build(self):
        cf = tk.Frame(self.root, bg=COLORS["sidebar"])
        cf.pack(expand=True)

        tk.Label(cf, text="🐾 VetPro", font=("Arial", 30, "bold"),
                 bg=COLORS["sidebar"], fg="#4169E1").pack(pady=(0, 6))
        tk.Label(cf, text="Κτηνιατρικό Σύστημα Διαχείρισης",
                 font=("Arial", 10), bg=COLORS["sidebar"], fg="#555").pack(pady=(0, 24))

        for lbl, attr, show in [
            ("Όνομα Χρήστη:", "username_entry", ""),
            ("Κωδικός:",      "password_entry", "*"),
        ]:
            tk.Label(cf, text=lbl, font=("Arial", 11),
                     bg=COLORS["sidebar"], anchor="w").pack(anchor="w", padx=30)
            e = tk.Entry(cf, font=("Arial", 11), width=28, show=show)
            e.pack(padx=30, pady=(0, 12))
            setattr(self, attr, e)

        self.password_entry.bind("<Return>", lambda e: self._login())

        tk.Button(cf, text="Σύνδεση", command=self._login,
                  bg=COLORS["btn_blue"], fg="white",
                  font=("Arial", 12, "bold"), width=24,
                  bd=0, pady=8, cursor="hand2").pack(pady=6)

        tk.Button(cf, text="Εγγραφή Νέου Χρήστη", command=self._open_register,
                  bg=COLORS["btn_green"], fg="white",
                  font=("Arial", 11, "bold"), width=24,
                  bd=0, pady=6, cursor="hand2").pack(pady=4)

        tk.Button(cf, text="Διαγραφή Λογαριασμού",
                  command=self._open_delete,
                  bg=COLORS["sidebar"], fg="#CC0000",
                  font=("Arial", 9, "underline"), bd=0,
                  cursor="hand2").pack(pady=(10, 0))

        tk.Label(cf, text="Demo: vet1/1234 | rec1/1234 | owner1/1234",
                 font=("Arial", 8), bg=COLORS["sidebar"], fg="#666").pack(pady=(14, 0))

    def _login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showwarning("Ελλιπή Στοιχεία", "Συμπληρώστε όνομα χρήστη και κωδικό.")
            return
        try:
            conn = get_connection()
            user = conn.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, password)
            ).fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror("Σφάλμα ΒΔ", str(e))
            return

        if not user:
            messagebox.showerror("Σφάλμα", "Λάθος στοιχεία σύνδεσης.")
            return

        self.root.withdraw()
        new_win = tk.Toplevel(self.root)
        new_win.protocol("WM_DELETE_WINDOW", self.root.destroy)

        role = user["role"]
        uid  = user["id"]

        if role == "Κτηνίατρος":
            from screens.vet_screen import VetScreen
            VetScreen(new_win, uid)
        elif role == "Ρεσεψιόν":
            from screens.reception_screen import ReceptionScreen
            ReceptionScreen(new_win, uid)
        elif role == "Ιδιοκτήτης Κατοικίδιου":
            from screens.owner_screen import OwnerScreen
            OwnerScreen(new_win, uid)
        else:
            messagebox.showerror("Σφάλμα", f"Άγνωστος ρόλος: {role}")
            self.root.deiconify()

    def _open_register(self):
        w = tk.Toplevel(self.root)
        from screens.register_screen import RegisterScreen
        RegisterScreen(w)

    def _open_delete(self):
        w = tk.Toplevel(self.root)
        from screens.delete_screen import DeleteScreen
        DeleteScreen(w)
