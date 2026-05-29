import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
import sys, os, uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_setup import get_connection
from utils.ui_helpers import (COLORS, make_sidebar, make_main_frame,
                               clear_frame, rounded_box, section_title)
from logic.vaccine_saver   import VaccineSaver, AllergyChecker, HistoryManager
from logic.admission_manager import AdmissionManager, DailyLogManager, DischargeManager
from logic.report_generator  import ReportGenerator, DrugCatalog, TempList, ResultsAnalyzer
from logic.inventory_manager import InventoryManager, ForecastEngine
from logic.appointment_service import AppointmentService

class VetScreen:
    def __init__(self, root, vet_id):
        self.root   = root
        self.vet_id = vet_id
        self.root.title("VetPro - Κτηνίατρος")
        self.root.geometry("1050x640")
        self.root.configure(bg=COLORS["bg_main"])

        conn = get_connection()
        row  = conn.execute("SELECT fullname FROM users WHERE id=?", (vet_id,)).fetchone()
        conn.close()
        self.vet_name = row["fullname"] if row else "Κτηνίατρος"

        sidebar_btns = [
            ("🏠  Αρχική",               self.show_home),
            ("🔍  Ιστορικό Ζώου",        self.show_search),
            ("💉  Εμβολιασμοί",           self.show_vaccinations),
            ("🏥  Νοσηλεία",             self.show_hospitalizations),
            ("💊  Συνταγογράφηση",        self.show_prescriptions),
            ("📊  Αναφορές",             self.show_reports),
            ("📦  Απόθεμα Φαρμάκων",     self.show_stock),
        ]
        self.sidebar = make_sidebar(self.root, sidebar_btns)
        self.main    = make_main_frame(self.root)
        self.show_home()

    # ── HOME ──────────────────────────────────────────────────────────────────
    def show_home(self):
        clear_frame(self.main)
        conn  = get_connection()
        today = date.today().isoformat()
        apt_count  = conn.execute("SELECT COUNT(*) FROM appointments WHERE appt_date=? AND status='Scheduled'",(today,)).fetchone()[0]
        hosp_count = conn.execute("SELECT COUNT(*) FROM hospitalizations WHERE status='Active'").fetchone()[0]
        conn.close()
        # ForecastEngine.triggerForecast (Class Diagram)
        low_stock_items = ForecastEngine().triggerForecast()
        low_count = len(low_stock_items)

        tk.Label(self.main, text=f"Γεια σου, {self.vet_name}!",
                 font=("Arial",18,"bold"), bg=COLORS["bg_main"]).pack(anchor="w", padx=20, pady=(20,4))
        tk.Label(self.main, text=f"Σήμερα: {today}",
                 font=("Arial",10), bg=COLORS["bg_main"], fg="#555").pack(anchor="w", padx=20)

        bf = tk.Frame(self.main, bg=COLORS["bg_main"])
        bf.pack(pady=24, padx=20, anchor="w")
        rounded_box(bf,   0, 0, 160, 90, "#9ACD32", "Ραντεβού\nσήμερα",    apt_count,  "#003300", self.show_search)
        rounded_box(bf, 180, 0, 160, 90, "#6495ED", "Ενεργές\nΝοσηλείες",  hosp_count, "#000066", self.show_hospitalizations)
        rounded_box(bf, 360, 0, 160, 90, "#DC143C", "Χαμηλό\nApόθεμα",    low_count,  "white",   self.show_stock)

        sf = tk.Frame(self.main, bg=COLORS["bg_main"]); sf.pack(anchor="w", padx=20, pady=10)
        tk.Label(sf, text="Αναζήτηση Πελάτη/Ζώου:",
                 font=("Arial",11,"bold"), bg=COLORS["bg_main"]).pack(anchor="w")
        row2 = tk.Frame(sf, bg=COLORS["bg_main"]); row2.pack(anchor="w", pady=4)
        self._qs = tk.Entry(row2, font=("Arial",11), width=30)
        self._qs.pack(side="left", padx=(0,8))
        self._qs.bind("<Return>", lambda e: self._do_quick_search())
        tk.Button(row2, text="🔍 Αναζήτηση", command=self._do_quick_search,
                  bg=COLORS["btn_blue"], fg="white", font=("Arial",10,"bold"),
                  bd=0, padx=10, pady=4, cursor="hand2").pack(side="left")

        if low_stock_items:
            af = tk.LabelFrame(self.main, text="⚠️ Φάρμακα με χαμηλό απόθεμα",
                                font=("Arial",9,"bold"), bg=COLORS["bg_main"])
            af.pack(fill="x", padx=20, pady=6)
            for m in low_stock_items:
                tk.Label(af, text=f"  • {m['name']}  (Stock: {m['stock_level']} / Όριο: {m['min_threshold']})",
                         font=("Arial",9), bg=COLORS["bg_main"], fg="red").pack(anchor="w")

    def _do_quick_search(self):
        q = self._qs.get().strip()
        if q: self.show_search(q)

    # ── UC1: Αναζήτηση / Ιστορικό Ζώου ──────────────────────────────────────
    # Uses: ResultsAnalyzer, HistoryManager (Class Diagram)
    def show_search(self, initial=""):
        clear_frame(self.main)
        section_title(self.main, "🔍 Ιστορικό Ζώου (UC1)")

        sf = tk.Frame(self.main, bg=COLORS["bg_main"]); sf.pack(anchor="w", padx=16, pady=4)
        tk.Label(sf, text="Όνομα ζώου ή τηλέφωνο ιδιοκτήτη:",
                 font=("Arial",10), bg=COLORS["bg_main"]).pack(anchor="w")
        row = tk.Frame(sf, bg=COLORS["bg_main"]); row.pack(anchor="w", pady=4)
        sv  = tk.StringVar(value=initial)
        tk.Entry(row, textvariable=sv, font=("Arial",11), width=30).pack(side="left", padx=(0,8))
        rf = tk.Frame(self.main, bg=COLORS["bg_main"])
        rf.pack(fill="both", expand=True, padx=16)

        def do_search():
            clear_frame(rf)
            q = sv.get().strip()
            if not q: return
            conn = get_connection()
            rows = conn.execute("""
                SELECT a.id, a.name, a.species, a.breed, a.age, a.weight,
                       u.fullname as owner, u.phone
                FROM animals a JOIN users u ON a.owner_id=u.id
                WHERE a.name LIKE ? OR u.phone LIKE ?
            """, (f"%{q}%", f"%{q}%")).fetchall()
            conn.close()

            # ResultsAnalyzer (Class Diagram)
            analyzer = ResultsAnalyzer()
            result   = analyzer.notifyResults(rows)

            if result["is_empty"]:
                tk.Label(rf, text="❌ Δεν βρέθηκαν αποτελέσματα.",
                         font=("Arial",11), bg=COLORS["bg_main"], fg="red").pack(pady=10)
            elif result["has_multiple"]:
                # DataEnricher: shows phone to differentiate (Class Diagram)
                tk.Label(rf, text="Βρέθηκαν πολλά αποτελέσματα - επιλέξτε:",
                         font=("Arial",10,"bold"), bg=COLORS["bg_main"]).pack(anchor="w", pady=4)
                for r in rows:
                    lbl = f"🐾 {r['name']} ({r['species']}) | Ιδιοκτ: {r['owner']} | Τηλ: {r['phone']}"
                    tk.Button(rf, text=lbl, font=("Arial",10), bg="white", anchor="w", cursor="hand2",
                              command=lambda aid=r["id"]: self._open_animal_card(aid)
                              ).pack(fill="x", pady=2)
            else:
                self._open_animal_card(rows[0]["id"])

        tk.Button(row, text="🔍 Αναζήτηση", command=do_search,
                  bg=COLORS["btn_blue"], fg="white", font=("Arial",10,"bold"),
                  bd=0, padx=10, pady=4, cursor="hand2").pack(side="left")
        if initial: do_search()

    def _open_animal_card(self, animal_id):
        conn = get_connection()
        a     = conn.execute("SELECT * FROM animals WHERE id=?", (animal_id,)).fetchone()
        owner = conn.execute("SELECT fullname, phone FROM users WHERE id=?", (a["owner_id"],)).fetchone()
        conn.close()

        # HistoryManager.retrieveHistory (Class Diagram)
        records = HistoryManager().retrieveHistory(animal_id)

        win = tk.Toplevel(self.root)
        win.title(f"Καρτέλα Ζώου - {a['name']}")
        win.geometry("540x500")
        win.configure(bg="#f5f5f5")

        tk.Label(win, text=f"🐾 {a['name']}", font=("Arial",18,"bold"), bg="#f5f5f5").pack(pady=(14,2))
        tk.Label(win, text=f"{a['species']} | {a['breed']} | {a['age']} ετών | {a['weight']} kg",
                 font=("Arial",10), bg="#f5f5f5", fg="#555").pack()
        tk.Label(win, text=f"Ιδιοκτήτης: {owner['fullname']} | Τηλ: {owner['phone']}",
                 font=("Arial",10), bg="#f5f5f5", fg="#555").pack(pady=(2,10))
        tk.Label(win, text="Ιατρικό Ιστορικό:", font=("Arial",12,"bold","underline"), bg="#f5f5f5").pack(anchor="w", padx=14)

        lf = tk.Frame(win, bg="#f5f5f5"); lf.pack(fill="both", expand=True, padx=14, pady=6)
        sb = tk.Scrollbar(lf); sb.pack(side="right", fill="y")
        lb = tk.Listbox(lf, font=("Arial",10), yscrollcommand=sb.set, height=10); lb.pack(fill="both", expand=True)
        sb.config(command=lb.yview)

        if not records:
            lb.insert(tk.END, "📭 Κενό ιστορικό / Πρώτη επίσκεψη")
        else:
            for r in records:
                detail = r.get("diagnosis") or r.get("vaccine_name") or r.get("notes") or ""
                lb.insert(tk.END, f"[{r['record_date']}] {r['record_type']}: {detail}")

        bf2 = tk.Frame(win, bg="#f5f5f5"); bf2.pack(pady=8)
        tk.Button(bf2, text="💊 Συνταγή", bg=COLORS["btn_blue"], fg="white", font=("Arial",9,"bold"),
                  command=lambda: [win.destroy(), self.show_prescriptions(animal_id)], cursor="hand2").grid(row=0,column=0,padx=4)
        tk.Button(bf2, text="💉 Εμβόλιο", bg="#28A745", fg="white", font=("Arial",9,"bold"),
                  command=lambda: [win.destroy(), self.show_vaccinations(animal_id)], cursor="hand2").grid(row=0,column=1,padx=4)
        tk.Button(bf2, text="🏥 Νοσηλεία", bg="#FF8C00", fg="white", font=("Arial",9,"bold"),
                  command=lambda: [win.destroy(), self.show_hospitalizations(animal_id)], cursor="hand2").grid(row=0,column=2,padx=4)
        tk.Button(bf2, text="Κλείσιμο", bg=COLORS["btn_gray"], fg="white", font=("Arial",9,"bold"),
                  command=win.destroy, cursor="hand2").grid(row=0,column=3,padx=4)

    # ── UC3: Εμβολιασμοί ─────────────────────────────────────────────────────
    # Uses: VaccineSaver, AllergyChecker, DoseCalculator, InventoryManager (Class Diagram)
    def show_vaccinations(self, preselect=None):
        clear_frame(self.main)
        section_title(self.main, "💉 Διαχείριση Εμβολιασμών (UC3)")

        conn    = get_connection()
        animals = conn.execute("SELECT id, name, owner_id FROM animals ORDER BY name").fetchall()
        conn.close()

        af = tk.Frame(self.main, bg=COLORS["bg_main"]); af.pack(anchor="w", padx=16, pady=4)
        tk.Label(af, text="Ζώο:", font=("Arial",10), bg=COLORS["bg_main"]).pack(side="left")
        av    = tk.StringVar()
        amap  = {f"{a['name']} (#{a['id'][:8]})": a for a in animals}
        cb    = ttk.Combobox(af, textvariable=av, values=list(amap.keys()),
                              state="readonly", width=26, font=("Arial",10))
        cb.pack(side="left", padx=6)
        if preselect:
            for k, v in amap.items():
                if v["id"] == preselect: av.set(k); break

        hist_lf = tk.LabelFrame(self.main, text="Ιστορικό Εμβολιασμών",
                                  font=("Arial",10,"bold"), bg=COLORS["bg_main"])
        hist_lf.pack(fill="x", padx=16, pady=8)
        hist_lb = tk.Listbox(hist_lf, font=("Arial",10), height=6)
        hist_lb.pack(fill="x", padx=4, pady=4)

        def load_hist(*_):
            hist_lb.delete(0, tk.END)
            key = av.get()
            if not key: return
            aid  = amap[key]["id"]
            rows = HistoryManager().getVaccinationHistory(aid)
            if not rows: hist_lb.insert(tk.END, "Δεν υπάρχουν εμβολιασμοί.")
            for r in rows:
                flag = " ⚠️ΑΛΛΕΡΓΙΑ" if r["allergy_reaction"] else ""
                hist_lb.insert(tk.END, f"[{r['record_date']}] {r['vaccine_name']} | Επόμ: {r['next_due_date']}{flag}")

        cb.bind("<<ComboboxSelected>>", load_hist)
        if preselect: load_hist()

        nf = tk.LabelFrame(self.main, text="Νέος Εμβολιασμός",
                            font=("Arial",10,"bold"), bg=COLORS["bg_main"])
        nf.pack(fill="x", padx=16, pady=4)
        r1 = tk.Frame(nf, bg=COLORS["bg_main"]); r1.pack(anchor="w", padx=8, pady=4)
        tk.Label(r1, text="Εμβόλιο:", font=("Arial",10), bg=COLORS["bg_main"]).pack(side="left")
        vv = tk.StringVar()
        conn2 = get_connection()
        vmeds = [m["name"] for m in conn2.execute("SELECT name FROM medications WHERE type='Εμβόλιο'").fetchall()]
        conn2.close()
        if not vmeds: vmeds = ["Nobivac","Eurican","Feligen"]
        ttk.Combobox(r1, textvariable=vv, values=vmeds, width=18, font=("Arial",10)).pack(side="left", padx=6)
        tk.Label(r1, text="Παρτίδα:", font=("Arial",10), bg=COLORS["bg_main"]).pack(side="left", padx=(10,0))
        bv = tk.StringVar()
        tk.Entry(r1, textvariable=bv, font=("Arial",10), width=14).pack(side="left", padx=4)

        def save_vax():
            key = av.get(); vname = vv.get().strip(); batch = bv.get().strip()
            if not key or not vname:
                messagebox.showwarning("Ελλιπή", "Επιλέξτε ζώο και εμβόλιο."); return
            a_data  = amap[key]
            aid     = a_data["id"]
            oid     = a_data["owner_id"]
            # VaccineSaver.saveVaccination (Class Diagram)
            saver  = VaccineSaver()
            result = saver.saveVaccination(aid, self.vet_id, oid, vname, batch)
            if result["status"] == "ALLERGY_WARNING":
                past = result["past_allergies"]
                info = "\n".join(f"  {p['record_date']}: {p['vaccine_name']}" for p in past)
                if messagebox.askyesno("⚠️ Προειδοποίηση Αλλεργίας",
                    f"Το ζώο είχε αλλεργική αντίδραση σε {vname}:\n{info}\n\nΣυνέχεια;"):
                    result = saver.saveVaccination(aid, self.vet_id, oid, vname, batch, allergy_override=True)
                else:
                    return
            messagebox.showinfo("Επιτυχία",
                f"Εμβολιασμός {vname} καταχωρήθηκε!\nΕπόμενη δόση: {result['next_due_date']}")
            load_hist()

        tk.Button(nf, text="✔ Καταχώρηση Εμβολιασμού", command=save_vax,
                  bg=COLORS["btn_green"], fg="white", font=("Arial",10,"bold"),
                  bd=0, pady=6, cursor="hand2").pack(anchor="w", padx=8, pady=6)

    # ── UC4: Νοσηλεία ─────────────────────────────────────────────────────────
    # Uses: AdmissionManager, DailyLogManager, DischargeManager (Class Diagram)
    def show_hospitalizations(self, preselect=None):
        clear_frame(self.main)
        section_title(self.main, "🏥 Διαχείριση Νοσηλείας (UC4)")

        conn    = get_connection()
        animals = conn.execute("SELECT id, name, owner_id FROM animals ORDER BY name").fetchall()
        active  = conn.execute("""
            SELECT h.id, a.name as aname, a.owner_id, h.admission_date, h.reason, h.status
            FROM hospitalizations h JOIN animals a ON h.animal_id=a.id
            WHERE h.status IN ('Active','Critical')
        """).fetchall()
        conn.close()

        af = tk.LabelFrame(self.main, text="Ενεργές Νοσηλείες",
                            font=("Arial",10,"bold"), bg=COLORS["bg_main"])
        af.pack(fill="x", padx=16, pady=6)
        if not active:
            tk.Label(af, text="Δεν υπάρχουν ενεργές νοσηλείες.",
                     font=("Arial",10), bg=COLORS["bg_main"], fg="green").pack(padx=8, pady=4)
        for h in active:
            row2 = tk.Frame(af, bg="white" if h["status"]!="Critical" else "#ffe0e0",
                            bd=1, relief="solid")
            row2.pack(fill="x", padx=6, pady=2)
            status_sym = "🚨" if h["status"] == "Critical" else "🏥"
            tk.Label(row2, text=f"{status_sym} {h['aname']} | Εισ: {h['admission_date']} | {h['reason']} [{h['status']}]",
                     font=("Arial",9), bg=row2["bg"]).pack(side="left", padx=8, pady=5)
            tk.Button(row2, text="📋 Ημερήσια", bg=COLORS["btn_blue"], fg="white",
                      font=("Arial",8), bd=0, cursor="hand2",
                      command=lambda hid=h["id"],hn=h["aname"],oid=h["owner_id"],anm=h["aname"]:
                              self._daily_log_win(hid, hn, oid, anm)
                      ).pack(side="right", padx=4, pady=3)
            tk.Button(row2, text="🚪 Εξιτήριο", bg="#DC143C", fg="white",
                      font=("Arial",8), bd=0, cursor="hand2",
                      command=lambda hid=h["id"],oid=h["owner_id"],anid=h["id"]:
                              self._discharge_win(hid, oid)
                      ).pack(side="right", padx=4, pady=3)

        nf = tk.LabelFrame(self.main, text="Νέα Εισαγωγή σε Νοσηλεία",
                            font=("Arial",10,"bold"), bg=COLORS["bg_main"])
        nf.pack(fill="x", padx=16, pady=6)
        r1 = tk.Frame(nf, bg=COLORS["bg_main"]); r1.pack(anchor="w", padx=8, pady=4)
        tk.Label(r1, text="Ζώο:", font=("Arial",10), bg=COLORS["bg_main"]).pack(side="left")
        av2  = tk.StringVar()
        amap2 = {f"{a['name']} (#{a['id'][:8]})": a for a in animals}
        cb2   = ttk.Combobox(r1, textvariable=av2, values=list(amap2.keys()),
                              state="readonly", width=24, font=("Arial",10))
        cb2.pack(side="left", padx=6)
        if preselect:
            for k,v in amap2.items():
                if v["id"]==preselect: av2.set(k); break
        r2 = tk.Frame(nf, bg=COLORS["bg_main"]); r2.pack(anchor="w", padx=8, pady=2)
        tk.Label(r2, text="Λόγος εισαγωγής:", font=("Arial",10), bg=COLORS["bg_main"]).pack(side="left")
        rv = tk.StringVar()
        tk.Entry(r2, textvariable=rv, font=("Arial",10), width=34).pack(side="left", padx=6)

        def admit():
            key = av2.get(); reason = rv.get().strip()
            if not key or not reason:
                messagebox.showwarning("Ελλιπή","Επιλέξτε ζώο και λόγο."); return
            a_data = amap2[key]
            # AdmissionManager.createAdmission (Class Diagram)
            mgr = AdmissionManager()
            mgr.createAdmission(a_data["id"], self.vet_id, reason)
            mgr.notifyOwner(a_data["owner_id"], a_data["id"], f"Εισαγωγή σε νοσηλεία: {reason}")
            messagebox.showinfo("Επιτυχία","Το ζώο εισήχθη σε νοσηλεία.")
            self.show_hospitalizations()

        tk.Button(nf, text="✔ Εισαγωγή σε Νοσηλεία", command=admit,
                  bg=COLORS["btn_green"], fg="white", font=("Arial",10,"bold"),
                  bd=0, pady=6, cursor="hand2").pack(anchor="w", padx=8, pady=6)

    def _daily_log_win(self, hosp_id, animal_name, owner_id, animal_id):
        win = tk.Toplevel(self.root)
        win.title(f"Ημερήσια Καταγραφή - {animal_name}")
        win.geometry("430x400")
        win.configure(bg="#f5f5f5")
        tk.Label(win, text=f"Ημερήσια Καταγραφή: {animal_name}",
                 font=("Arial",13,"bold"), bg="#f5f5f5").pack(pady=10)
        fields = [("Θερμοκρασία (°C):","temp"),("Βάρος (kg):","wt"),
                  ("Φαρμακευτική Αγωγή:","meds"),("Παρατηρήσεις:","notes")]
        vs = {}
        for lbl, key in fields:
            row2 = tk.Frame(win, bg="#f5f5f5"); row2.pack(anchor="w", padx=16, pady=3)
            tk.Label(row2, text=lbl, font=("Arial",10), bg="#f5f5f5", width=22, anchor="w").pack(side="left")
            v = tk.StringVar(); tk.Entry(row2, textvariable=v, font=("Arial",10), width=18).pack(side="left")
            vs[key] = v
        critical_var = tk.BooleanVar()
        tk.Checkbutton(win, text="🚨 Σήμανση Κρίσιμης Κατάστασης", variable=critical_var,
                        bg="#f5f5f5", font=("Arial",10)).pack(pady=4)

        def save():
            try: temp = float(vs["temp"].get()) if vs["temp"].get() else None
            except: temp = None
            try: wt = float(vs["wt"].get()) if vs["wt"].get() else None
            except: wt = None
            # DailyLogManager.addDailyLog (Class Diagram)
            mgr = DailyLogManager()
            mgr.addDailyLog(hosp_id, temp, wt, vs["meds"].get(), vs["notes"].get())
            if critical_var.get():
                mgr.setCriticalStatus(hosp_id)
                mgr.sendUrgentAlert(owner_id, animal_id)
                messagebox.showwarning("🚨 Κρίσιμη Κατάσταση",
                    "Η κατάσταση σημάνθηκε ως κρίσιμη. Ο ιδιοκτήτης ειδοποιήθηκε.")
            else:
                messagebox.showinfo("Επιτυχία","Καταγραφή αποθηκεύτηκε!")
            win.destroy()

        tk.Button(win, text="✔ Αποθήκευση", command=save,
                  bg=COLORS["btn_green"], fg="white", font=("Arial",11,"bold"),
                  bd=0, pady=7, cursor="hand2").pack(pady=12)

    def _discharge_win(self, hosp_id, owner_id):
        win = tk.Toplevel(self.root)
        win.title("Έκδοση Εξιτηρίου")
        win.geometry("400x280")
        win.configure(bg="#f5f5f5")
        tk.Label(win, text="🚪 Έκδοση Εξιτηρίου", font=("Arial",14,"bold"), bg="#f5f5f5").pack(pady=12)
        tk.Label(win, text="Οδηγίες φροντίδας στο σπίτι:", font=("Arial",10), bg="#f5f5f5").pack(anchor="w", padx=16)
        iv = tk.StringVar()
        tk.Entry(win, textvariable=iv, font=("Arial",10), width=40).pack(padx=16, pady=4)

        def discharge():
            instructions = iv.get().strip()
            # DischargeManager.process (Class Diagram)
            mgr = DischargeManager()
            mgr.process(hosp_id, instructions)
            conn = get_connection()
            a = conn.execute("""SELECT a.id FROM hospitalizations h JOIN animals a ON h.animal_id=a.id WHERE h.id=?""",(hosp_id,)).fetchone()
            conn.close()
            if a: mgr.notifyOwner(owner_id, a["id"], instructions or "Ακολουθήστε τις οδηγίες του κτηνιάτρου.")
            messagebox.showinfo("Εξιτήριο","Εξιτήριο εκδόθηκε επιτυχώς!")
            win.destroy()
            self.show_hospitalizations()

        tk.Button(win, text="✔ Έκδοση Εξιτηρίου", command=discharge,
                  bg=COLORS["btn_red"], fg="white", font=("Arial",11,"bold"),
                  bd=0, pady=7, cursor="hand2").pack(pady=14)

    # ── UC5: Συνταγογράφηση ──────────────────────────────────────────────────
    # Uses: DrugCatalog, TempList, PrescriptionForm logic (Class Diagram)
    def show_prescriptions(self, preselect=None):
        clear_frame(self.main)
        section_title(self.main, "💊 Συνταγογράφηση Φαρμάκων (UC5)")

        conn    = get_connection()
        animals = conn.execute("SELECT id, name FROM animals ORDER BY name").fetchall()
        conn.close()
        catalog   = DrugCatalog()
        temp_list = TempList()  # TempList (Class Diagram)

        top = tk.Frame(self.main, bg=COLORS["bg_main"]); top.pack(anchor="w", padx=16, pady=4)
        tk.Label(top, text="Ζώο:", font=("Arial",10), bg=COLORS["bg_main"]).pack(side="left")
        av  = tk.StringVar()
        amap = {f"{a['name']} (#{a['id'][:8]})": a["id"] for a in animals}
        cb  = ttk.Combobox(top, textvariable=av, values=list(amap.keys()),
                            state="readonly", width=26, font=("Arial",10))
        cb.pack(side="left", padx=6)
        if preselect:
            for k,v in amap.items():
                if v==preselect: av.set(k); break

        # DrugCatalog search
        df  = tk.LabelFrame(self.main, text="Αναζήτηση Φαρμάκου (DrugCatalog.findDrug)",
                             font=("Arial",10,"bold"), bg=COLORS["bg_main"])
        df.pack(fill="x", padx=16, pady=6)
        d1  = tk.Frame(df, bg=COLORS["bg_main"]); d1.pack(anchor="w", padx=8, pady=4)
        tk.Label(d1, text="Φάρμακο:", font=("Arial",10), bg=COLORS["bg_main"]).pack(side="left")
        dv  = tk.StringVar()
        conn2 = get_connection()
        all_meds = [m["name"] for m in conn2.execute("SELECT name FROM medications ORDER BY name").fetchall()]
        conn2.close()
        dc  = ttk.Combobox(d1, textvariable=dv, values=all_meds, width=20, font=("Arial",10))
        dc.pack(side="left", padx=6)
        stock_lbl = tk.Label(d1, text="", font=("Arial",10), bg=COLORS["bg_main"], fg="#555")
        stock_lbl.pack(side="left", padx=6)

        def on_drug_sel(_=None):
            drug = catalog.findDrug(dv.get())
            if drug: stock_lbl.config(text=f"Stock: {drug['stock_level']} | {drug['type']}")
            else:     stock_lbl.config(text="❌ Δεν βρέθηκε")
        dc.bind("<<ComboboxSelected>>", on_drug_sel)

        d2 = tk.Frame(df, bg=COLORS["bg_main"]); d2.pack(anchor="w", padx=8, pady=4)
        tk.Label(d2, text="Ποσότητα:", font=("Arial",10), bg=COLORS["bg_main"]).pack(side="left")
        qv = tk.StringVar(value="1")
        tk.Entry(d2, textvariable=qv, font=("Arial",10), width=6).pack(side="left", padx=6)
        tk.Label(d2, text="Δοσολογία:", font=("Arial",10), bg=COLORS["bg_main"]).pack(side="left", padx=(10,0))
        dosv = tk.StringVar()
        tk.Entry(d2, textvariable=dosv, font=("Arial",10), width=24).pack(side="left", padx=6)

        # TempList display
        lf  = tk.LabelFrame(self.main, text="Φάρμακα Συνταγής (TempList)",
                             font=("Arial",10,"bold"), bg=COLORS["bg_main"])
        lf.pack(fill="x", padx=16, pady=4)
        lb  = tk.Listbox(lf, font=("Arial",10), height=5); lb.pack(fill="x", padx=4, pady=4)

        def add_drug():
            dname = dv.get().strip()
            drug  = catalog.findDrug(dname)
            if not drug:
                messagebox.showerror("Σφάλμα","Το φάρμακο δεν βρέθηκε στον κατάλογο."); return
            try:
                qty = int(qv.get())
                if qty < 1 or qty > 100: raise ValueError
            except: messagebox.showerror("Σφάλμα","Ποσότητα: 1-100."); return
            if drug["stock_level"] < qty:
                messagebox.showerror("⚠️ Ανεπαρκές Απόθεμα",
                    f"Stock {dname}: {drug['stock_level']} (ζητείται {qty})"); return
            # TempList.add (Class Diagram)
            temp_list.add(drug, qty, dosv.get())
            lb.insert(tk.END, f"• {dname} x{qty} | {dosv.get()}")

        tk.Button(df, text="➕ Προσθήκη (TempList.add)", command=add_drug,
                  bg=COLORS["btn_blue"], fg="white", font=("Arial",9,"bold"),
                  bd=0, padx=8, pady=4, cursor="hand2").pack(anchor="w", padx=8, pady=4)

        def submit():
            key = av.get()
            items = temp_list.getData()
            if not key or not items:
                messagebox.showwarning("Ελλιπή","Επιλέξτε ζώο και προσθέστε τουλάχιστον ένα φάρμακο."); return
            aid   = amap[key]
            today = date.today().isoformat()
            conn  = get_connection()
            rid   = str(uuid.uuid4())
            conn.execute("INSERT INTO medical_records (id,record_date,notes,record_type,animal_id,vet_id) VALUES (?,?,?,?,?,?)",
                         (rid, today, "Συνταγογράφηση", "Συνταγή", aid, self.vet_id))
            pres_id = str(uuid.uuid4())
            conn.execute("INSERT INTO prescriptions (id,pres_date,animal_id,vet_id,record_id) VALUES (?,?,?,?,?)",
                         (pres_id, today, aid, self.vet_id, rid))
            for item in items:
                conn.execute("INSERT INTO prescription_items (id,prescription_id,medication_id,quantity,dosage) VALUES (?,?,?,?,?)",
                             (str(uuid.uuid4()), pres_id, item["drug"]["id"], item["quantity"], item["dosage"]))
                # InventoryManager.decreaseStock (Class Diagram)
                try: InventoryManager().decreaseStock(item["drug"]["name"], item["quantity"])
                except ValueError as e: messagebox.showwarning("Απόθεμα", str(e))
            conn.commit(); conn.close()
            # TempList.clearData (Class Diagram)
            temp_list.clearData()
            messagebox.showinfo("Επιτυχία","Η συνταγή καταχωρήθηκε!")
            self.show_prescriptions()

        def cancel():
            if temp_list.getData() and messagebox.askyesno("Ακύρωση","Να ακυρωθεί η συνταγή;"):
                temp_list.clearData(); lb.delete(0, tk.END)

        br = tk.Frame(self.main, bg=COLORS["bg_main"]); br.pack(anchor="w", padx=16, pady=6)
        tk.Button(br, text="✔ Καταχώρηση Συνταγής (savePermanently)", command=submit,
                  bg=COLORS["btn_green"], fg="white", font=("Arial",10,"bold"),
                  bd=0, pady=6, cursor="hand2").pack(side="left", padx=(0,8))
        tk.Button(br, text="✖ Ακύρωση", command=cancel,
                  bg=COLORS["btn_red"], fg="white", font=("Arial",10,"bold"),
                  bd=0, pady=6, cursor="hand2").pack(side="left")

    # ── UC6: Αναφορές ─────────────────────────────────────────────────────────
    # Uses: ReportGenerator, MedHistory, FilterForm (Class Diagram)
    def show_reports(self):
        clear_frame(self.main)
        section_title(self.main, "📊 Αναφορές Ιατρικού Ιστορικού (UC6)")

        conn    = get_connection()
        animals = conn.execute("SELECT id, name FROM animals ORDER BY name").fetchall()
        conn.close()

        ff = tk.Frame(self.main, bg=COLORS["bg_main"]); ff.pack(anchor="w", padx=16, pady=6)
        tk.Label(ff, text="Ζώο:", font=("Arial",10), bg=COLORS["bg_main"]).pack(side="left")
        av   = tk.StringVar()
        amap = {f"{a['name']} (#{a['id'][:8]})": a["id"] for a in animals}
        ttk.Combobox(ff, textvariable=av, values=list(amap.keys()),
                     state="readonly", width=22, font=("Arial",10)).pack(side="left", padx=6)
        tk.Label(ff, text="Από:", font=("Arial",10), bg=COLORS["bg_main"]).pack(side="left", padx=(10,0))
        fv = tk.StringVar(value="2024-01-01")
        tk.Entry(ff, textvariable=fv, font=("Arial",10), width=12).pack(side="left", padx=4)
        tk.Label(ff, text="Έως:", font=("Arial",10), bg=COLORS["bg_main"]).pack(side="left")
        tv = tk.StringVar(value=date.today().isoformat())
        tk.Entry(ff, textvariable=tv, font=("Arial",10), width=12).pack(side="left", padx=4)

        rf = tk.Frame(self.main, bg=COLORS["bg_main"])
        rf.pack(fill="both", expand=True, padx=16, pady=6)

        def generate():
            clear_frame(rf)
            key = av.get()
            if not key: messagebox.showwarning("Ελλιπή","Επιλέξτε ζώο."); return
            aid = amap[key]
            try:
                # ReportGenerator.retrieveData → MedHistory.retrieveData (Class Diagram)
                gen  = ReportGenerator()
                data = gen.retrieveData(aid, fv.get().strip(), tv.get().strip())
            except ValueError as e:
                messagebox.showerror("Σφάλμα",str(e)); return
            if not data:
                tk.Label(rf, text="Δεν βρέθηκαν εγγραφές για το επιλεγμένο διάστημα.",
                         font=("Arial",11), bg=COLORS["bg_main"], fg="gray").pack(pady=10)
                return
            tk.Label(rf, text=f"Αναφορά: {key} | {fv.get()} → {tv.get()}",
                     font=("Arial",11,"bold"), bg=COLORS["bg_main"]).pack(anchor="w")
            sb  = tk.Scrollbar(rf); sb.pack(side="right", fill="y")
            lb  = tk.Listbox(rf, font=("Arial",10), yscrollcommand=sb.set, height=12)
            lb.pack(fill="both", expand=True); sb.config(command=lb.yview)
            for r in data:
                detail = r.get("diagnosis") or r.get("vaccine_name") or r.get("notes") or ""
                lb.insert(tk.END, f"[{r['record_date']}] {r['record_type']}: {detail}")
            # ReportGenerator.generatePDF (Class Diagram)
            pdf_text = gen.generatePDF(data, f"Αναφορά {key}")
            def save_report():
                messagebox.showinfo("Αποθήκευση Αναφοράς",
                    f"Η αναφορά αποθηκεύτηκε!\n\n{pdf_text[:200]}...")
            tk.Button(rf, text="💾 Αποθήκευση Αναφοράς (generatePDF)", command=save_report,
                      bg=COLORS["btn_blue"], fg="white", font=("Arial",10,"bold"),
                      bd=0, pady=5, cursor="hand2").pack(anchor="w", pady=6)

        tk.Button(ff, text="📊 Δημιουργία Αναφοράς", command=generate,
                  bg=COLORS["btn_blue"], fg="white", font=("Arial",10,"bold"),
                  bd=0, padx=8, pady=4, cursor="hand2").pack(side="left", padx=6)

    # ── UC10: Απόθεμα Φαρμάκων ───────────────────────────────────────────────
    # Uses: InventoryManager, ForecastEngine (Class Diagram)
    def show_stock(self):
        clear_frame(self.main)
        section_title(self.main, "📦 Διαχείριση Αποθέματος Φαρμάκων (UC10)")

        conn = get_connection()
        meds = conn.execute("SELECT * FROM medications ORDER BY name").fetchall()
        conn.close()

        # ForecastEngine.triggerForecast (Class Diagram)
        alerts = ForecastEngine().triggerForecast()
        if alerts:
            af = tk.Label(self.main,
                text="⚠️ FORECAST ALERT: " + ", ".join(f"{a['name']} ({a['stock_level']})" for a in alerts),
                font=("Arial",9,"bold"), bg="#FFF3CD", fg="#856404")
            af.pack(fill="x", padx=16, pady=4)

        lf = tk.Frame(self.main, bg=COLORS["bg_main"])
        lf.pack(fill="x", padx=16, pady=6)
        headers = ["Φάρμακο","Τύπος","Δραστική Ουσία","Stock","Ελάχ.","Κατάσταση"]
        widths  = [14, 10, 16, 6, 6, 10]
        for i,(h,w) in enumerate(zip(headers,widths)):
            tk.Label(lf, text=h, font=("Arial",9,"bold"), bg="#87CEEB",
                     width=w, relief="solid").grid(row=0, column=i, sticky="ew")
        for ri, m in enumerate(meds, 1):
            ok = m["stock_level"] > m["min_threshold"]
            status = "✅ OK" if ok else "⚠️ ΧΑΜΗΛΟ"
            fg = "black" if ok else "red"
            vals = [m["name"], m["type"] or "", m["active_ingredient"] or "",
                    str(m["stock_level"]), str(m["min_threshold"]), status]
            for ci,(val,w) in enumerate(zip(vals,widths)):
                tk.Label(lf, text=val, font=("Arial",9), bg="white", fg=fg,
                         width=w, relief="solid").grid(row=ri, column=ci, sticky="ew")

        # InventoryManager.updateStock (restock)
        rf = tk.LabelFrame(self.main, text="Αναπλήρωση Αποθέματος (InventoryManager.updateStock)",
                            font=("Arial",10,"bold"), bg=COLORS["bg_main"])
        rf.pack(fill="x", padx=16, pady=8)
        row3 = tk.Frame(rf, bg=COLORS["bg_main"]); row3.pack(anchor="w", padx=8, pady=6)
        tk.Label(row3, text="Φάρμακο:", font=("Arial",10), bg=COLORS["bg_main"]).pack(side="left")
        mv = tk.StringVar()
        ttk.Combobox(row3, textvariable=mv, values=[m["name"] for m in meds],
                     state="readonly", width=18, font=("Arial",10)).pack(side="left", padx=6)
        tk.Label(row3, text="Ποσότητα:", font=("Arial",10), bg=COLORS["bg_main"]).pack(side="left", padx=(10,0))
        qv = tk.StringVar(value="10")
        tk.Entry(row3, textvariable=qv, font=("Arial",10), width=8).pack(side="left", padx=4)

        def restock():
            name = mv.get()
            try:
                qty = int(qv.get()); assert qty > 0
            except: messagebox.showerror("Σφάλμα","Εισάγετε θετικό αριθμό."); return
            if not name: messagebox.showwarning("Ελλιπή","Επιλέξτε φάρμακο."); return
            InventoryManager().updateStock(name, qty)
            messagebox.showinfo("Επιτυχία", f"Προστέθηκαν {qty} τεμάχια {name}.")
            self.show_stock()

        tk.Button(rf, text="✔ Αναπλήρωση", command=restock,
                  bg=COLORS["btn_green"], fg="white", font=("Arial",10,"bold"),
                  bd=0, pady=6, cursor="hand2").pack(anchor="w", padx=8, pady=4)
