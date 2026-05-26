import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import os

class RegisterScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("VetPro - Εγγραφή Νέου Χρήστη")
        self.root.geometry("450x680")
        self.root.configure(bg="#87CEEB")
        
        self.setup_database()
        
        # Center frame
        center_frame = tk.Frame(root, bg="#87CEEB")
        center_frame.pack(expand=True)
        
        # Logo or Title
        title_label = tk.Label(
            center_frame,
            text="🐾 Νέος Λογαριασμός",
            font=("Arial", 24, "bold"),
            bg="#87CEEB",
            fg="#4169E1"
        )
        title_label.pack(pady=(0, 20))
        
        # Full Name label and entry
        fullname_label = tk.Label(
            center_frame,
            text="Ονοματεπώνυμο:",
            font=("Arial", 11),
            bg="#87CEEB",
            fg="#333333"
        )
        fullname_label.pack(anchor=tk.W, padx=20, pady=(5, 0))
        
        self.fullname_entry = tk.Entry(
            center_frame,
            font=("Arial", 11),
            width=30
        )
        self.fullname_entry.pack(padx=20, pady=(0, 10))
        
        # Email label and entry
        email_label = tk.Label(
            center_frame,
            text="Email:",
            font=("Arial", 11),
            bg="#87CEEB",
            fg="#333333"
        )
        email_label.pack(anchor=tk.W, padx=20, pady=(5, 0))
        
        self.email_entry = tk.Entry(
            center_frame,
            font=("Arial", 11),
            width=30
        )
        self.email_entry.pack(padx=20, pady=(0, 10))
        
        # Mobile Phone label and entry
        phone_label = tk.Label(
            center_frame,
            text="Κινητό:",
            font=("Arial", 11),
            bg="#87CEEB",
            fg="#333333"
        )
        phone_label.pack(anchor=tk.W, padx=20, pady=(5, 0))
        
        self.phone_entry = tk.Entry(
            center_frame,
            font=("Arial", 11),
            width=30
        )
        self.phone_entry.pack(padx=20, pady=(0, 10))

        # Username label and entry
        username_label = tk.Label(
            center_frame,
            text="Όνομα Χρήστη:",
            font=("Arial", 11),
            bg="#87CEEB",
            fg="#333333"
        )
        username_label.pack(anchor=tk.W, padx=20, pady=(5, 0))
        
        self.username_entry = tk.Entry(
            center_frame,
            font=("Arial", 11),
            width=30
        )
        self.username_entry.pack(padx=20, pady=(0, 10))
        
        # Password label and entry
        password_label = tk.Label(
            center_frame,
            text="Κωδικός Πρόσβασης:",
            font=("Arial", 11),
            bg="#87CEEB",
            fg="#333333"
        )
        password_label.pack(anchor=tk.W, padx=20, pady=(5, 0))
        
        self.password_entry = tk.Entry(
            center_frame,
            font=("Arial", 11),
            width=30,
            show="*"
        )
        self.password_entry.pack(padx=20, pady=(0, 10))
        
        # Role label and combobox
        role_label = tk.Label(
            center_frame,
            text="Επιλογή Ρόλου:",
            font=("Arial", 11),
            bg="#87CEEB",
            fg="#333333"
        )
        role_label.pack(anchor=tk.W, padx=20, pady=(5, 0))
        
        self.role_var = tk.StringVar()
        self.role_combobox = ttk.Combobox(
            center_frame,
            textvariable=self.role_var,
            font=("Arial", 11),
            width=28,
            state="readonly"
        )
        self.role_combobox['values'] = ("Κτηνίατρος", "Ρεσεψιόν", "Ιδιοκτήτης Κατοικίδιου")
        self.role_combobox.current(0)  # Default value
        self.role_combobox.pack(padx=20, pady=(0, 20))
        
        # Register button
        register_btn = tk.Button(
            center_frame,
            text="Δημιουργία Λογαριασμού",
            font=("Arial", 12, "bold"),
            bg="#4DA6FF",
            fg="white",
            width=25,
            border=0,
            padx=10,
            pady=8,
            cursor="hand2",
            activebackground="#3D7FBF",
            command=self.register_user
        )
        register_btn.pack(pady=10)

    def get_db_path(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, '..', 'vetpro.db')

    def setup_database(self):
        try:
            conn = sqlite3.connect(self.get_db_path())
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fullname TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    phone TEXT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL
                )
            ''')
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Σφάλμα Βάσης Δεδομένων", f"Αποτυχία δημιουργίας βάσης: {e}")

    def register_user(self):
        fullname = self.fullname_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_var.get()

        if not fullname or not email or not username or not password or not role:
            messagebox.showwarning("Ελλιπή Στοιχεία", "Παρακαλώ συμπληρώστε όλα τα υποχρεωτικά πεδία (Ονοματεπώνυμο, Email, Όνομα Χρήστη, Κωδικός, Ρόλος).")
            return

        try:
            conn = sqlite3.connect(self.get_db_path())
            cursor = conn.cursor()
            
            # Ελέγχουμε αν υπάρχει ήδη ο χρήστης με το ίδιο username ή email
            cursor.execute("SELECT * FROM users WHERE username=? OR email=?", (username, email))
            existing_user = cursor.fetchone()
            
            if existing_user:
                messagebox.showerror("Σφάλμα Εγγραφής", "Το Όνομα Χρήστη ή το Email υπάρχει ήδη. Παρακαλώ επιλέξτε διαφορετικά.")
                conn.close()
                return

            cursor.execute('''
                INSERT INTO users (fullname, email, phone, username, password, role)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (fullname, email, phone, username, password, role))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Επιτυχία", "Η εγγραφή ολοκληρώθηκε με επιτυχία!")
            
            # Καθαρισμός πεδίων μετά από επιτυχή εγγραφή
            self.fullname_entry.delete(0, tk.END)
            self.email_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.role_combobox.current(0)
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Σφάλμα", "Υπήρξε πρόβλημα με την εγγραφή (πιθανώς διπλότυπη εγγραφή).")
        except sqlite3.Error as e:
            messagebox.showerror("Σφάλμα Βάσης Δεδομένων", f"Συνέβη ένα σφάλμα: {e}")


def main():
    root = tk.Tk()
    app = RegisterScreen(root)
    root.mainloop()


if __name__ == "__main__":
    main()
