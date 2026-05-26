import tkinter as tk
from tkinter import messagebox
import sqlite3
import os

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("VetPro - Login")
        self.root.geometry("400x380")
        self.root.configure(bg="#87CEEB")
        
        # Center frame
        center_frame = tk.Frame(root, bg="#87CEEB")
        center_frame.pack(expand=True)
        
        # Logo
        logo_label = tk.Label(
            center_frame,
            text="🐾 VetPro",
            font=("Arial", 28, "bold"),
            bg="#87CEEB",
            fg="#4169E1"
        )
        logo_label.pack(pady=(0, 30))
        
        # Username label and entry
        username_label = tk.Label(
            center_frame,
            text="Όνομα Χρήστη:",
            font=("Arial", 11),
            bg="#87CEEB",
            fg="#333333"
        )
        username_label.pack(anchor=tk.W, padx=20, pady=(10, 0))
        
        self.username_entry = tk.Entry(
            center_frame,
            font=("Arial", 11),
            width=25
        )
        self.username_entry.pack(padx=20, pady=(0, 15))
        
        # Password label and entry
        password_label = tk.Label(
            center_frame,
            text="Κωδικός Πρόσβασης:",
            font=("Arial", 11),
            bg="#87CEEB",
            fg="#333333"
        )
        password_label.pack(anchor=tk.W, padx=20, pady=(10, 0))
        
        self.password_entry = tk.Entry(
            center_frame,
            font=("Arial", 11),
            width=25,
            show="*"
        )
        self.password_entry.pack(padx=20, pady=(0, 20))
        
        # Login button
        login_btn = tk.Button(
            center_frame,
            text="Σύνδεση",
            font=("Arial", 12, "bold"),
            bg="#4DA6FF",
            fg="white",
            width=25,
            border=0,
            padx=10,
            pady=8,
            cursor="hand2",
            activebackground="#3D7FBF",
            command=self.login
        )
        login_btn.pack(pady=10)
        
        # Register button
        register_btn = tk.Button(
            center_frame,
            text="Εγγραφή",
            font=("Arial", 12, "bold"),
            bg="#28A745",
            fg="white",
            width=25,
            border=0,
            padx=10,
            pady=8,
            cursor="hand2",
            activebackground="#218838",
            command=self.open_register
        )
        register_btn.pack(pady=(0, 10))

    def get_db_path(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, 'vetpro.db')

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Ελλιπή Στοιχεία", "Παρακαλώ συμπληρώστε Όνομα Χρήστη και Κωδικό Πρόσβασης.")
            return
            
        try:
            conn = sqlite3.connect(self.get_db_path())
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = cursor.fetchone()
            
            conn.close()
            
            if user:
                role = user[6]
                
                self.root.withdraw() # Κρύβουμε το login
                new_window = tk.Toplevel(self.root)
                
                # Αν κλείσει το νέο παράθυρο, να κλείσει όλη η εφαρμογή
                def on_close():
                    self.root.destroy()
                new_window.protocol("WM_DELETE_WINDOW", on_close)
                
                if role == "Κτηνίατρος":
                    try:
                        from vet_home_screen import VetHomeScreen
                    except ImportError:
                        from application.vet_home_screen import VetHomeScreen
                    VetHomeScreen(new_window)
                    
                elif role == "Ρεσεψιόν":
                    try:
                        from reception_home_screen import ReceptionHomeScreen
                    except ImportError:
                        from application.reception_home_screen import ReceptionHomeScreen
                    ReceptionHomeScreen(new_window)
                    
                elif role == "Ιδιοκτήτης Κατοικίδιου":
                    try:
                        from owner_home_screen import OwnerHomeScreen
                    except ImportError:
                        from application.owner_home_screen import OwnerHomeScreen
                    OwnerHomeScreen(new_window)
                else:
                    messagebox.showerror("Σφάλμα Ρόλου", "Μη αναγνωρίσιμος ρόλος χρήστη.")
                    self.root.deiconify() # Εμφάνιση του login ξανά
            else:
                messagebox.showerror("Λάθος Στοιχεία", "Το Όνομα Χρήστη ή ο Κωδικός Πρόσβασης είναι λάθος.")
                
        except sqlite3.Error as e:
            messagebox.showerror("Σφάλμα Βάσης Δεδομένων", f"Συνέβη ένα σφάλμα: {e}")

    def open_register(self):
        register_window = tk.Toplevel(self.root)
        try:
            from register_screen import RegisterScreen
        except ImportError:
            from application.register_screen import RegisterScreen
        RegisterScreen(register_window)


def main():
    root = tk.Tk()
    app = LoginScreen(root)
    root.mainloop()


if __name__ == "__main__":
    main()
