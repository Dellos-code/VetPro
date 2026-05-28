import unittest
import sys
import os

# Προσθήκη του γονικού καταλόγου στο path για να μπορούμε να κάνουμε import το prescription_sequence
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from prescription_sequence import DrugCatalog, TempList

class TestPrescriptionQuantity(unittest.TestCase):
    """
    Έλεγχος Αδιαφανούς Κουτιού (Black-Box Testing)
    Τεχνική: Διαμέριση σε Κλάσεις Ισοδυναμίας & Ανάλυση Οριακών Τιμών
    Μεταβλητή ελέγχου: Ποσότητα (quantity) φαρμάκου στη φόρμα συνταγογράφησης.
    Προδιαγραφές: Η ποσότητα πρέπει να είναι ακέραιος από 1 έως 100 τεμάχια.
    
    Κλάσεις Ισοδυναμίας:
    - Κλάση 1 (Άκυρη): quantity < 1
    - Κλάση 2 (Έγκυρη): 1 <= quantity <= 100
    - Κλάση 3 (Άκυρη): quantity > 100
    """

    def validate_quantity(self, quantity):
        """
        Εξομοίωση της μεθόδου επικύρωσης (validation) που ελέγχει 
        την ποσότητα πριν μπει στην προσωρινή λίστα (TempList).
        """
        if not isinstance(quantity, int):
            raise TypeError("Η ποσότητα πρέπει να είναι ακέραιος αριθμός.")
        if quantity < 1 or quantity > 100:
            raise ValueError("Μη αποδεκτή ποσότητα. Πρέπει να είναι μεταξύ 1 και 100.")
        return True

    def test_tc_01_lower_boundary_invalid(self):
        # TC-01: quantity = 0 (Οριακή τιμή κάτω ορίου - Άκυρη)
        with self.assertRaises(ValueError):
            self.validate_quantity(0)

    def test_tc_02_lower_boundary_valid(self):
        # TC-02: quantity = 1 (Οριακή τιμή κάτω ορίου - Έγκυρη)
        self.assertTrue(self.validate_quantity(1))

    def test_tc_03_upper_boundary_valid(self):
        # TC-03: quantity = 100 (Οριακή τιμή άνω ορίου - Έγκυρη)
        self.assertTrue(self.validate_quantity(100))

    def test_tc_04_upper_boundary_invalid(self):
        # TC-04: quantity = 101 (Οριακή τιμή άνω ορίου - Άκυρη)
        with self.assertRaises(ValueError):
            self.validate_quantity(101)

    def test_tc_05_extreme_negative(self):
        # TC-05: quantity = -5 (Ακραία αρνητική τιμή - Άκυρη)
        with self.assertRaises(ValueError):
            self.validate_quantity(-5)


class TestDrugCatalog(unittest.TestCase):
    """
    Έλεγχος Διαφανούς Κουτιού (White-Box Testing)
    Λογική εύρεσης φαρμάκου: Ανάλογα με την ύπαρξη ή όχι του φαρμάκου στον κατάλογο.
    """
    def setUp(self):
        self.catalog = DrugCatalog()

    def test_drug_found_exact_match(self):
        # Σενάριο: Το φάρμακο υπάρχει με ακριβώς το ίδιο όνομα (Κάλυψη επιτυχίας)
        drug = self.catalog.findDrug("Amoxil")
        self.assertIsNotNone(drug)
        self.assertEqual(drug["name"], "Amoxil")

    def test_drug_found_case_insensitive(self):
        # Σενάριο: Το φάρμακο υπάρχει, αλλά δίνεται με πεζά/κεφαλαία ανακατεμένα
        drug = self.catalog.findDrug("aMoXiL")
        self.assertIsNotNone(drug)
        self.assertEqual(drug["name"], "Amoxil")

    def test_drug_not_found(self):
        # Σενάριο: Το φάρμακο ΔΕΝ υπάρχει (Κάλυψη αποτυχίας)
        drug = self.catalog.findDrug("Panadol")
        self.assertIsNone(drug)

if __name__ == '__main__':
    unittest.main()
