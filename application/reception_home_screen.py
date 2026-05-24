import tkinter as tk
from tkinter import font as tkfont

class ReceptionHomeScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("VetPro - Αρχική Ρεσεψιόν")
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
            "Κλεισιμο Ραντεβου",
            "Ειδοποιησεις",
            "Πληρωμη/ Χρεωση",
            "Αναφορες"
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
        
        # Title
        title_font = tkfont.Font(family="Comic Sans MS", size=32, weight="bold")
        self.title_label = tk.Label(
            self.main_frame,
            text="Αρχική",
            font=title_font,
            bg="#D3D3D3",
            fg="black"
        )
        self.title_label.place(x=20, y=20)
        
        # Subtitle and Dog Emoji
        self.subtitle_label = tk.Label(
            self.main_frame,
            text="Καλως ηρθατε στο VetPro 🐶",
            font=("Arial", 12, "bold"),
            bg="#D3D3D3",
            fg="black"
        )
        self.subtitle_label.place(x=20, y=100)
        
        # --- Info Boxes ---
        boxes_y = 150
        
        # Box 1: Appointments of the Day
        self.create_info_box(
            x=150, y=boxes_y, 
            bg_color="#9ACD32", # Yellow-Green
            title="Ραντεβου\nτης Ημερας",
            count="12",
            count_color="#0000FF"
        )
        
        # Box 2: Pending Payments
        self.create_info_box(
            x=320, y=boxes_y, 
            bg_color="#6495ED", # Cornflower Blue
            title="Εκκρεμεις\nΠληρωμες",
            count="5",
            count_color="#0000FF"
        )
        
        # Box 3: Notifications to send
        self.create_info_box(
            x=490, y=boxes_y, 
            bg_color="#DC143C", # Crimson Red
            title="Ειδοποιησεις\nπρος Αποστολη",
            count="4",
            count_color="black"
        )
        
        # Cat Image placeholder bottom right
        self.cat_label = tk.Label(
            self.main_frame,
            text="🐱",
            font=("Arial", 60),
            bg="#D3D3D3"
        )
        self.cat_label.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)


    def create_info_box(self, x, y, bg_color, title, count, count_color):
        # We use a Canvas to draw a rounded rectangle
        canvas = tk.Canvas(self.main_frame, width=150, height=80, bg="#D3D3D3", highlightthickness=0)
        canvas.place(x=x, y=y)
        
        # Draw rounded rectangle (simulated with standard shapes)
        r = 15 # radius
        w = 150
        h = 80
        
        # Create arcs for corners
        canvas.create_arc(0, 0, r*2, r*2, start=90, extent=90, fill=bg_color, outline=bg_color)
        canvas.create_arc(w-r*2, 0, w, r*2, start=0, extent=90, fill=bg_color, outline=bg_color)
        canvas.create_arc(0, h-r*2, r*2, h, start=180, extent=90, fill=bg_color, outline=bg_color)
        canvas.create_arc(w-r*2, h-r*2, w, h, start=270, extent=90, fill=bg_color, outline=bg_color)
        
        # Create rectangles to fill the rest
        canvas.create_rectangle(r, 0, w-r, h, fill=bg_color, outline=bg_color)
        canvas.create_rectangle(0, r, w, h-r, fill=bg_color, outline=bg_color)
        
        # Add outline (optional, to match image exactly we can draw a thicker line)
        border_color = "black" if bg_color == "#DC143C" else ("blue" if bg_color == "#6495ED" else "green")
        # Just simple text inside canvas
        
        canvas.create_text(10, 10, text=title, anchor="nw", font=("Arial", 10, "bold"), fill="black")
        canvas.create_text(140, 70, text=count, anchor="se", font=("Arial", 12, "bold"), fill=count_color)


def main():
    root = tk.Tk()
    app = ReceptionHomeScreen(root)
    root.mainloop()

if __name__ == "__main__":
    main()
