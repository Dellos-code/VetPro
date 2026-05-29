"""
VetPro - Οθόνη Ιδιοκτήτη
UC7: Προβολή Προφίλ Ιδιοκτήτη
UC8: Προβολή Ειδοποιήσεων
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_setup import get_connection
from utils.ui_helpers import (COLORS, make_sidebar, make_main_frame,
                               clear_frame, rounded_box, section_title)

class OwnerScreen:
    def __init__(self, root, owner_id):
        self.root = root
        self.owner_id = owner_id
        self.root.title("VetPro - Ιδιοκτήτης")
        self.root.geometry("900x580")
        self.root.configure(bg=COLORS["bg_main"])

        conn = get_connection()
        row = conn.execute("SELECT fullname FROM users WHERE id=?", (owner_id,)).fetchone()
        conn.close()
        self.owner_name = row["fullname"] if row else "Ιδιοκτήτης"

        sidebar_btns = [
            ("🏠 Αρχική",         self.show_home),
            ("👤 Το Προφίλ μου",  self.show_profile),
            ("📅 Ραντεβού",       self.show_appointments),
            ("🔔 Ειδοποιήσεις",   self.show_notifications),
            ("🐾 Ιστορικό Ζώου",  self.show_animal_history),
        ]
        self.sidebar = make_sidebar(self.root, sidebar_btns)
        self.main = make_main_frame(self.root)
        self.show_home()

    # ── HOME ──────────────────────────────────────────────────────────────────
    def show_home(self):
        clear_frame(self.main)
        conn = get_connection()
        pets = conn.execute("SELECT id, name, species FROM animals WHERE owner_id=?",
                            (self.owner_id,)).fetchall()
        notif_count = conn.execute(
            "SELECT COUNT(*) FROM reminders WHERE owner_id=? AND status='Sent'",
            (self.owner_id,)
        ).fetchone()[0]
        next_apt = conn.execute("""
            SELECT a.appt_date, a.time, a.reason, an.name as animal_name
            FROM appointments a JOIN animals an ON a.animal_id=an.id
            WHERE an.owner_id=? AND a.status='Scheduled' AND a.appt_date >= ?
            ORDER BY a.appt_date LIMIT 1
        """, (self.owner_id, date.today().isoformat())).fetchone()
        next_vax = conn.execute("""
            SELECT v.next_due_date, v.vaccine_name, an.name as animal_name
            FROM vaccinations v
            JOIN medical_records mr ON v.record_id=mr.id
            JOIN animals an ON mr.animal_id=an.id
            WHERE an.owner_id=? AND v.next_due_date >= ?
            ORDER BY v.next_due_date LIMIT 1
        """, (self.owner_id, date.today().isoformat())).fetchone()
        conn.close()

        tk.Label(self.main, text=f"Γεια σου, {self.owner_name}!",
                 font=("Arial", 16, "bold"), bg=COLORS["bg_main"]).pack(anchor="w", padx=20, pady=(20, 4))

        box_frame = tk.Frame(self.main, bg=COLORS["bg_main"])
        box_frame.pack(pady=20, padx=20, anchor="w")

        pet_names = ", ".join(p["name"] for p in pets) if pets else "—"
        rounded_box(box_frame, 0,   0, 200, 100, "#87CEEB",  "Τα Κατοικίδιά μου", pet_names, "#4169E1", self.show_profile)

        apt_text = f"{next_apt['appt_date']}\n{next_apt['animal_name']}" if next_apt else "—"
        rounded_box(box_frame, 220, 0, 200, 100, "#9ACD32",  "Επόμενο Ραντεβού",  apt_text, "#006400", self.show_appointments)

        vax_text = f"{next_vax['next_due_date']}\n{next_vax['vaccine_name']}" if next_vax else "—"
        rounded_box(box_frame, 440, 0, 200, 100, "#FFD700",  "Επόμενο Εμβόλιο",   vax_text, "#8B6914", self.show_animal_history)

        rounded_box(box_frame, 660, 0, 160, 100, "#DC143C",  "Ειδοποιήσεις",       notif_count, "white", self.show_notifications)

    # ── UC7: ΠΡΟΦΙΛ ΙΔΙΟΚΤΗΤΗ ─────────────────────────────────────────────────
    def show_profile(self):
        clear_frame(self.main)
        section_title(self.main, "👤 Το Προφίλ μου")

        conn = get_connection()
        user = conn.execute("SELECT * FROM users WHERE id=?", (self.owner_id,)).fetchone()
        owner = conn.execute("SELECT * FROM owners WHERE user_id=?", (self.owner_id,)).fetchone()
        pets = conn.execute("SELECT * FROM animals WHERE owner_id=?", (self.owner_id,)).fetchall()
        conn.close()

        if not user:
            tk.Label(self.main, text="⚠️ Αδυναμία φόρτωσης στοιχείων.",
                     font=("Arial", 11), bg=COLORS["bg_main"], fg="red").pack(pady=10)
            return

        # Personal info
        info_frame = tk.LabelFrame(self.main, text="Προσωπικά Στοιχεία",
                                    font=("Arial", 10, "bold"), bg=COLORS["bg_main"])
        info_frame.pack(fill="x", padx=16, pady=6)
        fields = [
            ("Ονοματεπώνυμο:", user["fullname"]),
            ("Email:",          user["email"]),
            ("Τηλέφωνο:",       user["phone"] or "—"),
            ("Διεύθυνση:",      owner["address"] if owner else "—"),
            ("Υπόλοιπο χρέους:", f"€{owner['debt_amount']:.2f}" if owner else "€0.00"),
        ]
        for lbl, val in fields:
            row = tk.Frame(info_frame, bg=COLORS["bg_main"])
            row.pack(anchor="w", padx=12, pady=2)
            tk.Label(row, text=lbl, font=("Arial", 10, "bold"), bg=COLORS["bg_main"],
                     width=20, anchor="w").pack(side="left")
            tk.Label(row, text=val, font=("Arial", 10), bg=COLORS["bg_main"]).pack(side="left")

        # Pets
        if not pets:
            tk.Label(self.main, text="ℹ️ Δεν υπάρχουν καταχωρημένα ζώα. Επικοινωνήστε με τη ρεσεψιόν.",
                     font=("Arial", 10), bg=COLORS["bg_main"], fg="#555").pack(padx=16, pady=8, anchor="w")
            return

        pf = tk.LabelFrame(self.main, text="Τα Κατοικίδιά μου",
                            font=("Arial", 10, "bold"), bg=COLORS["bg_main"])
        pf.pack(fill="x", padx=16, pady=6)
        for pet in pets:
            row = tk.Frame(pf, bg="white", bd=1, relief="solid")
            row.pack(fill="x", padx=4, pady=2)
            tk.Label(row, text=f"🐾 {pet['name']} | {pet['species']} | {pet['breed']} | {pet['age']} ετών | {pet['weight']}kg",
                     font=("Arial", 10), bg="white").pack(side="left", padx=8, pady=6)
            tk.Button(row, text="📋 Ιστορικό", bg=COLORS["btn_blue"], fg="white",
                      font=("Arial", 9), bd=0, cursor="hand2",
                      command=lambda pid=pet["id"]: self._show_pet_history(pid)
                      ).pack(side="right", padx=8, pady=4)

    def _show_pet_history(self, animal_id):
        conn = get_connection()
        # Access check: animal must belong to this owner
        animal = conn.execute("SELECT * FROM animals WHERE id=? AND owner_id=?",
                              (animal_id, self.owner_id)).fetchone()
        if not animal:
            conn.close()
            messagebox.showerror("Πρόσβαση Απαγορευμένη", "Δεν έχετε πρόσβαση σε αυτό το ζώο.")
            return

        records = conn.execute("""
            SELECT mr.record_date, mr.record_type, mr.notes,
                   e.diagnosis, v.vaccine_name
            FROM medical_records mr
            LEFT JOIN examinations e ON e.record_id = mr.id
            LEFT JOIN vaccinations v ON v.record_id = mr.id
            WHERE mr.animal_id=?
            ORDER BY mr.record_date DESC
        """, (animal_id,)).fetchall()
        conn.close()

        win = tk.Toplevel(self.root)
        win.title(f"Ιστορικό: {animal['name']}")
        win.geometry("480x400")
        win.configure(bg="#f5f5f5")
        tk.Label(win, text=f"🐾 Ιστορικό: {animal['name']}",
                 font=("Arial", 14, "bold"), bg="#f5f5f5").pack(pady=12)

        sb = tk.Scrollbar(win); sb.pack(side="right", fill="y")
        lb = tk.Listbox(win, font=("Arial", 10), yscrollcommand=sb.set, height=14)
        lb.pack(fill="both", expand=True, padx=10)
        sb.config(command=lb.yview)

        if not records:
            lb.insert(tk.END, "📭 Δεν υπάρχουν εγγραφές.")
        for r in records:
            detail = r["diagnosis"] or r["vaccine_name"] or r["notes"] or ""
            lb.insert(tk.END, f"[{r['record_date']}] {r['record_type']}: {detail}")

        tk.Button(win, text="Κλείσιμο", command=win.destroy,
                  bg=COLORS["btn_gray"], fg="white", font=("Arial", 10, "bold"),
                  bd=0, pady=6, cursor="hand2").pack(pady=10)

    # ── ΡΑΝΤΕΒΟΥ (read-only view for owner) ──────────────────────────────────
    def show_appointments(self):
        clear_frame(self.main)
        section_title(self.main, "📅 Τα Ραντεβού μου")

        conn = get_connection()
        apts = conn.execute("""
            SELECT a.appt_date, a.time, a.reason, a.status,
                   an.name as animal_name, u.fullname as vet_name
            FROM appointments a
            JOIN animals an ON a.animal_id=an.id
            LEFT JOIN users u ON a.vet_id=u.id
            WHERE an.owner_id=?
            ORDER BY a.appt_date DESC
        """, (self.owner_id,)).fetchall()
        conn.close()

        lf = tk.Frame(self.main, bg=COLORS["bg_main"])
        lf.pack(fill="both", expand=True, padx=16, pady=6)
        if not apts:
            tk.Label(lf, text="Δεν υπάρχουν ραντεβού.", font=("Arial", 11),
                     bg=COLORS["bg_main"], fg="gray").pack(pady=10)
        for apt in apts:
            row = tk.Frame(lf, bg="white", bd=1, relief="solid")
            row.pack(fill="x", pady=2)
            status_sym = "✅" if apt["status"] == "Completed" else ("⏳" if apt["status"] == "Scheduled" else "❌")
            tk.Label(row,
                     text=f"{status_sym} [{apt['appt_date']} {apt['time']}] {apt['animal_name']} | {apt['reason']} | Κτηνίατρος: {apt['vet_name'] or '—'}",
                     font=("Arial", 10), bg="white").pack(anchor="w", padx=8, pady=5)

    # ── UC8: ΕΙΔΟΠΟΙΗΣΕΙΣ ─────────────────────────────────────────────────────
    def show_notifications(self):
        clear_frame(self.main)
        section_title(self.main, "🔔 Ειδοποιήσεις")

        conn = get_connection()
        notifs = conn.execute("""
            SELECT r.id, r.send_date, r.reminder_type, r.message, r.status,
                   a.name as animal_name
            FROM reminders r
            LEFT JOIN animals a ON r.animal_id=a.id
            WHERE r.owner_id=?
            ORDER BY r.send_date DESC
        """, (self.owner_id,)).fetchall()

        pref = conn.execute(
            "SELECT notifications_enabled FROM users WHERE id=?", (self.owner_id,)
        ).fetchone()
        notif_enabled = bool(pref["notifications_enabled"]) if pref else True
        conn.close()

        # Preferences toggle
        pf = tk.Frame(self.main, bg=COLORS["bg_main"])
        pf.pack(anchor="w", padx=16, pady=4)
        notif_var = tk.BooleanVar(value=notif_enabled)

        def toggle_notif():
            conn = get_connection()
            conn.execute("UPDATE users SET notifications_enabled=? WHERE id=?",
                         (1 if notif_var.get() else 0, self.owner_id))
            conn.commit()
            conn.close()

        tk.Checkbutton(pf, text="Ειδοποιήσεις Email/SMS ενεργές",
                        variable=notif_var, command=toggle_notif,
                        bg=COLORS["bg_main"], font=("Arial", 10)).pack(side="left")

        lf = tk.Frame(self.main, bg=COLORS["bg_main"])
        lf.pack(fill="both", expand=True, padx=16, pady=6)

        if not notifs:
            tk.Label(lf, text="Δεν υπάρχουν ειδοποιήσεις.",
                     font=("Arial", 11), bg=COLORS["bg_main"], fg="gray").pack(pady=10)
        for n in notifs:
            row = tk.Frame(lf, bg="white", bd=1, relief="solid")
            row.pack(fill="x", pady=2)
            status_color = "green" if n["status"] == "Sent" else "red"
            animal_str = f" | {n['animal_name']}" if n["animal_name"] else ""
            tk.Label(row,
                     text=f"🔔 [{n['send_date']}] {n['reminder_type']}{animal_str}: {n['message']}",
                     font=("Arial", 10), bg="white").pack(side="left", padx=8, pady=5)
            tk.Label(row, text=n["status"], font=("Arial", 9, "bold"),
                     bg="white", fg=status_color).pack(side="right", padx=8)

    # ── ΙΣΤΟΡΙΚΟ ΖΩΟΥ ─────────────────────────────────────────────────────────
    def show_animal_history(self):
        clear_frame(self.main)
        section_title(self.main, "🐾 Ιστορικό Ζώου")

        conn = get_connection()
        pets = conn.execute("SELECT id, name FROM animals WHERE owner_id=?",
                            (self.owner_id,)).fetchall()
        conn.close()

        if not pets:
            tk.Label(self.main, text="Δεν υπάρχουν καταχωρημένα ζώα.",
                     font=("Arial", 11), bg=COLORS["bg_main"], fg="gray").pack(padx=16, pady=10)
            return

        ff = tk.Frame(self.main, bg=COLORS["bg_main"])
        ff.pack(anchor="w", padx=16, pady=6)
        tk.Label(ff, text="Ζώο:", font=("Arial", 10), bg=COLORS["bg_main"]).pack(side="left")
        pet_var = tk.StringVar()
        pet_map = {p["name"]: p["id"] for p in pets}
        cb = ttk.Combobox(ff, textvariable=pet_var, values=list(pet_map.keys()),
                          state="readonly", width=20, font=("Arial", 10))
        cb.pack(side="left", padx=6)

        result_frame = tk.Frame(self.main, bg=COLORS["bg_main"])
        result_frame.pack(fill="both", expand=True, padx=16)

        def load_history(_=None):
            clear_frame(result_frame)
            key = pet_var.get()
            if not key:
                return
            aid = pet_map[key]
            conn = get_connection()
            records = conn.execute("""
                SELECT mr.record_date, mr.record_type, mr.notes,
                       e.diagnosis, v.vaccine_name, v.next_due_date
                FROM medical_records mr
                LEFT JOIN examinations e ON e.record_id=mr.id
                LEFT JOIN vaccinations v ON v.record_id=mr.id
                WHERE mr.animal_id=?
                ORDER BY mr.record_date DESC
            """, (aid,)).fetchall()
            conn.close()

            if not records:
                tk.Label(result_frame, text="Δεν υπάρχουν εγγραφές.",
                         font=("Arial", 11), bg=COLORS["bg_main"], fg="gray").pack(pady=10)
                return
            sb = tk.Scrollbar(result_frame); sb.pack(side="right", fill="y")
            lb = tk.Listbox(result_frame, font=("Arial", 10), yscrollcommand=sb.set, height=12)
            lb.pack(fill="both", expand=True)
            sb.config(command=lb.yview)
            for r in records:
                detail = r["diagnosis"] or r["vaccine_name"] or r["notes"] or ""
                extra = f" | Επόμενο: {r['next_due_date']}" if r["next_due_date"] else ""
                lb.insert(tk.END, f"[{r['record_date']}] {r['record_type']}: {detail}{extra}")

        cb.bind("<<ComboboxSelected>>", load_history)
