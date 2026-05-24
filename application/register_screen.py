import tkinter as tk
from tkinter import ttk

class RegisterScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("VetPro - Εγγραφή Νέου Χρήστη")
        self.root.geometry("450x680")
        self.root.configure(bg="#87CEEB")
        
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
        
        # Register button (Non-functional as requested)
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
            activebackground="#3D7FBF"
        )
        register_btn.pack(pady=10)


def main():
    root = tk.Tk()
    app = RegisterScreen(root)
    root.mainloop()


if __name__ == "__main__":
    main()
