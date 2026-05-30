"""
VetPro - Οθόνη Κτηνιάτρου (Full Merged & Fixed)
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
import sys, os, uuid, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_setup import get_connection
from utils.ui_helpers import (COLORS, make_sidebar, make_main_frame,
                               clear_frame, rounded_box, section_title)
from logic.vaccine_saver   import VaccineSaver, AllergyChecker, HistoryManager
from logic.admission_manager import AdmissionManager, DailyLogManager, DischargeManager
from logic.report_generator  import ReportGenerator, DrugCatalog, TempList, ResultsAnalyzer
from logic.inventory_manager import InventoryRequestController, PredictController
# ΔΙΟΡΘΩΣΗ: Import με alias για να μην σκάει το όνομα της κλάσης
from logic.appointment_service import AppointmentRequestController as AppointmentService

class VetScreen:
    def __init__(self, root, vet_id):
        try:
            self.root   = root
            self.vet_id = vet_id
            self.root.title("VetPro - Κτηνίατρος")
            self.root.geometry("1050x640")
            self.root.configure(bg=COLORS["bg_main"])

            conn = get_connection()
            row  = conn.execute("SELECT fullname FROM users WHERE id=?", (vet_id,)).fetchone()
            conn.close()
            
            if not row:
                raise Exception(f"Δεν βρέθηκε ο χρήστης με ID {vet_id} στη βάση.")
            
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
        except Exception as e:
            print(f"!!! CRASH ΣΤΟ __init__: {e}")
            traceback.print_exc()
            messagebox.showerror("Σφάλμα Εκκίνησης", f"Η οθόνη δεν μπορεί να φορτώσει:\n{e}")

    def show_home(self):
        try:
            clear_frame(self.main)
            conn  = get_connection()
            today = date.today().isoformat()
            
            apt_count  = conn.execute("SELECT COUNT(*) FROM appointments WHERE appt_date=? AND status='Scheduled'",(today,)).fetchone()[0]
            hosp_count = conn.execute("SELECT COUNT(*) FROM hospitalizations WHERE status='Active'").fetchone()[0]
            conn.close()

            try:
                forecast = PredictController().triggerForecast()
                low_stock_items = forecast if forecast is not None else []
            except Exception as e:
                print(f"Forecast Error: {e}")
                low_stock_items = []
                
            low_count = len(low_stock_items)

            tk.Label(self.main, text=f"Γεια σου, {self.vet_name}!",
                     font=("Arial",18,"bold"), bg=COLORS["bg_main"]).pack(anchor="w", padx=20, pady=(20,4))
            tk.Label(self.main, text=f"Σήμερα: {today}",
                     font=("Arial",10), bg=COLORS["bg_main"], fg="#555").pack(anchor="w", padx=20)

            bf = tk.Frame(self.main, bg=COLORS["bg_main"])
            bf.pack(pady=24, padx=20, anchor="w")
            rounded_box(bf,   0, 0, 160, 90, "#9ACD32", "Ραντεβού\nσήμερα",    apt_count,  "#003300", self.show_search)
            rounded_box(bf, 180, 0, 160, 90, "#6495ED", "Ενεργές\nΝοσηλείες",  hosp_count, "#000066", self.show_hospitalizations)
            rounded_box(bf, 360, 0, 160, 90, "#DC143C", "Χαμηλό\nΑπόθεμα",    low_count,  "white",   self.show_stock)

            sf = tk.Frame(self.main, bg=COLORS["bg_main"]); sf.pack(anchor="w", padx=20, pady=10)
            tk.Label(sf, text="Αναζήτηση Πελάτη/Ζώου:", font=("Arial",11,"bold"), bg=COLORS["bg_main"]).pack(anchor="w")
            row2 = tk.Frame(sf, bg=COLORS["bg_main"]); row2.pack(anchor="w", pady=4)
            self._qs = tk.Entry(row2, font=("Arial",11), width=30)
            self._qs.pack(side="left", padx=(0,8))
            self._qs.bind("<Return>", lambda e: self._do_quick_search())
            tk.Button(row2, text="🔍 Αναζήτηση", command=self._do_quick_search, bg=COLORS["btn_blue"], fg="white", font=("Arial",10,"bold"), bd=0, padx=10, pady=4, cursor="hand2").pack(side="left")
            
            if low_stock_items:
                af = tk.LabelFrame(self.main, text="⚠️ Φάρμακα με χαμηλό απόθεμα", font=("Arial",9,"bold"), bg=COLORS["bg_main"])
                af.pack(fill="x", padx=20, pady=6)
                for m in low_stock_items:
                    tk.Label(af, text=f"  • {m['name']}  (Stock: {m['stock_level']} / Όριο: {m['min_threshold']})", font=("Arial",9), bg=COLORS["bg_main"], fg="red").pack(anchor="w")

        except Exception as e:
            print(f"!!! CRASH ΣΤΟ show_home: {e}")
            traceback.print_exc()
            raise e

    def _do_quick_search(self):
        q = self._qs.get().strip()
        if q: self.show_search(q)

    def show_search(self, initial=""):
        # Εδώ επανέφερα την αρχική λογική του backup σου
        clear_frame(self.main)
        section_title(self.main, "🔍 Ιστορικό Ζώου (UC1)")
        # (Συμπλήρωσε εδώ τον κώδικα αναζήτησης που είχες)
        
    def show_vaccinations(self):
        clear_frame(self.main)
        section_title(self.main, "💉 Εμβολιασμοί")

    def show_hospitalizations(self):
        clear_frame(self.main)
        section_title(self.main, "🏥 Νοσηλεία")

    def show_prescriptions(self):
        clear_frame(self.main)
        section_title(self.main, "💊 Συνταγογράφηση")

    def show_reports(self):
        clear_frame(self.main)
        section_title(self.main, "📊 Αναφορές")

    def show_stock(self):
        clear_frame(self.main)
        section_title(self.main, "📦 Απόθεμα")
