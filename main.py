"""
VetPro - Main Entry Point
Εκκινεί την εφαρμογή, δημιουργεί τη βάση και ανοίγει το login.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_setup import setup_database, seed_demo_data
import tkinter as tk
from screens.login_screen import LoginScreen

def main():
    setup_database()
    seed_demo_data()

    root = tk.Tk()
    root.resizable(True, True)
    LoginScreen(root)
    root.mainloop()

if __name__ == "__main__":
    main()
