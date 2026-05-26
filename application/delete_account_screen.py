import tkinter as tk
from tkinter import messagebox
import sqlite3
import os

class DeleteAccountScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("VetPro - Διαγραφή Λογαριασμού")
        self.root.geometry("400x350")
        self.root.configure(bg="#FFCCCC")
        
        # Center frame
        center_frame = tk.Frame(root, bg="#FFCCCC")
        center_frame.pack(expand=True)
        
        # Logo or Title
        title_label = tk.Label(
            center_frame,
            text="⚠️ Διαγραφή",
            font=("Arial", 24, "bold"),
            bg="#FFCCCC",
            fg="#CC0000"
        )
        title_label.pack(pady=(0, 20))
        
        # Username label and entry
        username_label = tk.Label(
            center_frame,
            text="Όνομα Χρήστη:",
            font=("Arial", 11),
            bg="#FFCCCC",
            fg="#333333"
        )
        username_label.pack(anchor=tk.W, padx=20, pady=(5, 0))
        
        self.username_entry = tk.Entry(
            center_frame,
            font=("Arial", 11),
            width=25
        )
        self.username_entry.pack(padx=20, pady=(0, 10))
        
        # Password label and entry
        password_label = tk.Label(
            center_frame,
            text="Κωδικός Πρόσβασης:",
            font=("Arial", 11),
            bg="#FFCCCC",
            fg="#333333"
        )
        password_label.pack(anchor=tk.W, padx=20, pady=(5, 0))
        
        self.password_entry = tk.Entry(
            center_frame,
            font=("Arial", 11),
            width=25,
            show="*"
        )
        self.password_entry.pack(padx=20, pady=(0, 20))
        
        # Delete button
        delete_btn = tk.Button(
            center_frame,
            text="Οριστική Διαγραφή",
            font=("Arial", 12, "bold"),
            bg="#CC0000",
            fg="white",
            width=25,
            border=0,
            padx=10,
            pady=8,
            cursor="hand2",
            activebackground="#990000",
            command=self.delete_account
        )
        delete_btn.pack(pady=10)

    def get_db_path(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, 'vetpro.db')

    def delete_account(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Ελλιπή Στοιχεία", "Παρακαλώ συμπληρώστε Όνομα Χρήστη και Κωδικό Πρόσβασης.")
            return
            
        # Confirm deletion
        confirm = messagebox.askyesno("Επιβεβαίωση", "Είστε σίγουροι ότι θέλετε να διαγράψετε οριστικά τον λογαριασμό σας;")
        if not confirm:
            return

        try:
            conn = sqlite3.connect(self.get_db_path())
            cursor = conn.cursor()
            
            # Check if user exists with those credentials
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = cursor.fetchone()
            
            if user:
                cursor.execute("DELETE FROM users WHERE username=? AND password=?", (username, password))
                conn.commit()
                messagebox.showinfo("Επιτυχία", "Ο λογαριασμός διαγράφηκε επιτυχώς.")
                self.root.destroy()
            else:
                messagebox.showerror("Λάθος Στοιχεία", "Το Όνομα Χρήστη ή ο Κωδικός Πρόσβασης είναι λάθος.")
                
            conn.close()
                
        except sqlite3.Error as e:
            messagebox.showerror("Σφάλμα Βάσης Δεδομένων", f"Συνέβη ένα σφάλμα: {e}")

def main():
    root = tk.Tk()
    app = DeleteAccountScreen(root)
    root.mainloop()

if __name__ == "__main__":
    main()
