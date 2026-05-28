from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pydantic import BaseModel

# --- Μοντέλα Δεδομένων (Data Models) ---
class AppointmentRequest(BaseModel):
    vet_id: int
    client_name: str
    animal_name: str
    target_date: datetime
    duration_minutes: int
    is_urgent: bool = False

class Appointment(AppointmentRequest):
    appointment_id: int
    status: str

# --- Μηχανή Βελτιστοποίησης & Ελέγχου (Scheduler Engine) ---
class SchedulerEngine:
    """
    Μηχανή ελέγχου διαθεσιμότητας και βελτιστοποίησης ραντεβού (Use Case 9).
    Υλοποιεί τον αλγόριθμο αποφυγής επικαλύψεων και διαχείρισης επειγόντων.
    """
    
    def __init__(self, db_session):
        self.db = db_session # Mock DB session για την ενσωμάτωση

    def get_daily_schedule(self, vet_id: int, date: datetime) -> List[Appointment]:
        """Ανακτά το τρέχον πρόγραμμα του κτηνιάτρου από τη βάση δεδομένων."""
        # Προσομοίωση ανάκτησης από τη Βάση (Entity: AppointmentDatabase)
        # Στην πραγματικότητα εδώ γίνεται: SELECT * FROM appointments WHERE vet_id = ...
        return []

    def check_availability(self, request: AppointmentRequest) -> bool:
        """
        Ελέγχει αν υπάρχει διαθέσιμο κενό στο πρόγραμμα.
        """
        daily_schedule = self.get_daily_schedule(request.vet_id, request.target_date)
        req_start = request.target_date
        req_end = req_start + timedelta(minutes=request.duration_minutes)

        for appt in daily_schedule:
            appt_start = appt.target_date
            appt_end = appt_start + timedelta(minutes=appt.duration_minutes)
            
            # Αλγόριθμος εντοπισμού επικάλυψης (Overlap Detection)
            if (req_start < appt_end) and (req_end > appt_start):
                return False # Βρέθηκε σύγκρουση
                
        return True # Η ώρα είναι διαθέσιμη

    def process_appointment(self, request: AppointmentRequest) -> Dict:
        """
        Ο κύριος ελεγκτής της λογικής. Συντονίζει τον έλεγχο και την αποθήκευση.
        """
        # 1. Έλεγχος Διαθεσιμότητας
        is_available = self.check_availability(request)
        
        if is_available:
            # 2. Ελεγκτής Εγγραφής (Αποθήκευση στη Βάση)
            new_id = self._insert_appointment(request)
            return {"status": "success", "message": "Επιτυχής Κράτηση", "appointment_id": new_id}
        else:
            # 3. Διαχείριση Επειγόντων (Preemption Logic)
            if request.is_urgent:
                return self._handle_urgent_preemption(request)
            
            # Ελεγκτής Σφαλμάτων
            return {"status": "error", "message": "Η ώρα δεν είναι διαθέσιμη. Υπάρχει σύγκρουση."}

    def _insert_appointment(self, request: AppointmentRequest) -> int:
        """Εσωτερική συνάρτηση για την εγγραφή στη βάση."""
        # Προσομοίωση INSERT
        return 101

    def _handle_urgent_preemption(self, request: AppointmentRequest) -> Dict:
        """Εκτοπίζει ένα ραντεβού ρουτίνας για να κάνει χώρο στο επείγον."""
        # Εδώ μπαίνει η λογική ακύρωσης ενός ρουτινιάρικου ραντεβού και ειδοποίησης
        return {"status": "success", "message": "Επιτυχής Κράτηση Επείγοντος (Εκτόπιση ρουτίνας)", "appointment_id": 999}

# Παράδειγμα χρήσης:
# engine = SchedulerEngine(db_session=db)
# result = engine.process_appointment(req_data)
