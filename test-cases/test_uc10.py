import unittest
from unittest.mock import patch, MagicMock
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from logic.inventory_manager import InventoryRequestController

class TestUC10InventoryManagement(unittest.TestCase):
    def setUp(self):
        self.req_ctrl = InventoryRequestController()

    @patch('logic.inventory_manager.get_connection')
    def test_basic_flow_sufficient_stock(self, mock_db_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (15,)  # Stock is 15
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value = mock_conn

        result = self.req_ctrl.submitPrescriptionRequest("Bravecto", 5)
        self.assertTrue(result)
        mock_conn.commit.assert_called_once()

    @patch('logic.inventory_manager.get_connection')
    def test_alt_flow_insufficient_stock(self, mock_db_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (2,)  # Stock is only 2
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value = mock_conn

        with self.assertRaises(ValueError) as context:
            self.req_ctrl.submitPrescriptionRequest("Bravecto", 5)
        self.assertTrue("Σφάλμα: Αρνητικό Απόθεμα!" in str(context.exception))

if __name__ == '__main__':
    unittest.main()
