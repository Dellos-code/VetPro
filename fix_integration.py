import os

vet_screen = 'screens/vet_screen.py'
inv_manager = 'logic/inventory_manager.py'

# 1. Ενημέρωση του Frontend (Οθόνη Κτηνιάτρου)
if os.path.exists(vet_screen):
    with open(vet_screen, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Αλλαγή των παλιών μεθόδων στις νέες του Controller
    content = content.replace('.decreaseStock(', '.submitPrescriptionRequest(')
    content = content.replace('.updateStock(', '.submitReplenishRequest(')
    # Ενημέρωση του import του PredictController (πρώην ForecastEngine)
    content = content.replace('ForecastEngine', 'PredictController')
    
    with open(vet_screen, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Το vet_screen.py διορθώθηκε επιτυχώς!")

# 2. Προσθήκη της λογικής Αναπλήρωσης (UC10) στο Backend αν λείπει
if os.path.exists(inv_manager):
    with open(inv_manager, 'r', encoding='utf-8') as f:
        inv_content = f.read()
        
    if 'def submitReplenishRequest' not in inv_content:
        new_method = """
    def submitReplenishRequest(self, item_name, qty):
        from database.db_setup import get_connection
        conn = get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE inventory SET quantity = quantity + ? WHERE item_name = ?", (qty, item_name))
            conn.commit()
            return True
        except Exception as e:
            print(f"DB Error: {e}")
            return False
        finally:
            conn.close()
"""
        with open(inv_manager, 'a', encoding='utf-8') as f:
            f.write(new_method)
        print("✅ Η μέθοδος αναπλήρωσης αποθέματος προστέθηκε στον Controller!")
