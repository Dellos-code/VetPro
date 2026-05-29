"""
VetPro - Οθόνη Ρεσεψιόν
UC2: Καταχώρηση Πληρωμής/Χρέωσης
UC9: Κράτηση Ραντεβού
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_setup import get_connection
from utils.ui_helpers import (COLORS, make_sidebar, make_main_frame,
                               clear_frame, rounded_box, section_title)

class ReceptionScreen:
    def __init__(self, root, rec_id):
        self.root = root
        self.rec_id = rec_id
        self.root.title("VetPro - Ρεσεψιόν")
        self.root.geometry("1000x620")
        self.root.configure(bg=COLORS["bg_main"])

        sidebar_btns = [
            ("🏠 Αρχική",             self.show_home),
            ("📅 Κράτηση Ραντεβού",   self.show_appointments),
            ("💳 Πληρωμές",           self.show_payments),
            ("🔔 Ειδοποιήσεις",       self.show_notifications),
        ]
        self.sidebar = make_sidebar(self.root, sidebar_btns)
        self.main = make_main_frame(self.root)
        self.show_home()

    # ── HOME ──────────────────────────────────────────────────────────────────
    def show_home(self):
        clear_frame(self.main)
        today = date.today().isoformat()
        conn = get_connection()
        apt_count = conn.execute(
            "SELECT COUNT(*) FROM appointments WHERE appt_date=? AND status='Scheduled'", (today,)
        ).fetchone()[0]
        pay_count = conn.execute(
            "SELECT COUNT(*) FROM appointments WHERE status='Scheduled'"
        ).fetchone()[0]
        notif_count = conn.execute(
            "SELECT COUNT(*) FROM reminders WHERE status='Pending'"
        ).fetchone()[0]
        conn.close()

        tk.Label(self.main, text="Καλώς ήρθατε στο VetPro 🐶",
                 font=("Arial", 16, "bold"), bg=COLORS["bg_main"]).pack(anchor="w", padx=20, pady=(20, 4))
        tk.Label(self.main, text=f"Σήμερα: {today}",
                 font=("Arial", 10), bg=COLORS["bg_main"], fg="#555").pack(anchor="w", padx=20)

        box_frame = tk.Frame(self.main, bg=COLORS["bg_main"])
        box_frame.pack(pady=30, padx=20, anchor="w")
        rounded_box(box_frame, 0,   0, 160, 90, "#9ACD32", "Ραντεβού\nσήμερα",     apt_count, "#0000FF", self.show_appointments)
        rounded_box(box_frame, 180, 0, 160, 90, "#6495ED", "Εκκρεμείς\nΠληρωμές",  pay_count, "#0000FF", self.show_payments)
        rounded_box(box_frame, 360, 0, 160, 90, "#DC143C", "Ειδοποιήσεις\nπρος Αποστολή", notif_count, "white", self.show_notifications)

    # ── UC9: ΚΡΑΤΗΣΗ ΡΑΝΤΕΒΟΥ ─────────────────────────────────────────────────
    def show_appointments(self):
        clear_frame(self.main)
        section_title(self.main, "📅 Κράτηση & Διαχείριση Ραντεβού")

        conn = get_connection()
        animals = conn.execute("SELECT id, name FROM animals ORDER BY name").fetchall()
        vets = conn.execute("SELECT id, fullname FROM users WHERE role='Κτηνίατρος' ORDER BY fullname").fetchall()
        today_apts = conn.execute("""
            SELECT a.id, a.appt_date, a.time, a.reason, a.status, a.priority,
                   an.name as animal_name, u.fullname as vet_name
            FROM appointments a
            JOIN animals an ON a.animal_id = an.id
            LEFT JOIN users u ON a.vet_id = u.id
            WHERE a.appt_date >= ?
            ORDER BY a.appt_date, a.time
            LIMIT 20
        """, (date.today().isoformat(),)).fetchall()
        conn.close()

        # Today's appointments list
        lf = tk.LabelFrame(self.main, text="Επερχόμενα Ραντεβού",
                            font=("Arial", 10, "bold"), bg=COLORS["bg_main"])
        lf.pack(fill="x", padx=16, pady=6)
        if not today_apts:
            tk.Label(lf, text="Δεν υπάρχουν ραντεβού.", font=("Arial", 10),
                     bg=COLORS["bg_main"], fg="gray").pack(padx=8, pady=4)
        for apt in today_apts:
            row = tk.Frame(lf, bg="white", bd=1, relief="solid")
            row.pack(fill="x", padx=4, pady=2)
            prio_sym = "🚨" if apt["priority"] >= 5 else "📌"
            tk.Label(row, text=f"{prio_sym} [{apt['appt_date']} {apt['time']}] "
                               f"{apt['animal_name']} | {apt['reason']} | {apt['vet_name'] or 'Αδιάθετος'} | {apt['status']}",
                     font=("Arial", 9), bg="white").pack(side="left", padx=8, pady=4)
            if apt["status"] == "Scheduled":
                tk.Button(row, text="✅ Ολοκλήρωση", bg=COLORS["btn_green"], fg="white",
                          font=("Arial", 8), bd=0, cursor="hand2",
                          command=lambda aid=apt["id"]: self._complete_apt(aid)
                          ).pack(side="right", padx=4, pady=2)

        # New appointment form
        nf = tk.LabelFrame(self.main, text="Νέο Ραντεβού",
                            font=("Arial", 10, "bold"), bg=COLORS["bg_main"])
        nf.pack(fill="x", padx=16, pady=6)

        r1 = tk.Frame(nf, bg=COLORS["bg_main"]); r1.pack(anchor="w", padx=8, pady=4)
        tk.Label(r1, text="Ζώο:", font=("Arial", 10), bg=COLORS["bg_main"]).pack(side="left")
        animal_var = tk.StringVar()
        animal_map = {f"{a['name']} (#{a['id']})": a["id"] for a in animals}
        ttk.Combobox(r1, textvariable=animal_var, values=list(animal_map.keys()),
                     state="readonly", width=20, font=("Arial", 10)).pack(side="left", padx=4)
        tk.Label(r1, text="Κτηνίατρος:", font=("Arial", 10), bg=COLORS["bg_main"]).pack(side="left", padx=(10,0))
        vet_var = tk.StringVar()
        vet_map = {v["fullname"]: v["id"] for v in vets}
        ttk.Combobox(r1, textvariable=vet_var, values=list(vet_map.keys()),
                     state="readonly", width=18, font=("Arial", 10)).pack(side="left", padx=4)

        r2 = tk.Frame(nf, bg=COLORS["bg_main"]); r2.pack(anchor="w", padx=8, pady=4)
        tk.Label(r2, text="Ημερομηνία:", font=("Arial", 10), bg=COLORS["bg_main"]).pack(side="left")
        date_var = tk.StringVar(value=date.today().isoformat())
        tk.Entry(r2, textvariable=date_var, font=("Arial", 10), width=12).pack(side="left", padx=4)
        tk.Label(r2, text="Ώρα:", font=("Arial", 10), bg=COLORS["bg_main"]).pack(side="left", padx=(10, 0))
        time_var = tk.StringVar(value="10:00")
        tk.Entry(r2, textvariable=time_var, font=("Arial", 10), width=8).pack(side="left", padx=4)
        tk.Label(r2, text="Λόγος:", font=("Arial", 10), bg=COLORS["bg_main"]).pack(side="left", padx=(10, 0))
        reason_var = tk.StringVar()
        tk.Entry(r2, textvariable=reason_var, font=("Arial", 10), width=20).pack(side="left", padx=4)

        r3 = tk.Frame(nf, bg=COLORS["bg_main"]); r3.pack(anchor="w", padx=8, pady=4)
        tk.Label(r3, text="Επείγον:", font=("Arial", 10), bg=COLORS["bg_main"]).pack(side="left")
        urgent_var = tk.BooleanVar()
        tk.Checkbutton(r3, text="Ναι (Priority 5)", variable=urgent_var,
                       bg=COLORS["bg_main"], font=("Arial", 10)).pack(side="left", padx=4)

        def book():
            key = animal_var.get()
            vkey = vet_var.get()
            d = date_var.get().strip()
            t = time_var.get().strip()
            reason = reason_var.get().strip()
            if not key or not d or not t or not reason:
                messagebox.showwarning("Ελλιπή", "Συμπληρώστε ζώο, ημερομηνία, ώρα και λόγο.")
                return

            aid = animal_map[key]
            vid = vet_map.get(vkey)
            priority = 5 if urgent_var.get() else 1

            conn = get_connection()
            # UC9: Check availability - conflict detection
            conflict = conn.execute(
                "SELECT id FROM appointments WHERE vet_id=? AND appt_date=? AND time=? AND status='Scheduled'",
                (vid, d, t)
            ).fetchone()

            if conflict and priority < 5:
                conn.close()
                messagebox.showerror("⚠️ Σύγκρουση Ωρών",
                    "Ο κτηνίατρος έχει ήδη ραντεβού αυτή την ώρα.\nΕπιλέξτε διαφορετική ώρα.")
                return

            if conflict and priority == 5:
                # Preemption for urgent
                conn.execute("UPDATE appointments SET status='Rescheduled' WHERE id=?", (conflict["id"],))
                messagebox.showwarning("🚨 Επείγον",
                    "Ένα υπάρχον ραντεβού αναβλήθηκε λόγω επείγοντος περιστατικού.")

            conn.execute(
                "INSERT INTO appointments (appt_date,time,reason,status,priority,animal_id,vet_id) VALUES (?,?,?,?,?,?,?)",
                (d, t, reason, "Scheduled", priority, aid, vid)
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Επιτυχία", f"Ραντεβού κλεισμένο για {d} {t}!")
            self.show_appointments()

        tk.Button(nf, text="✔ Κλείσιμο Ραντεβού", command=book,
                  bg=COLORS["btn_green"], fg="white", font=("Arial", 10, "bold"),
                  bd=0, pady=6, cursor="hand2").pack(anchor="w", padx=8, pady=6)

    def _complete_apt(self, apt_id):
        conn = get_connection()
        conn.execute("UPDATE appointments SET status='Completed' WHERE id=?", (apt_id,))
        conn.commit()
        conn.close()
        self.show_appointments()

    # ── UC2: ΠΛΗΡΩΜΕΣ ─────────────────────────────────────────────────────────
    def show_payments(self):
        clear_frame(self.main)
        section_title(self.main, "💳 Καταχώρηση Πληρωμής / Χρέωσης")

        conn = get_connection()
        pending = conn.execute("""
            SELECT a.id, a.appt_date, a.reason,
                   an.name as animal_name,
                   u.fullname as owner_name, u.id as owner_id,
                   o.debt_amount
            FROM appointments a
            JOIN animals an ON a.animal_id = an.id
            JOIN users u ON an.owner_id = u.id
            LEFT JOIN owners o ON o.user_id = u.id
            WHERE a.status IN ('Scheduled','Completed')
            ORDER BY a.appt_date DESC
        """).fetchall()
        conn.close()

        lf = tk.LabelFrame(self.main, text="Εκκρεμείς Πληρωμές",
                            font=("Arial", 10, "bold"), bg=COLORS["bg_main"])
        lf.pack(fill="both", expand=True, padx=16, pady=6)

        if not pending:
            tk.Label(lf, text="✅ Δεν υπάρχουν εκκρεμείς πληρωμές!",
                     font=("Arial", 11), bg=COLORS["bg_main"], fg="green").pack(pady=10)
            return

        sb = tk.Scrollbar(lf); sb.pack(side="right", fill="y")
        canvas = tk.Canvas(lf, bg=COLORS["bg_main"], yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.config(command=canvas.yview)
        inner = tk.Frame(canvas, bg=COLORS["bg_main"])
        canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        for apt in pending:
            row = tk.Frame(inner, bg="white", bd=1, relief="solid")
            row.pack(fill="x", padx=4, pady=3)
            debt = apt["debt_amount"] or 0.0
            debt_str = f" | Χρέος: €{debt:.2f}" if debt > 0 else ""
            tk.Label(row,
                     text=f"🐾 {apt['animal_name']} | {apt['owner_name']} | {apt['appt_date']} | {apt['reason']}{debt_str}",
                     font=("Arial", 10), bg="white").pack(side="left", padx=8, pady=6)
            tk.Button(row, text="💳 Πληρωμή", bg=COLORS["btn_green"], fg="white",
                      font=("Arial", 9, "bold"), bd=0, cursor="hand2",
                      command=lambda a=apt: self._open_payment_window(a)
                      ).pack(side="right", padx=8, pady=4)

    def _open_payment_window(self, apt):
        win = tk.Toplevel(self.root)
        win.title(f"Πληρωμή - {apt['animal_name']}")
        win.geometry("400x360")
        win.configure(bg="#f8f9fa")

        tk.Label(win, text=f"Πελάτης: {apt['owner_name']}",
                 font=("Arial", 14, "bold"), bg="#f8f9fa").pack(pady=(16, 4))
        tk.Label(win, text=f"Ζώο: {apt['animal_name']} | {apt['reason']}",
                 font=("Arial", 11), bg="#f8f9fa", fg="#555").pack()

        conn = get_connection()
        prev_debt = conn.execute(
            "SELECT debt_amount FROM owners WHERE user_id=?", (apt["owner_id"],)
        ).fetchone()
        conn.close()
        debt = prev_debt["debt_amount"] if prev_debt else 0.0

        # Simulated charges (in a real system, linked to medical records)
        total_label = tk.Label(win, text="Συνολικό Ποσό Χρέωσης (€):",
                                font=("Arial", 11), bg="#f8f9fa")
        total_label.pack(pady=(14, 2))
        total_var = tk.StringVar(value="50.00")
        tk.Entry(win, textvariable=total_var, font=("Arial", 12),
                 width=14, justify="center").pack()

        if debt > 0:
            tk.Label(win, text=f"⚠️ Υπάρχον χρέος ιδιοκτήτη: €{debt:.2f}",
                     font=("Arial", 10), bg="#f8f9fa", fg="red").pack(pady=4)

        tk.Label(win, text="Ποσό που καταβλήθηκε (€):",
                 font=("Arial", 11), bg="#f8f9fa").pack(pady=(10, 2))
        amount_var = tk.StringVar()
        tk.Entry(win, textvariable=amount_var, font=("Arial", 12),
                 width=14, justify="center").pack()

        def confirm(method):
            try:
                total = float(total_var.get())
                given = float(amount_var.get())
            except ValueError:
                messagebox.showerror("Σφάλμα", "Εισάγετε έγκυρα ποσά.")
                return

            if method == "card_fail":
                messagebox.showerror("❌ Απόρριψη POS",
                    "Η συναλλαγή απορρίφθηκε (Ανεπαρκές υπόλοιπο).\nΖητήστε εναλλακτικό τρόπο πληρωμής.")
                return

            today = date.today().isoformat()
            conn = get_connection()
            new_debt = max(0.0, total - given)

            if new_debt > 0:
                status = "Partial"
                conn.execute(
                    "UPDATE owners SET debt_amount = debt_amount + ? WHERE user_id=?",
                    (new_debt, apt["owner_id"])
                )
            else:
                status = "Paid"

            conn.execute(
                "INSERT INTO payments (amount,method,pay_date,status,appointment_id,owner_id) VALUES (?,?,?,?,?,?)",
                (given, method, today, status, apt["id"], apt["owner_id"])
            )
            conn.execute("UPDATE appointments SET status='Completed' WHERE id=?", (apt["id"],))
            conn.commit()
            conn.close()

            msg = f"✅ Πληρωμή ολοκληρώθηκε ({method})!\nΠοσό: €{given:.2f}"
            if new_debt > 0:
                msg += f"\n⚠️ Υπόλοιπο χρέος: €{new_debt:.2f} στην καρτέλα ιδιοκτήτη."
            messagebox.showinfo("Ολοκλήρωση", msg)
            win.destroy()
            self.show_payments()

        btn_f = tk.Frame(win, bg="#f8f9fa"); btn_f.pack(pady=16)
        tk.Button(btn_f, text="💵 Μετρητά", command=lambda: confirm("Μετρητά"),
                  bg=COLORS["btn_green"], fg="white", font=("Arial", 10, "bold"),
                  width=12, bd=0, pady=6, cursor="hand2").grid(row=0, column=0, padx=4)
        tk.Button(btn_f, text="💳 Κάρτα", command=lambda: confirm("Κάρτα"),
                  bg=COLORS["btn_blue"], fg="white", font=("Arial", 10, "bold"),
                  width=12, bd=0, pady=6, cursor="hand2").grid(row=0, column=1, padx=4)
        tk.Button(win, text="🔴 Δοκιμή: Απόρριψη Κάρτας", command=lambda: confirm("card_fail"),
                  bg="#ffc107", fg="black", font=("Arial", 9), bd=0,
                  cursor="hand2").pack(pady=4)

    # ── ΕΙΔΟΠΟΙΗΣΕΙΣ (UC8 simplified) ─────────────────────────────────────────
    def show_notifications(self):
        clear_frame(self.main)
        section_title(self.main, "🔔 Ειδοποιήσεις")

        conn = get_connection()
        reminders = conn.execute("""
            SELECT r.id, r.send_date, r.reminder_type, r.message, r.status,
                   u.fullname as owner_name, a.name as animal_name
            FROM reminders r
            LEFT JOIN users u ON r.owner_id = u.id
            LEFT JOIN animals a ON r.animal_id = a.id
            ORDER BY r.send_date DESC
            LIMIT 30
        """).fetchall()
        conn.close()

        lf = tk.Frame(self.main, bg=COLORS["bg_main"])
        lf.pack(fill="both", expand=True, padx=16, pady=6)

        if not reminders:
            tk.Label(lf, text="Δεν υπάρχουν ειδοποιήσεις.",
                     font=("Arial", 11), bg=COLORS["bg_main"], fg="gray").pack(pady=10)
        for r in reminders:
            row = tk.Frame(lf, bg="white", bd=1, relief="solid")
            row.pack(fill="x", pady=2)
            status_color = "green" if r["status"] == "Sent" else ("red" if r["status"] == "Failed" else "orange")
            tk.Label(row,
                     text=f"[{r['send_date']}] {r['reminder_type']} | {r['animal_name']} → {r['owner_name']} | {r['message'][:50]}",
                     font=("Arial", 9), bg="white").pack(side="left", padx=8, pady=4)
            tk.Label(row, text=r["status"], font=("Arial", 9, "bold"),
                     bg="white", fg=status_color).pack(side="right", padx=8)

        # Quick add reminder
        nf = tk.LabelFrame(self.main, text="Νέα Ειδοποίηση",
                            font=("Arial", 10, "bold"), bg=COLORS["bg_main"])
        nf.pack(fill="x", padx=16, pady=6)
        conn = get_connection()
        owners = conn.execute("SELECT id, fullname FROM users WHERE role='Ιδιοκτήτης Κατοικίδιου'").fetchall()
        animals = conn.execute("SELECT id, name FROM animals").fetchall()
        conn.close()

        r1 = tk.Frame(nf, bg=COLORS["bg_main"]); r1.pack(anchor="w", padx=8, pady=4)
        tk.Label(r1, text="Ιδιοκτήτης:", font=("Arial", 10), bg=COLORS["bg_main"]).pack(side="left")
        owner_var = tk.StringVar()
        owner_map = {o["fullname"]: o["id"] for o in owners}
        ttk.Combobox(r1, textvariable=owner_var, values=list(owner_map.keys()),
                     state="readonly", width=18, font=("Arial", 10)).pack(side="left", padx=4)
        tk.Label(r1, text="Ζώο:", font=("Arial", 10), bg=COLORS["bg_main"]).pack(side="left", padx=(8, 0))
        animal_var = tk.StringVar()
        animal_map = {a["name"]: a["id"] for a in animals}
        ttk.Combobox(r1, textvariable=animal_var, values=list(animal_map.keys()),
                     state="readonly", width=14, font=("Arial", 10)).pack(side="left", padx=4)

        r2 = tk.Frame(nf, bg=COLORS["bg_main"]); r2.pack(anchor="w", padx=8, pady=4)
        tk.Label(r2, text="Μήνυμα:", font=("Arial", 10), bg=COLORS["bg_main"]).pack(side="left")
        msg_var = tk.StringVar()
        tk.Entry(r2, textvariable=msg_var, font=("Arial", 10), width=36).pack(side="left", padx=4)
        type_var = tk.StringVar(value="Ραντεβού")
        ttk.Combobox(r2, textvariable=type_var,
                     values=["Ραντεβού", "Εμβόλιο", "Φάρμακο", "Γενική"],
                     state="readonly", width=12, font=("Arial", 10)).pack(side="left", padx=4)

        def send_notif():
            okey = owner_var.get()
            akey = animal_var.get()
            msg = msg_var.get().strip()
            if not okey or not msg:
                messagebox.showwarning("Ελλιπή", "Επιλέξτε ιδιοκτήτη και γράψτε μήνυμα.")
                return
            conn = get_connection()
            conn.execute(
                "INSERT INTO reminders (send_date,reminder_type,message,status,owner_id,animal_id) VALUES (?,?,?,?,?,?)",
                (date.today().isoformat(), type_var.get(), msg, "Sent",
                 owner_map[okey], animal_map.get(akey))
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Επιτυχία", "Η ειδοποίηση στάλθηκε!")
            self.show_notifications()

        tk.Button(nf, text="📤 Αποστολή", command=send_notif,
                  bg=COLORS["btn_blue"], fg="white", font=("Arial", 10, "bold"),
                  bd=0, pady=6, cursor="hand2").pack(anchor="w", padx=8, pady=6)
