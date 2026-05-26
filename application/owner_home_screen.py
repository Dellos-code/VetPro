import tkinter as tk
from tkinter import font as tkfont

class OwnerHomeScreen:
    def __init__(self, root, fullname=""):
        self.root = root
        self.root.title("VetPro - Αρχική Ιδιοκτήτη")
        self.root.geometry("850x500")
        self.root.configure(bg="#D3D3D3")
        
        # --- Sidebar ---
        self.sidebar_frame = tk.Frame(self.root, bg="#87CEEB", width=250)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False) # Don't shrink
        
        # Logo
        logo_font = tkfont.Font(family="Comic Sans MS", size=24, weight="bold")
        self.logo_label = tk.Label(
            self.sidebar_frame, 
            text="🐾 VetPro", 
            font=logo_font, 
            bg="#87CEEB", 
            fg="#9932CC" # Purple color
        )
        self.logo_label.pack(pady=(20, 30))
        
        # Sidebar Buttons
        buttons_data = [
            "Αρχικη",
            "Το Προφιλ μου",
            "Κλεισιμο Ραντεβου",
            "Πληρωμη/ Χρεωση",
            "Ειδοποιησεις",
            "Ιστορικο Ζωου"
        ]
        
        for btn_text in buttons_data:
            btn = tk.Button(
                self.sidebar_frame,
                text=btn_text,
                font=("Arial", 10, "bold"),
                bg="#87CEEB",
                fg="#333333",
                anchor="w",
                padx=20,
                pady=5,
                bd=1,
                relief="solid",
                cursor="hand2"
            )
            btn.pack(fill="x", padx=10, pady=2)

        # --- Main Content Area ---
        self.main_frame = tk.Frame(self.root, bg="#D3D3D3")
        self.main_frame.pack(side="left", fill="both", expand=True)
        
        # Greeting text
        greeting_font = tkfont.Font(family="Consolas", size=14, weight="bold")
        greeting_text = f"Γεια σου, {fullname}" if fullname else "Γεια σου, <name>"
        self.greeting_label = tk.Label(
            self.main_frame,
            text=greeting_text,
            font=greeting_font,
            bg="#D3D3D3",
            fg="black"
        )
        self.greeting_label.place(x=20, y=20)
        
        # Dog Image placeholder middle left
        self.dog_label = tk.Label(
            self.main_frame,
            text="🐶",
            font=("Arial", 60),
            bg="#D3D3D3"
        )
        self.dog_label.place(x=0, y=200)

        # --- Info Boxes ---
        # Box 1: My Pet
        self.create_info_box(
            x=150, y=80, 
            bg_color="#87CEEB", # Light blue
            outline_color="#4169E1", # Royal Blue
            title="Το Κατοικιδιο μου,",
            info_text="<pet's name>, <pet>",
            info_color="#4169E1"
        )
        
        # Box 2: Next Appointment
        self.create_info_box(
            x=380, y=80, 
            bg_color="#9ACD32", # Yellow-Green
            outline_color="#32CD32", # LimeGreen
            title="Επομενο Ραντεβου",
            info_text="24 Απριλιου - Ελεγχος",
            info_color="#32CD32"
        )
        
        # Box 3: Next Vaccination
        self.create_info_box(
            x=150, y=240, 
            bg_color="#FFD700", # Gold/Yellow
            outline_color="#DAA520", # Goldenrod
            title="Επομενο Εμβολιο",
            info_text="20 Μαιου",
            info_color="#DAA520"
        )
        
        # Box 4: Notifications
        self.create_info_box(
            x=380, y=240, 
            bg_color="#DC143C", # Crimson
            outline_color="#8B0000", # Dark Red
            title="Ειδοποιησεις",
            info_text="3 Νεα Μηνυματα",
            info_color="#8B0000"
        )
        
        # Cat Image placeholder bottom right
        self.cat_label = tk.Label(
            self.main_frame,
            text="🐱",
            font=("Arial", 60),
            bg="#D3D3D3"
        )
        self.cat_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)


    def create_info_box(self, x, y, bg_color, outline_color, title, info_text, info_color):
        canvas = tk.Canvas(self.main_frame, width=200, height=120, bg="#D3D3D3", highlightthickness=0)
        canvas.place(x=x, y=y)
        
        # Draw rounded rectangle (simulated with standard shapes)
        r = 20 # radius
        w = 200
        h = 120
        
        # Create arcs for corners
        canvas.create_arc(0, 0, r*2, r*2, start=90, extent=90, fill=bg_color, outline=outline_color, width=3)
        canvas.create_arc(w-r*2, 0, w, r*2, start=0, extent=90, fill=bg_color, outline=outline_color, width=3)
        canvas.create_arc(0, h-r*2, r*2, h, start=180, extent=90, fill=bg_color, outline=outline_color, width=3)
        canvas.create_arc(w-r*2, h-r*2, w, h, start=270, extent=90, fill=bg_color, outline=outline_color, width=3)
        
        # Create rectangles to fill the rest
        canvas.create_rectangle(r, 0, w-r, h, fill=bg_color, outline="")
        canvas.create_rectangle(0, r, w, h-r, fill=bg_color, outline="")
        
        # Draw borders
        canvas.create_line(r, 0, w-r, 0, fill=outline_color, width=3) # top
        canvas.create_line(r, h, w-r, h, fill=outline_color, width=3) # bottom
        canvas.create_line(0, r, 0, h-r, fill=outline_color, width=3) # left
        canvas.create_line(w, r, w, h-r, fill=outline_color, width=3) # right
        
        # Text
        canvas.create_text(15, 15, text=title, anchor="nw", font=("Consolas", 10, "bold"), fill="black")
        canvas.create_text(185, 105, text=info_text, anchor="se", font=("Consolas", 10, "bold"), fill=info_color)


def main():
    root = tk.Tk()
    app = OwnerHomeScreen(root)
    root.mainloop()

if __name__ == "__main__":
    main()
