import unittest
import sys
import os
from datetime import datetime

# Προσθήκη του γονικού καταλόγου στο path για να μπορούμε να κάνουμε import το report_sequence
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from report_sequence import MedHistory

class TestReportDateFilters(unittest.TestCase):
    """
    Έλεγχος Αδιαφανούς Κουτιού (Black-Box Testing)
    Τεχνική: Διαμέριση σε Κλάσεις Ισοδυναμίας
    Μεταβλητές ελέγχου: from_date, to_date (στο FilterForm)
    Προδιαγραφές: Η ημερομηνία 'from_date' πρέπει να είναι προγενέστερη ή ίδια με την 'to_date'.
    
    Κλάσεις Ισοδυναμίας:
    - Κλάση 1 (Έγκυρη): from_date < to_date
    - Κλάση 2 (Έγκυρη): from_date == to_date
    - Κλάση 3 (Άκυρη): from_date > to_date
    """

    def validate_date_range(self, from_date_str, to_date_str):
        """
        Εξομοίωση της επικύρωσης των φίλτρων ημερομηνίας που
        πληκτρολογεί ο κτηνίατρος για την παραγωγή αναφοράς.
        """
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d")
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d")
        
        if from_date > to_date:
            raise ValueError("Η αρχική ημερομηνία (from_date) δεν μπορεί να είναι μεταγενέστερη της τελικής (to_date).")
        return True

    def test_tc_01_valid_range(self):
        # TC-01: from_date < to_date (Έγκυρο διάστημα)
        self.assertTrue(self.validate_date_range("2023-01-01", "2023-12-31"))

    def test_tc_02_same_date(self):
        # TC-02: from_date == to_date (Οριακή έγκυρη τιμή - 1 ημέρα μόνο)
        self.assertTrue(self.validate_date_range("2023-05-15", "2023-05-15"))

    def test_tc_03_invalid_range(self):
        # TC-03: from_date > to_date (Άκυρο διάστημα)
        with self.assertRaises(ValueError):
            self.validate_date_range("2023-12-31", "2023-01-01")


class TestMedHistory(unittest.TestCase):
    """
    Έλεγχος Διαφανούς Κουτιού - Condition Coverage
    Ελέγχει αν το σύστημα επιστρέφει δεδομένα ή None.
    """
    def setUp(self):
        self.history = MedHistory()

    def test_retrieve_data_empty(self):
        # Σενάριο: Απουσία Εγγραφών (Εναλλακτική Ροή 1)
        # Βάσει του κώδικα, αν from_date == "empty", επιστρέφει None.
        result = self.history.retrieveData("empty", "2023-12-31")
        self.assertIsNone(result)

    def test_retrieve_data_found(self):
        # Σενάριο: Εύρεση Εγγραφών (Βασική Ροή)
        result = self.history.retrieveData("2023-01-01", "2023-12-31")
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)  # Επιστρέφει προκαθορισμένη λίστα με 2 εγγραφές

if __name__ == '__main__':
    unittest.main()
