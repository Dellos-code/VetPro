import os

def bypass_seed():
    main_file = 'main.py'
    
    if not os.path.exists(main_file):
        print(f"❌ Δεν βρέθηκε το {main_file}")
        return

    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.readlines()

    # Ψάχνουμε για το seed_demo_data() και το σχολιάζουμε
    changed = False
    for i, line in enumerate(content):
        if 'seed_demo_data()' in line and not line.strip().startswith('#'):
            content[i] = line.replace('seed_demo_data()', '# seed_demo_data()  # Bypassed to avoid schema errors')
            changed = True

    if changed:
        with open(main_file, 'w', encoding='utf-8') as f:
            f.writelines(content)
        print("✅ Το seed_demo_data() απενεργοποιήθηκε επιτυχώς στο main.py.")
    else:
        print("⚠️ Το seed_demo_data() είναι ήδη απενεργοποιημένο ή δεν βρέθηκε.")

    # Διαγράφουμε την παλιά βάση αν υπάρχει, για να δημιουργηθούν καθαρά τα tables
    db_file = 'vetpro.db'
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"🗑️ Διαγράφηκε η παλιά βάση ({db_file}). Θα δημιουργηθούν νέα άδεια tables στο επόμενο τρέξιμο.")
        except Exception as e:
            print(f"⚠️ Δεν ήταν δυνατή η διαγραφή της βάσης: {e}")

if __name__ == "__main__":
    print("--- 🛠️ VETPRO BYPASS DB ERROR ---\n")
    bypass_seed()
    print("\n🚀 Ολοκληρώθηκε! Τρέξε τώρα: python3 main.py")
