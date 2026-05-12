import tkinter as tk

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("VetPro - Login")
        self.root.geometry("400x300")
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
            activebackground="#3D7FBF"
        )
        login_btn.pack(pady=10)


def main():
    root = tk.Tk()
    app = LoginScreen(root)
    root.mainloop()


if __name__ == "__main__":
    main()
