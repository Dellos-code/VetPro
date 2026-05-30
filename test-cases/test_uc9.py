import unittest
from unittest.mock import patch, MagicMock
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from logic.appointment_service import AppointmentRequestController

class TestUC9AppointmentBooking(unittest.TestCase):
    def setUp(self):
        self.req_ctrl = AppointmentRequestController()

    @patch('logic.appointment_service.get_connection')
    def test_basic_flow_success(self, mock_db_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # No conflict
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value = mock_conn

        result = self.req_ctrl.submitAppointment(1, 2, '2026-06-15', '10:30', 'Εμβόλιο')
        self.assertTrue(result)
        mock_conn.commit.assert_called_once()

    @patch('logic.appointment_service.get_connection')
    def test_alt_flow_conflict(self, mock_db_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (99,)  # Conflict exists
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value = mock_conn

        result = self.req_ctrl.submitAppointment(1, 2, '2026-06-15', '10:30', 'Εμβόλιο')
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
