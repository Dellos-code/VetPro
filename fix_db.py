import os
import subprocess

db_setup_path = 'database/db_setup.py'
db_path = 'vetpro.db'

print("🔧 Έναρξη Αυτόματης Επιδιόρθωσης Βάσης Δεδομένων...\n")

# 1. Διόρθωση του αρχείου db_setup.py
if os.path.exists(db_setup_path):
    with open(db_setup_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Η προβληματική εντολή SQL
    old_query = '"INSERT OR IGNORE INTO users (id,username,email,role,phone,password) VALUES (?,?,?,?,?,?)"'
    # Η σωστή εντολή SQL (με το fullname και το 7ο '?')
    new_query = '"INSERT OR IGNORE INTO users (id,username,email,role,fullname,phone,password) VALUES (?,?,?,?,?,?,?)"'

    if old_query in content:
        content = content.replace(old_query, new_query)
        with open(db_setup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ ΒΗΜΑ 1: Το database/db_setup.py διορθώθηκε!")
    else:
        print("⚠️ ΒΗΜΑ 1: Η παλιά γραμμή δεν βρέθηκε (ίσως είναι ήδη διορθωμένη).")
else:
    print(f"❌ Δεν βρέθηκε το αρχείο {db_setup_path}")

# 2. Διαγραφή της παλιάς (κατεστραμμένης) βάσης
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"✅ ΒΗΜΑ 2: Η παλιά βάση ({db_path}) διαγράφηκε επιτυχώς!")
else:
    print(f"ℹ️ ΒΗΜΑ 2: Η βάση {db_path} δεν υπήρχε, προχωράμε.")

# 3. Δημιουργία νέας βάσης
print("⏳ ΒΗΜΑ 3: Δημιουργία νέας, σωστής βάσης δεδομένων...")
subprocess.run(["python3", db_setup_path])
print("✅ Η νέα βάση δημιουργήθηκε γεμάτη με δεδομένα!\n")

# 4. Εκτέλεση εντολών Git (Η Δικτατορία)
print("⏳ ΒΗΜΑ 4: Ανέβασμα των αλλαγών στο GitHub...")
commands = [
    ["git", "checkout", "-b", "fix-db-seeding"],
    ["git", "add", db_setup_path],
    ["git", "commit", "-m", "Fix SQL Insert missing fullname column crashing db creation"],
    ["git", "push", "origin", "fix-db-seeding"]
]

for cmd in commands:
    print(f"Εκτέλεση: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"\n❌ Σφάλμα κατά την εκτέλεση του Git.")
        print("🔑 Αν σου ζητήσει κωδικό, θυμήσου να βάλεις το **νέο Token (PAT)** που φτιάξαμε νωρίτερα!")
        break
else:
    print("\n🎉 ΟΛΑ ΕΤΟΙΜΑ! Το script ολοκληρώθηκε με απόλυτη επιτυχία.")
    print("👉 Τώρα μπες στο GitHub, κάνε 'Compare & pull request' και πάτα 'Merge'!")
