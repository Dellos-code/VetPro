import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox

# ==========================================
# 1. ΒΑΣΕΙΣ ΔΕΔΟΜΕΝΩΝ (MOCK ENTITIES)
# ==========================================
class MockDatabase:
    def __init__(self):
        # Βάση Ραντεβού / Εκκρεμών Πληρωμών
        self.appointments = [
            {"id": 101, "pet": "Bella", "owner": "Γιώργος", "charges": 50.0, "status": "Pending"},
            {"id": 102, "pet": "Max", "owner": "Μαρία", "charges": 120.0, "status": "Pending"},
            {"id": 103, "pet": "Luna", "owner": "Νίκος", "charges": 35.0, "status": "Pending"},
            {"id": 104, "pet": "Rocky", "owner": "Ελένη", "charges": 0.0, "status": "Pending"}
        ]
        
        # Καρτέλες Ιδιοκτητών (για καταγραφή χρέους)
        self.owner_cards = {
            "Γιώργος": {"debt": 0.0},
            "Μαρία": {"debt": 0.0},
            "Νίκος": {"debt": 0.0},
            "Ελένη": {"debt": 0.0}
        }

    def get_pending_appointments(self):
        return [apt for apt in self.appointments if apt["status"] == "Pending"]

# ==========================================
# 2. ΚΕΝΤΡΙΚΗ ΟΘΟΝΗ ΡΕΣΕΨΙΟΝ (ΜΕ ΠΛΟΗΓΗΣΗ)
# ==========================================
class ReceptionHomeScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("VetPro - Αρχική Ρεσεψιόν")
        self.root.geometry("850x550")
        self.root.configure(bg="#D3D3D3")
        
        self.db = MockDatabase()
        
        # --- Sidebar (Σταθερό Αριστερά) ---
        self.sidebar_frame = tk.Frame(self.root, bg="#87CEEB", width=250)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)
        
        logo_font = tkfont.Font(family="Comic Sans MS", size=24, weight="bold")
        tk.Label(self.sidebar_frame, text="🐾 VetPro", font=logo_font, bg="#87CEEB", fg="#9932CC").pack(pady=(20, 30))
        
        # Δημιουργία των κουμπιών sidebar με σύνδεση στις αντίστοιχες οθόνες
        buttons_data = [
            ("Αρχική", self.show_home_view),
            ("Κλείσιμο Ραντεβού", lambda: messagebox.showinfo("Πλοήγηση", "Σύντομα: Οθόνη 'Κλείσιμο Ραντεβού'")),
            ("Ειδοποιήσεις", lambda: messagebox.showinfo("Πλοήγηση", "Σύντομα: Οθόνη 'Ειδοποιήσεων'")),
            ("Πληρωμή/ Χρέωση", self.show_payments_view),
            ("Αναφορές", lambda: messagebox.showinfo("Πλοήγηση", "Σύντομα: Οθόνη 'Αναφορών'"))
        ]
        
        for btn_text, btn_command in buttons_data:
            btn = tk.Button(
                self.sidebar_frame,
                text=btn_text,
                font=("Arial", 10, "bold"),
                bg="#87CEEB",
                anchor="w",
                padx=20,
                pady=5,
                bd=1,
                relief="solid",
                command=btn_command
            )
            btn.pack(fill="x", padx=10, pady=2)

        # --- Main Content Area (Μεταβαλλόμενο Δεξιά) ---
        self.main_frame = tk.Frame(self.root, bg="#D3D3D3")
        self.main_frame.pack(side="left", fill="both", expand=True)
        
        # Φόρτωση της Αρχικής οθόνης κατά την εκκίνηση
        self.show_home_view()

    def clear_main_frame(self):
        """Καθαρίζει τη δεξιά πλευρά της οθόνης για να σχεδιαστεί το νέο View"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ==========================================
    # ΟΘΟΝΗ 1: ΑΡΧΙΚΗ (DASHBOARD ΜΕ ΚΛΙΚΑΡΙΣΤΑ ΚΟΥΤΑΚΙΑ)
    # ==========================================
    def show_home_view(self):
        self.clear_main_frame()
        
        # Τίτλος & Υπότιτλος
        tk.Label(self.main_frame, text="Αρχική", font=("Comic Sans MS", 32, "bold"), bg="#D3D3D3", fg="black").place(x=20, y=20)
        tk.Label(self.main_frame, text="Καλώς ήρθατε στο VetPro 🐶", font=("Arial", 12, "bold"), bg="#D3D3D3", fg="black").place(x=20, y=100)
        
        boxes_y = 150
        
        # -- Ορισμός ενεργειών όταν πατάμε τα κουτάκια --
        def on_appointments_click(event):
            messagebox.showinfo("Ραντεβού της Ημέρας", "Εδώ θα εμφανίζεται η αναλυτική λίστα με τα σημερινά ραντεβού.")

        def on_payments_click(event):
            # Όταν πατάμε το μπλε κουτάκι, μας πάει στην οθόνη πληρωμών!
            self.show_payments_view()

        def on_notifications_click(event):
            messagebox.showinfo("Ειδοποιήσεις", "Εδώ θα προβάλλονται τα μηνύματα που πρέπει να σταλούν στους ιδιοκτήτες.")
        
        # Κουτάκι 1: Ραντεβού της Ημέρας
        self.create_info_box(self.main_frame, x=150, y=boxes_y, bg_color="#9ACD32", 
                             title="Ραντεβού\nτης Ημέρας", count="12", count_color="#0000FF", command=on_appointments_click)
        
        # Κουτάκι 2: Δυναμικό & Κλικάριστο!
        pending_count = len(self.db.get_pending_appointments())
        self.create_info_box(self.main_frame, x=320, y=boxes_y, bg_color="#6495ED", 
                             title="Εκκρεμείς\nΠληρωμές", count=str(pending_count), count_color="#0000FF", command=on_payments_click)
        
        # Κουτάκι 3: Ειδοποιήσεις προς Αποστολή
        self.create_info_box(self.main_frame, x=490, y=boxes_y, bg_color="#DC143C", 
                             title="Ειδοποιήσεις\nπρος Αποστολή", count="4", count_color="black", command=on_notifications_click)
        
        # Placeholder Γάτας κάτω δεξιά
        tk.Label(self.main_frame, text="🐱", font=("Arial", 60), bg="#D3D3D3").place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

    # ==========================================
    # ΟΘΟΝΗ 2: ΛΙΣΤΑ ΕΚΚΡΕΜΩΝ ΠΛΗΡΩΜΩΝ
    # ==========================================
    def show_payments_view(self):
        self.clear_main_frame()
        
        tk.Label(self.main_frame, text="Εκκρεμείς Πληρωμές", font=("Comic Sans MS", 28, "bold"), bg="#D3D3D3", fg="black").place(x=20, y=20)
        
        self.list_frame = tk.Frame(self.main_frame, bg="#D3D3D3")
        self.list_frame.place(x=20, y=100, width=550, height=350)
        
        pending = self.db.get_pending_appointments()
        
        if not pending:
            tk.Label(self.list_frame, text="Δεν υπάρχουν εκκρεμείς πληρωμές!", font=("Arial", 12, "bold"), bg="#D3D3D3", fg="green").pack(pady=20)
        else:
            for apt in pending:
                apt_frame = tk.Frame(self.list_frame, bg="white", bd=1, relief="solid")
                apt_frame.pack(fill="x", pady=5, padx=5)
                
                info_text = f"🐶 {apt['pet']}  |  Ιδιοκτ: {apt['owner']}  |  Ποσό: €{apt['charges']}"
                tk.Label(apt_frame, text=info_text, font=("Arial", 11), bg="white").pack(side="left", padx=10, pady=10)
                
                pay_btn = tk.Button(apt_frame, text="Πληρωμή", bg="#28A745", fg="white", font=("Arial", 10, "bold"),
                                    command=lambda a=apt: self.process_payment_selection(a))
                pay_btn.pack(side="right", padx=10, pady=5)
                
        tk.Label(self.main_frame, text="🐱", font=("Arial", 60), bg="#D3D3D3").place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

    # ==========================================
    # 3. ΕΛΕΓΚΤΕΣ & ΠΑΡΑΘΥΡΑ ΔΙΑΛΟΓΟΥ (UC2 LOGIC)
    # ==========================================
    def process_payment_selection(self, appointment):
        if appointment["charges"] <= 0:
            messagebox.showerror("Απουσία Χρεώσεων", f"Σφάλμα: Δεν υπάρχουν καταχωρημένες χρεώσεις για την επίσκεψη του {appointment['pet']}.\n\nΠαρακαλώ ζητήστε από τον Κτηνίατρο να ενημερώσει την καρτέλα.")
            return
            
        self.open_payment_screen(appointment)

    def open_payment_screen(self, appointment):
        pay_win = tk.Toplevel(self.root)
        pay_win.title(f"Πληρωμή - {appointment['pet']}")
        pay_win.geometry("400x350")
        pay_win.configure(bg="#f8f9fa")
        
        tk.Label(pay_win, text=f"Συναλλαγή: {appointment['owner']}", font=("Arial", 16, "bold"), bg="#f8f9fa").pack(pady=15)
        
        total_cost = appointment["charges"]
        tk.Label(pay_win, text=f"Συνολικό Ποσό: €{total_cost}", font=("Arial", 14, "bold"), fg="#DC143C", bg="#f8f9fa").pack(pady=10)
        
        tk.Label(pay_win, text="Ποσό που δόθηκε (€):", font=("Arial", 11), bg="#f8f9fa").pack(pady=5)
        amount_entry = tk.Entry(pay_win, font=("Arial", 12), width=15, justify="center")
        amount_entry.insert(0, str(total_cost))
        amount_entry.pack()

        def confirm_payment(method):
            try:
                given_amount = float(amount_entry.get())
            except ValueError:
                messagebox.showerror("Λάθος", "Παρακαλώ εισάγετε έγκυρο ποσό.")
                return

            if method == "Card_Fail":
                messagebox.showerror("Απόρριψη Συναλλαγής", "Σφάλμα από το POS:\nΗ συναλλαγή απορρίφθηκε (Πιθανή έλλειψη υπολοίπου). Ζητήστε εναλλακτικό τρόπο πληρωμής.")
                return

            if given_amount < total_cost:
                debt = total_cost - given_amount
                self.db.owner_cards[appointment["owner"]]["debt"] += debt
                appointment["status"] = "Partially Paid"
                msg = f"Επιτυχής Μερική Πληρωμή!\n\nΕισπράχθηκαν: €{given_amount}\nΠροστέθηκε χρέος: €{debt} στην καρτέλα του/της {appointment['owner']}."
            else:
                appointment["status"] = "Paid"
                msg = f"Η πληρωμή ολοκληρώθηκε επιτυχώς με {method}!"

            messagebox.showinfo("Ολοκλήρωση", msg)
            pay_win.destroy()
            
            # Ανανέωση του View στο οποίο βρισκόμαστε αυτή τη στιγμή
            self.show_payments_view()

        btn_frame = tk.Frame(pay_win, bg="#f8f9fa")
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="💵 Μετρητά", command=lambda: confirm_payment("Μετρητά"), bg="#28A745", fg="white", width=12).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="💳 Κάρτα (Επιτυχία)", command=lambda: confirm_payment("Κάρτα"), bg="#4DA6FF", fg="white", width=15).grid(row=0, column=1, padx=5)
        
        tk.Button(pay_win, text="⚠️ Προσομοίωση: Απόρριψη Κάρτας", command=lambda: confirm_payment("Card_Fail"), bg="#ffc107", fg="black").pack(pady=10)

    # ==========================================
    # ΒΟΗΘΗΤΙΚΗ ΣΥΝΑΡΤΗΣΗ ΓΙΑ ΣΧΕΔΙΑΣΗ ΚΟΥΤΙΩΝ (CANVAS) - ΤΩΡΑ CLICKABLE!
    # ==========================================
    def create_info_box(self, container, x, y, bg_color, title, count, count_color, command=None):
        # Αν υπάρχει "command", κάνουμε το ποντίκι "χεράκι" (hand2) για να ξέρει ο χρήστης ότι πατιέται
        cursor_type = "hand2" if command else ""
        canvas = tk.Canvas(container, width=150, height=80, bg="#D3D3D3", highlightthickness=0, cursor=cursor_type)
        canvas.place(x=x, y=y)
        
        r = 15 
        w = 150
        h = 80
        
        canvas.create_arc(0, 0, r*2, r*2, start=90, extent=90, fill=bg_color, outline=bg_color)
        canvas.create_arc(w-r*2, 0, w, r*2, start=0, extent=90, fill=bg_color, outline=bg_color)
        canvas.create_arc(0, h-r*2, r*2, h, start=180, extent=90, fill=bg_color, outline=bg_color)
        canvas.create_arc(w-r*2, h-r*2, w, h, start=270, extent=90, fill=bg_color, outline=bg_color)
        
        canvas.create_rectangle(r, 0, w-r, h, fill=bg_color, outline=bg_color)
        canvas.create_rectangle(0, r, w, h-r, fill=bg_color, outline=bg_color)
        
        canvas.create_text(10, 10, text=title, anchor="nw", font=("Arial", 10, "bold"), fill="black")
        canvas.create_text(140, 70, text=count, anchor="se", font=("Arial", 12, "bold"), fill=count_color)
        
        # Σύνδεση του αριστερού κλικ (<Button-1>) με τη συνάρτηση (αν δόθηκε κάποια)
        if command:
            canvas.bind("<Button-1>", command)


def main():
    root = tk.Tk()
    app = ReceptionHomeScreen(root)
    root.mainloop()

if __name__ == "__main__":
    main()