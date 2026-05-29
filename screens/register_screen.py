"""VetPro - Register Screen"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_setup import get_connection
from utils.ui_helpers import COLORS

class RegisterScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("VetPro - Εγγραφή")
        self.root.geometry("440x580")
        self.root.configure(bg=COLORS["sidebar"])
        self._build()

    def _build(self):
        cf = tk.Frame(self.root, bg=COLORS["sidebar"])
        cf.pack(expand=True, fill="both", padx=30, pady=20)

        tk.Label(cf, text="🐾 Νέος Λογαριασμός", font=("Arial", 20, "bold"),
                 bg=COLORS["sidebar"], fg="#4169E1").pack(pady=(0, 16))

        fields = [
            ("Ονοματεπώνυμο:", "fullname",  ""),
            ("Email:",          "email",     ""),
            ("Κινητό:",         "phone",     ""),
            ("Όνομα Χρήστη:",  "username",  ""),
            ("Κωδικός:",        "password",  "*"),
        ]
        self.vars = {}
        for lbl, key, show in fields:
            tk.Label(cf, text=lbl, font=("Arial", 10), bg=COLORS["sidebar"], anchor="w").pack(anchor="w")
            v = tk.StringVar()
            tk.Entry(cf, textvariable=v, font=("Arial", 11), width=32, show=show).pack(pady=(0, 8))
            self.vars[key] = v

        tk.Label(cf, text="Ρόλος:", font=("Arial", 10), bg=COLORS["sidebar"], anchor="w").pack(anchor="w")
        self.role_var = tk.StringVar(value="Κτηνίατρος")
        ttk.Combobox(cf, textvariable=self.role_var, width=30, state="readonly",
                     values=["Κτηνίατρος", "Ρεσεψιόν", "Ιδιοκτήτης Κατοικίδιου"]
                     ).pack(pady=(0, 16))

        tk.Button(cf, text="Δημιουργία Λογαριασμού", command=self._register,
                  bg=COLORS["btn_blue"], fg="white", font=("Arial", 11, "bold"),
                  width=26, bd=0, pady=7, cursor="hand2").pack()

    def _register(self):
        v = {k: var.get().strip() for k, var in self.vars.items()}
        role = self.role_var.get()
        if not all([v["fullname"], v["email"], v["username"], v["password"]]):
            messagebox.showwarning("Ελλιπή", "Συμπληρώστε όλα τα υποχρεωτικά πεδία.")
            return
        try:
            conn = get_connection()
            conn.execute(
                "INSERT INTO users (fullname,email,phone,username,password,role) VALUES (?,?,?,?,?,?)",
                (v["fullname"], v["email"], v["phone"], v["username"], v["password"], role)
            )
            if role == "Ιδιοκτήτης Κατοικίδιου":
                uid = conn.execute("SELECT id FROM users WHERE username=?", (v["username"],)).fetchone()["id"]
                conn.execute("INSERT INTO owners (user_id) VALUES (?)", (uid,))
            elif role == "Κτηνίατρος":
                uid = conn.execute("SELECT id FROM users WHERE username=?", (v["username"],)).fetchone()["id"]
                conn.execute("INSERT INTO veterinarians (user_id) VALUES (?)", (uid,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Επιτυχία", "Ο λογαριασμός δημιουργήθηκε!")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Σφάλμα", str(e))
