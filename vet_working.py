import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox

# ==========================================
# 1. Η ΟΝΤΟΤΗΤΑ ΤΗΣ ΒΑΣΗΣ ΔΕΔΟΜΕΝΩΝ (MOCK DB)
# ==========================================
class MockDatabase:
    def __init__(self):
        self.records = [
            {"id": 1, "name": "Bella", "owner": "Γιώργος", "phone": "6900000001", "history": ["Εμβόλιο Λύσσας", "Εξέταση Αίματος"]},
            {"id": 2, "name": "Max", "owner": "Μαρία", "phone": "6900000002", "history": ["Καθαρισμός Δοντιών"]},
            {"id": 3, "name": "Max", "owner": "Κώστας", "phone": "6900000003", "history": ["Στείρωση"]},
            {"id": 4, "name": "Rocky", "owner": "Ελένη", "phone": "6900000004", "history": []} # Κενό Ιστορικό
        ]

    def search(self, query):
        results = []
        for r in self.records:
            if query.lower() == r["name"].lower() or query == r["phone"]:
                results.append(r)
        return results

# ==========================================
# 2. Η ΚΕΝΤΡΙΚΗ ΟΘΟΝΗ (ΜΕ ΕΝΕΡΓΑ ΚΟΥΜΠΙΑ ΜΕΝΟΥ)
# ==========================================
class VetHomeScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("VetPro - Αρχική Κτηνιάτρου")
        self.root.geometry("850x500")
        self.root.configure(bg="#D3D3D3")
        
        self.db = MockDatabase()
        
        # --- Sidebar ---
        self.sidebar_frame = tk.Frame(self.root, bg="#87CEEB", width=250)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)
        
        logo_font = tkfont.Font(family="Comic Sans MS", size=24, weight="bold")
        self.logo_label = tk.Label(self.sidebar_frame, text="🐾 VetPro", font=logo_font, bg="#87CEEB", fg="#9932CC")
        self.logo_label.pack(pady=(20, 30))
        
        # --- Ενεργοποίηση Κουμπιών Sidebar ---
        def go_home():
            messagebox.showinfo("Πλοήγηση", "Βρίσκεστε ήδη στην Αρχική!")
            
        def open_appointments():
            messagebox.showinfo("Πλοήγηση", "Σύντομα: Άνοιγμα οθόνης 'Κλείσιμο Ραντεβού'")
            
        def open_prescriptions():
            messagebox.showinfo("Πλοήγηση", "Σύντομα: Άνοιγμα οθόνης 'Συνταγογράφηση' ")

        # Λίστα με τα ονόματα και τις συναρτήσεις τους
        buttons_data = [
            ("Αρχική", go_home),
            ("Κλείσιμο Ραντεβού", open_appointments),
            ("Ιστορικό Ζώου", lambda: messagebox.showinfo("Πλοήγηση", "Χρησιμοποιήστε την Αναζήτηση στο κέντρο της οθόνης.")),
            ("Συνταγογράφηση", open_prescriptions),
            ("Διαχείριση Εμβολίων", lambda: messagebox.showinfo("Πλοήγηση", "Σύντομα: Άνοιγμα 'Διαχείριση Εμβολίων'"))
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
                command=btn_command # Εδώ συνδέεται το πάτημα με την ενέργεια
            )
            btn.pack(fill="x", padx=10, pady=2)

        # --- Main Content Area ---
        self.main_frame = tk.Frame(self.root, bg="#D3D3D3")
        self.main_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(self.main_frame, text="Αρχική", font=("Comic Sans MS", 32, "bold"), bg="#D3D3D3").place(x=20, y=20)
        
        # --- Search Bar ---
        self.search_frame = tk.Frame(self.main_frame, bg="black", bd=2, relief="solid")
        self.search_frame.place(x=150, y=280, width=300, height=40)
        
        tk.Label(self.search_frame, text="Αναζήτηση:", font=("Arial", 10, "bold"), bg="#696969", fg="black").pack(side="left", fill="y")
        
        self.search_entry = tk.Entry(self.search_frame, bg="#696969", fg="white", borderwidth=0, font=("Arial", 10, "bold"))
        self.search_entry.pack(side="left", fill="both", expand=True)
        
        self.search_entry.bind("<Return>", self.perform_search)
        
        tk.Label(self.main_frame, text=" Δοκίμασε: Bella, Max, Rocky, Lassie", bg="#D3D3D3", fg="#555555", font=("Arial", 9)).place(x=150, y=330)

    # ==========================================
    # 3. ΟΙ ΕΛΕΓΚΤΕΣ & ΤΑ ΣΕΝΑΡΙΑ ΑΝΑΖΗΤΗΣΗΣ
    # ==========================================
    def perform_search(self, event):
        query = self.search_entry.get().strip()
        if not query:
            return
            
        results = self.db.search(query)
        
        if len(results) == 0:
            messagebox.showerror("Σφάλμα", f"Δεν βρέθηκε πελάτης ή ζώο με τα στοιχεία '{query}'.")
            self.search_entry.delete(0, tk.END)
        elif len(results) > 1:
            self.show_results_list(results)
        else:
            self.open_animal_card(results[0])

    def show_results_list(self, results):
        list_window = tk.Toplevel(self.root)
        list_window.title("Επιλογή Ζώου (Βρέθηκε Συνωνυμία)")
        list_window.geometry("450x250")
        list_window.configure(bg="#87CEEB")
        
        tk.Label(list_window, text="Βρέθηκαν πολλαπλά αποτελέσματα.\nΕπιλέξτε το σωστό:", bg="#87CEEB", font=("Arial", 11, "bold")).pack(pady=10)
        
        listbox = tk.Listbox(list_window, font=("Arial", 11), width=45, selectbackground="#4DA6FF")
        listbox.pack(pady=5)
        
        for r in results:
            listbox.insert(tk.END, f" 🐶 {r['name']}  |  Ιδιοκτ: {r['owner']}  |  Τηλ: {r['phone']}")
            
        def on_select(event=None):
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                list_window.destroy()
                self.open_animal_card(results[index])
            else:
                messagebox.showwarning("Προσοχή", "Παρακαλώ επιλέξτε ένα ζώο από τη λίστα κάνοντας κλικ πάνω του!")

        listbox.bind("<Double-1>", on_select)
        tk.Button(list_window, text="Επιβεβαίωση Επιλογής", command=on_select, bg="#28A745", fg="white", font=("Arial", 10, "bold"), padx=10).pack(pady=10)

    def open_animal_card(self, animal_data):
        card_window = tk.Toplevel(self.root)
        card_window.title(f"Καρτέλα Ζώου - {animal_data['name']}")
        card_window.geometry("380x380")
        card_window.configure(bg="#f0f0f0")
        
        tk.Label(card_window, text=f"🐾 {animal_data['name']}", font=("Arial", 18, "bold"), fg="#333333").pack(pady=(15, 5))
        tk.Label(card_window, text=f"Ιδιοκτήτης: {animal_data['owner']} | Τηλ: {animal_data['phone']}", font=("Arial", 10), fg="#555555").pack()
        
        tk.Label(card_window, text="Ιατρικό Ιστορικό:", font=("Arial", 12, "bold", "underline")).pack(pady=(15, 5))
        
        if len(animal_data['history']) == 0:
            tk.Label(card_window, text=" Κενό Ιστορικό / Πρώτη Επίσκεψη", fg="#DC143C", font=("Arial", 11, "bold")).pack(pady=5)
        else:
            history_frame = tk.Frame(card_window, bg="#f0f0f0")
            history_frame.pack(pady=5)
            for item in animal_data['history']:
                tk.Label(history_frame, text=f" {item}", font=("Arial", 10), bg="#f0f0f0").pack(anchor="w")

        tk.Label(card_window, text="Γρήγορες Ενέργειες:", font=("Arial", 10, "bold")).pack(pady=(20, 5))
        
        actions_frame = tk.Frame(card_window, bg="#f0f0f0")
        actions_frame.pack()
        
        def mock_action(action_name):
            messagebox.showinfo(action_name, f"Σύντομα θα ανοίγει η οθόνη για '{action_name}'.")

        tk.Button(actions_frame, text=" Νέα Εξέταση", command=lambda: mock_action("Νέα Εξέταση"), bg="#28A745", fg="white", width=12).grid(row=0, column=0, padx=5)
        tk.Button(actions_frame, text=" Συνταγή", command=lambda: mock_action("Συνταγογράφηση"), bg="#4DA6FF", fg="white", width=12).grid(row=0, column=1, padx=5)
        
        tk.Button(card_window, text="Κλείσιμο", command=card_window.destroy, bg="#6c757d", fg="white", width=26).pack(side="bottom", pady=20)

def main():
    root = tk.Tk()
    app = VetHomeScreen(root)
    root.mainloop()

if __name__ == "__main__":
    main()