import os
import subprocess
import sys

def print_status(message, success=True):
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")

def check_architecture():
    print("\n--- 🔍 VETPRO ARCHITECTURAL STEALTH CHECKER ---\n")
    all_good = True

    # 1. Check if files exist in the right place
    files_to_check = [
        'logic/appointment_service.py',
        'logic/inventory_manager.py',
        'test-cases/test_uc9.py',
        'test-cases/test_uc10.py'
    ]
    
    print("📂 Ελέγχοντας τη δομή αρχείων...")
    for f in files_to_check:
        if os.path.exists(f):
            print_status(f"Το αρχείο {f} βρέθηκε.")
        else:
            print_status(f"Το αρχείο {f} ΑΓΝΟΕΙΤΑΙ. Δημιούργησέ το!", False)
            all_good = False

    if not all_good:
        print("\n⚠️ ΔΙΟΡΘΩΣΕ ΤΑ ΑΡΧΕΙΑ ΚΑΙ ΞΑΝΑΤΡΕΞΕ ΤΟ SCRIPT.")
        return False

    # 2. Run Unit Tests via Subprocess (Bypasses the hyphen issue in 'test-cases' folder name)
    print("\n🧪 Τρέχοντας τα Unit Tests των UC9 & UC10 στο παρασκήνιο...")
    
    tests = ['test-cases/test_uc9.py', 'test-cases/test_uc10.py']
    
    for test_file in tests:
        print(f"  Εκτέλεση {test_file}...")
        # Τρέχουμε το κάθε test σαν ανεξάρτητο process
        result = subprocess.run([sys.executable, '-m', 'unittest', test_file], capture_output=True, text=True)
        
        if result.returncode == 0:
             print_status(f"Το test {test_file} πέρασε επιτυχώς!")
        else:
             print_status(f"Το test {test_file} ΑΠΕΤΥΧΕ.", False)
             print("Λεπτομέρειες Σφάλματος:\n" + result.stderr)
             all_good = False

    return all_good

if __name__ == "__main__":
    success = check_architecture()
    if success:
        print("\n🚀 ΟΛΑ ΤΡΕΧΟΥΝ ΡΟΛΟΪ. ΕΙΣΑΙ ΕΤΟΙΜΟΣ ΓΙΑ GIT PUSH!")
    else:
        print("\n🛑 ΜΗΝ ΚΑΝΕΙΣ PUSH ΑΚΟΜΑ. Διόρθωσε τα σφάλματα.") 
