"""
VetPro - Database Setup
Βασισμένο στο Class Diagram v1.0
"""
import sqlite3
import os
from datetime import date, timedelta

DB_NAME = "vetpro.db"

def get_db_path():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, DB_NAME)

def get_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def setup_database():
    conn = get_connection()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id                   TEXT PRIMARY KEY,
            username             TEXT NOT NULL UNIQUE,
            email                TEXT NOT NULL UNIQUE,
            role                 TEXT NOT NULL,
            fullname             TEXT NOT NULL,
            phone                TEXT,
            password             TEXT NOT NULL,
            notifications_enabled INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS owners (
            user_id      TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
            phone_number TEXT,
            address      TEXT,
            debt_amount  REAL DEFAULT 0.0
        );
        CREATE TABLE IF NOT EXISTS veterinarians (
            user_id   TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
            specialty TEXT
        );
        CREATE TABLE IF NOT EXISTS receptionists (
            user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS administrators (
            user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS animals (
            id       TEXT PRIMARY KEY,
            name     TEXT NOT NULL,
            species  TEXT NOT NULL,
            breed    TEXT,
            age      INTEGER,
            weight   REAL,
            owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS pet_documents (
            id            TEXT PRIMARY KEY,
            document_type TEXT,
            file_path     TEXT,
            is_approved   INTEGER DEFAULT 0,
            animal_id     TEXT NOT NULL REFERENCES animals(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS medical_records (
            id          TEXT PRIMARY KEY,
            record_date TEXT NOT NULL,
            notes       TEXT,
            record_type TEXT NOT NULL,
            animal_id   TEXT NOT NULL REFERENCES animals(id) ON DELETE CASCADE,
            vet_id      TEXT REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS examinations (
            record_id TEXT PRIMARY KEY REFERENCES medical_records(id) ON DELETE CASCADE,
            diagnosis TEXT
        );
        CREATE TABLE IF NOT EXISTS vaccinations (
            record_id        TEXT PRIMARY KEY REFERENCES medical_records(id) ON DELETE CASCADE,
            vaccine_name     TEXT NOT NULL,
            batch_number     TEXT,
            next_due_date    TEXT,
            allergy_reaction INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS hospitalizations (
            id             TEXT PRIMARY KEY,
            admission_date TEXT NOT NULL,
            discharge_date TEXT,
            reason         TEXT,
            status         TEXT DEFAULT 'Active',
            animal_id      TEXT NOT NULL REFERENCES animals(id) ON DELETE CASCADE,
            vet_id         TEXT REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS daily_logs (
            id                 TEXT PRIMARY KEY,
            log_date           TEXT NOT NULL,
            temperature        REAL,
            weight             REAL,
            medication         TEXT,
            notes              TEXT,
            hospitalization_id TEXT NOT NULL REFERENCES hospitalizations(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS prescriptions (
            id          TEXT PRIMARY KEY,
            pres_date   TEXT NOT NULL,
            dosage      TEXT,
            quantity    INTEGER,
            animal_id   TEXT NOT NULL REFERENCES animals(id) ON DELETE CASCADE,
            vet_id      TEXT REFERENCES users(id),
            record_id   TEXT REFERENCES medical_records(id)
        );
        CREATE TABLE IF NOT EXISTS prescription_items (
            id              TEXT PRIMARY KEY,
            prescription_id TEXT NOT NULL REFERENCES prescriptions(id) ON DELETE CASCADE,
            medication_id   TEXT NOT NULL REFERENCES medications(id),
            quantity        INTEGER NOT NULL,
            dosage          TEXT
        );
        CREATE TABLE IF NOT EXISTS medications (
            id                TEXT PRIMARY KEY,
            name              TEXT NOT NULL UNIQUE,
            type              TEXT,
            active_ingredient TEXT,
            stock_level       INTEGER DEFAULT 0,
            min_threshold     INTEGER DEFAULT 5
        );
        CREATE TABLE IF NOT EXISTS appointments (
            id         TEXT PRIMARY KEY,
            appt_date  TEXT NOT NULL,
            time       TEXT NOT NULL,
            reason     TEXT,
            status     TEXT DEFAULT 'Scheduled',
            priority   INTEGER DEFAULT 1,
            animal_id  TEXT NOT NULL REFERENCES animals(id) ON DELETE CASCADE,
            vet_id     TEXT REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS payments (
            id             TEXT PRIMARY KEY,
            amount         REAL NOT NULL,
            method         TEXT,
            pay_date       TEXT NOT NULL,
            status         TEXT DEFAULT 'Pending',
            appointment_id TEXT REFERENCES appointments(id),
            owner_id       TEXT REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS reminders (
            id            TEXT PRIMARY KEY,
            send_date     TEXT NOT NULL,
            reminder_type TEXT,
            message       TEXT,
            status        TEXT DEFAULT 'Pending',
            owner_id      TEXT REFERENCES users(id),
            animal_id     TEXT REFERENCES animals(id)
        );
        CREATE TABLE IF NOT EXISTS notification_preferences (
            owner_id              TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
            notifications_enabled INTEGER DEFAULT 1,
            email_enabled         INTEGER DEFAULT 1,
            sms_enabled           INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS notification_error_log (
            id              TEXT PRIMARY KEY,
            notification_id TEXT,
            error_details   TEXT,
            timestamp       TEXT
        );
    """)
    conn.commit()
    conn.close()
    print("[DB] Schema created from Class Diagram v1.0")


def seed_demo_data():
    conn = get_connection()
    c = conn.cursor()

    # ── Ημερομηνίες ──────────────────────────────────────────────────────────
    today = date.today().isoformat()
    p1  = (date.today() - timedelta(days=15)).isoformat()
    p2  = (date.today() - timedelta(days=45)).isoformat()
    p3  = (date.today() - timedelta(days=90)).isoformat()
    p4  = (date.today() - timedelta(days=150)).isoformat()
    p5  = (date.today() - timedelta(days=210)).isoformat()
    p6  = (date.today() - timedelta(days=300)).isoformat()
    p7  = (date.today() - timedelta(days=400)).isoformat()
    t1  = (date.today() + timedelta(days=1)).isoformat()
    t2  = (date.today() + timedelta(days=2)).isoformat()
    t3  = (date.today() + timedelta(days=3)).isoformat()
    t4  = (date.today() + timedelta(days=4)).isoformat()
    t5  = (date.today() + timedelta(days=5)).isoformat()
    t7  = (date.today() + timedelta(days=7)).isoformat()
    t10 = (date.today() + timedelta(days=10)).isoformat()
    t14 = (date.today() + timedelta(days=14)).isoformat()
    ny  = (date.today() + timedelta(days=335)).isoformat()

    # ── ΧΡΗΣΤΕΣ ──────────────────────────────────────────────────────────────
    users = [
        # Κτηνίατροι
        ("vet-001","vet1",  "vet1@vetpro.gr",   "Κτηνίατρος",             "Γεράσιμος Γερόλυμος",      "6911111111","1234"),
        ("vet-002","vet2",  "vet2@vetpro.gr",   "Κτηνίατρος",             "Γεώργιος Κεπενός",         "6944444444","1234"),
        # Ρεσεψιόν
        ("rec-001","rec1",  "rec1@vetpro.gr",   "Ρεσεψιόν",               "Φωτεινή Μυλωνά",          "6922222222","1234"),
        # Ιδιοκτήτες — 15 άτομα
        ("own-001","owner1","owner1@vetpro.gr", "Ιδιοκτήτης Κατοικίδιου","Κωνσταντίνα Αναστοπούλου","6933333333","1234"),
        ("own-002","owner2","owner2@vetpro.gr", "Ιδιοκτήτης Κατοικίδιου","Ιωάννης Κωνσταντέλλος",   "6955555555","1234"),
        ("own-003","owner3","owner3@vetpro.gr", "Ιδιοκτήτης Κατοικίδιου","Μαρία Παπαδοπούλου",      "6966666666","1234"),
        ("own-004","owner4","owner4@vetpro.gr", "Ιδιοκτήτης Κατοικίδιου","Νίκος Αλεξόπουλος",       "6977777777","1234"),
        ("own-005","owner5","owner5@vetpro.gr", "Ιδιοκτήτης Κατοικίδιου","Ελένη Δημητρίου",         "6988888888","1234"),
        ("own-006","owner6","owner6@vetpro.gr", "Ιδιοκτήτης Κατοικίδιου","Χρήστος Οικονόμου",       "6911222333","1234"),
        ("own-007","owner7","owner7@vetpro.gr", "Ιδιοκτήτης Κατοικίδιου","Σοφία Παναγιωτοπούλου",   "6922333444","1234"),
        ("own-008","owner8","owner8@vetpro.gr", "Ιδιοκτήτης Κατοικίδιου","Δημήτρης Καραγιάννης",    "6933444555","1234"),
        ("own-009","owner9","owner9@vetpro.gr", "Ιδιοκτήτης Κατοικίδιου","Αγγελική Σταματοπούλου",  "6944555666","1234"),
        ("own-010","owner10","owner10@vetpro.gr","Ιδιοκτήτης Κατοικίδιου","Παναγιώτης Λαμπρόπουλος","6955666777","1234"),
        ("own-011","owner11","owner11@vetpro.gr","Ιδιοκτήτης Κατοικίδιου","Κατερίνα Νικολάου",      "6966777888","1234"),
        ("own-012","owner12","owner12@vetpro.gr","Ιδιοκτήτης Κατοικίδιου","Θανάσης Βασιλόπουλος",   "6977888999","1234"),
        ("own-013","owner13","owner13@vetpro.gr","Ιδιοκτήτης Κατοικίδιου","Ζωή Αθανασοπούλου",      "6988999000","1234"),
        ("own-014","owner14","owner14@vetpro.gr","Ιδιοκτήτης Κατοικίδιου","Κώστας Παπαγεωργίου",    "6999000111","1234"),
        ("own-015","owner15","owner15@vetpro.gr","Ιδιοκτήτης Κατοικίδιου","Ανδρέας Μαυρόπουλος",    "6900111222","1234"),
        # Διαχειριστής
        ("adm-001","admin1","admin@vetpro.gr",  "Διαχειριστής",           "Admin VetPro",             "6900000000","1234"),
    ]
    for row in users:
        c.execute("INSERT OR IGNORE INTO users (id,username,email,role,fullname,phone,password) VALUES (?,?,?,?,?,?,?)", row)

    # Owner extras
    owners_extra = [
        ("own-001","6933333333","Πάτρα, Αχαΐα",          0.0),
        ("own-002","6955555555","Ρίο, Αχαΐα",            30.0),
        ("own-003","6966666666","Αίγιο, Αχαΐα",           0.0),
        ("own-004","6977777777","Πάτρα, Αχαΐα",          15.0),
        ("own-005","6988888888","Κάτω Αχαΐα, Αχαΐα",      0.0),
        ("own-006","6911222333","Πάτρα, Αχαΐα",          50.0),
        ("own-007","6922333444","Παραλία, Πάτρα",          0.0),
        ("own-008","6933444555","Ρίο, Αχαΐα",             0.0),
        ("own-009","6944555666","Πάτρα, Αχαΐα",          20.0),
        ("own-010","6955666777","Ερατεινή, Αχαΐα",        0.0),
        ("own-011","6966777888","Πάτρα, Αχαΐα",           0.0),
        ("own-012","6977888999","Αίγιο, Αχαΐα",          10.0),
        ("own-013","6988999000","Ρίο, Αχαΐα",             0.0),
        ("own-014","6999000111","Πάτρα, Αχαΐα",           0.0),
        ("own-015","6900111222","Μεσσάτι, Αχαΐα",         0.0),
    ]
    for row in owners_extra:
        c.execute("INSERT OR IGNORE INTO owners (user_id,phone_number,address,debt_amount) VALUES (?,?,?,?)", row)

    c.execute("INSERT OR IGNORE INTO veterinarians (user_id,specialty) VALUES (?,?)", ("vet-001","Παθολογία"))
    c.execute("INSERT OR IGNORE INTO veterinarians (user_id,specialty) VALUES (?,?)", ("vet-002","Χειρουργική"))
    c.execute("INSERT OR IGNORE INTO receptionists (user_id) VALUES (?)", ("rec-001",))
    c.execute("INSERT OR IGNORE INTO administrators (user_id) VALUES (?)", ("adm-001",))

    for oid in [f"own-{str(i).zfill(3)}" for i in range(1,16)]:
        c.execute("INSERT OR IGNORE INTO notification_preferences (owner_id) VALUES (?)", (oid,))

    conn.commit()

    # ── ΦΑΡΜΑΚΑ ──────────────────────────────────────────────────────────────
    meds = [
        ("med-001","Amoxil",    "Χάπι",     "Αμοξικιλλίνη",    50, 5),
        ("med-002","Rimadyl",   "Χάπι",     "Καρπροφαίνη",     30, 5),
        ("med-003","Bravecto",  "Μασώμενο", "Φλουρολάνερ",     20, 3),
        ("med-004","Nobivac",   "Εμβόλιο",  "Πολυδύναμο Σκύλου",40,5),
        ("med-005","Frontline", "Spray",    "Φιπρονίλη",       25, 5),
        ("med-006","Eurican",   "Εμβόλιο",  "Πολυδύναμο Σκύλου", 8,5),
        ("med-007","Meloxidyl", "Χάπι",     "Μελοξικάμη",      15, 4),
        ("med-008","Feligen",   "Εμβόλιο",  "Πολυδύναμο Γάτας",35, 5),
        ("med-009","Convenia",  "Ένεση",    "Σεφοβεκίν",       12, 3),
        ("med-010","Onsior",    "Χάπι",     "Ροβεναξικάμη",    18, 4),
        ("med-011","Advocate",  "Spot-on",  "Ιμιδακλοπρίδιο", 22, 5),
        ("med-012","Panacur",   "Σκόνη",    "Φεμπεντελαζόλη",  16, 4),
    ]
    for row in meds:
        c.execute("INSERT OR IGNORE INTO medications (id,name,type,active_ingredient,stock_level,min_threshold) VALUES (?,?,?,?,?,?)", row)

    conn.commit()

    # ── ΖΩΑΑ — 28 ζώα σε 15 ιδιοκτήτες ──────────────────────────────────────
    animals = [
        # own-001 Κωνσταντίνα → 2 ζώα
        ("ani-001","Bella",   "Σκύλος","Labrador Retriever",  3, 25.0,"own-001"),
        ("ani-002","Luna",    "Γάτα",  "Siamese",             2,  4.5,"own-001"),
        # own-002 Ιωάννης → 2 ζώα
        ("ani-003","Rocky",   "Σκύλος","French Bulldog",      5, 12.0,"own-002"),
        ("ani-004","Mimi",    "Γάτα",  "Persian",             4,  5.2,"own-002"),
        # own-003 Μαρία → 2 ζώα
        ("ani-005","Zeus",    "Σκύλος","German Shepherd",     6, 35.0,"own-003"),
        ("ani-006","Nala",    "Γάτα",  "Maine Coon",          1,  3.8,"own-003"),
        # own-004 Νίκος → 2 ζώα
        ("ani-007","Max",     "Σκύλος","Golden Retriever",    4, 30.0,"own-004"),
        ("ani-008","Simba",   "Γάτα",  "Scottish Fold",       2,  4.8,"own-004"),
        # own-005 Ελένη → 2 ζώα
        ("ani-009","Cleo",    "Γάτα",  "British Shorthair",   3,  5.0,"own-005"),
        ("ani-010","Archi",   "Σκύλος","Beagle",              2, 10.0,"own-005"),
        # own-006 Χρήστος → 2 ζώα
        ("ani-011","Rex",     "Σκύλος","Rottweiler",          4, 42.0,"own-006"),
        ("ani-012","Kiki",    "Γάτα",  "Ragdoll",             3,  6.1,"own-006"),
        # own-007 Σοφία → 2 ζώα
        ("ani-013","Lola",    "Σκύλος","Poodle",              5,  8.0,"own-007"),
        ("ani-014","Oscar",   "Γάτα",  "Abyssinian",          4,  4.2,"own-007"),
        # own-008 Δημήτρης → 2 ζώα
        ("ani-015","Bruno",   "Σκύλος","Doberman",            3, 38.0,"own-008"),
        ("ani-016","Lily",    "Γάτα",  "Russian Blue",        2,  3.9,"own-008"),
        # own-009 Αγγελική → 2 ζώα
        ("ani-017","Roxy",    "Σκύλος","Chihuahua",           6,  2.5,"own-009"),
        ("ani-018","Tigger",  "Γάτα",  "Bengal",              3,  5.5,"own-009"),
        # own-010 Παναγιώτης → 2 ζώα
        ("ani-019","Duke",    "Σκύλος","Husky",               2, 28.0,"own-010"),
        ("ani-020","Mia",     "Γάτα",  "Turkish Angora",      5,  4.0,"own-010"),
        # own-011 Κατερίνα → 2 ζώα
        ("ani-021","Toby",    "Σκύλος","Cocker Spaniel",      4, 14.0,"own-011"),
        ("ani-022","Zoe",     "Γάτα",  "Burmese",             2,  4.3,"own-011"),
        # own-012 Θανάσης → 1 ζώο
        ("ani-023","Hector",  "Σκύλος","Border Collie",       3, 20.0,"own-012"),
        # own-013 Ζωή → 2 ζώα
        ("ani-024","Daisy",   "Γάτα",  "Norwegian Forest",    1,  3.5,"own-013"),
        ("ani-025","Paco",    "Σκύλος","Shih Tzu",            7,  6.0,"own-013"),
        # own-014 Κώστας → 1 ζώο
        ("ani-026","Atlas",   "Σκύλος","Saint Bernard",       5, 65.0,"own-014"),
        # own-015 Ανδρέας → 2 ζώα
        ("ani-027","Penny",   "Γάτα",  "Sphynx",              4,  4.6,"own-015"),
        ("ani-028","Spike",   "Σκύλος","Dalmatian",           2, 22.0,"own-015"),
    ]
    for row in animals:
        c.execute("INSERT OR IGNORE INTO animals (id,name,species,breed,age,weight,owner_id) VALUES (?,?,?,?,?,?,?)", row)

    conn.commit()

    # ── ΙΑΤΡΙΚΕΣ ΕΓΓΡΑΦΕΣ ────────────────────────────────────────────────────
    records = [
        # Bella (ani-001)
        ("mr-001",p7,"Ετήσια εξέταση",             "Εξέταση",     "ani-001","vet-001"),
        ("mr-002",p5,"Εμβολιασμός Nobivac",         "Εμβολιασμός", "ani-001","vet-001"),
        ("mr-003",p2,"Επανεξέταση - γαστρεντερίτιδα","Εξέταση",   "ani-001","vet-001"),
        ("mr-004",p2,"Συνταγή Amoxil",              "Συνταγή",     "ani-001","vet-001"),
        # Luna (ani-002)
        ("mr-005",p6,"Ετήσια εξέταση",             "Εξέταση",     "ani-002","vet-001"),
        ("mr-006",p4,"Εμβολιασμός Feligen",         "Εμβολιασμός", "ani-002","vet-001"),
        ("mr-007",p1,"Εξέταση - ουρολοίμωξη",      "Εξέταση",     "ani-002","vet-001"),
        # Rocky (ani-003)
        ("mr-008",p7,"Εξέταση δερματίτιδας",       "Εξέταση",     "ani-003","vet-002"),
        ("mr-009",p5,"Εμβολιασμός Eurican",         "Εμβολιασμός", "ani-003","vet-002"),
        ("mr-010",p3,"Χειρουργείο - αποστείρωση",  "Εξέταση",     "ani-003","vet-002"),
        # Mimi (ani-004)
        ("mr-011",p4,"Ετήσια εξέταση",             "Εξέταση",     "ani-004","vet-001"),
        ("mr-012",p2,"Εμβολιασμός Feligen",         "Εμβολιασμός", "ani-004","vet-001"),
        # Zeus (ani-005)
        ("mr-013",p6,"Ετήσια εξέταση",             "Εξέταση",     "ani-005","vet-001"),
        ("mr-014",p4,"Εμβολιασμός Nobivac",         "Εμβολιασμός", "ani-005","vet-001"),
        ("mr-015",p2,"Εξέταση - πρόβλημα αρθρώσεων","Εξέταση",   "ani-005","vet-002"),
        ("mr-016",p2,"Συνταγή Rimadyl",             "Συνταγή",     "ani-005","vet-002"),
        # Nala (ani-006)
        ("mr-017",p3,"Πρώτη επίσκεψη",             "Εξέταση",     "ani-006","vet-001"),
        ("mr-018",p1,"Εμβολιασμός Feligen",         "Εμβολιασμός", "ani-006","vet-001"),
        # Max (ani-007)
        ("mr-019",p5,"Ετήσια εξέταση",             "Εξέταση",     "ani-007","vet-001"),
        ("mr-020",p3,"Εμβολιασμός Nobivac",         "Εμβολιασμός", "ani-007","vet-001"),
        ("mr-021",p1,"Εξέταση - δερματικό",        "Εξέταση",     "ani-007","vet-001"),
        # Simba (ani-008)
        ("mr-022",p4,"Ετήσια εξέταση",             "Εξέταση",     "ani-008","vet-001"),
        ("mr-023",p2,"Εμβολιασμός Feligen",         "Εμβολιασμός", "ani-008","vet-001"),
        # Cleo (ani-009)
        ("mr-024",p5,"Ετήσια εξέταση",             "Εξέταση",     "ani-009","vet-001"),
        ("mr-025",p3,"Εμβολιασμός Feligen",         "Εμβολιασμός", "ani-009","vet-001"),
        # Archi (ani-010)
        ("mr-026",p6,"Ετήσια εξέταση",             "Εξέταση",     "ani-010","vet-001"),
        ("mr-027",p4,"Εμβολιασμός Eurican",         "Εμβολιασμός", "ani-010","vet-001"),
        ("mr-028",p1,"Εξέταση - ωτίτιδα",          "Εξέταση",     "ani-010","vet-001"),
        # Rex (ani-011)
        ("mr-029",p5,"Ετήσια εξέταση",             "Εξέταση",     "ani-011","vet-002"),
        ("mr-030",p3,"Εμβολιασμός Nobivac",         "Εμβολιασμός", "ani-011","vet-002"),
        # Kiki (ani-012)
        ("mr-031",p4,"Ετήσια εξέταση",             "Εξέταση",     "ani-012","vet-001"),
        # Lola (ani-013)
        ("mr-032",p6,"Ετήσια εξέταση",             "Εξέταση",     "ani-013","vet-001"),
        ("mr-033",p4,"Εμβολιασμός Nobivac",         "Εμβολιασμός", "ani-013","vet-001"),
        ("mr-034",p2,"Καθαρισμός δοντιών",         "Εξέταση",     "ani-013","vet-001"),
        # Oscar (ani-014)
        ("mr-035",p3,"Ετήσια εξέταση",             "Εξέταση",     "ani-014","vet-001"),
        # Bruno (ani-015)
        ("mr-036",p5,"Ετήσια εξέταση",             "Εξέταση",     "ani-015","vet-002"),
        ("mr-037",p3,"Εμβολιασμός Nobivac",         "Εμβολιασμός", "ani-015","vet-002"),
        # Lily (ani-016)
        ("mr-038",p4,"Ετήσια εξέταση",             "Εξέταση",     "ani-016","vet-001"),
        ("mr-039",p2,"Εμβολιασμός Feligen",         "Εμβολιασμός", "ani-016","vet-001"),
        # Roxy (ani-017)
        ("mr-040",p7,"Ετήσια εξέταση",             "Εξέταση",     "ani-017","vet-001"),
        ("mr-041",p5,"Εμβολιασμός Nobivac",         "Εμβολιασμός", "ani-017","vet-001"),
        ("mr-042",p2,"Εξέταση - καρδιολογική",     "Εξέταση",     "ani-017","vet-001"),
        # Tigger (ani-018)
        ("mr-043",p4,"Ετήσια εξέταση",             "Εξέταση",     "ani-018","vet-001"),
        ("mr-044",p2,"Εμβολιασμός Feligen",         "Εμβολιασμός", "ani-018","vet-001"),
        # Duke (ani-019)
        ("mr-045",p3,"Πρώτη επίσκεψη",             "Εξέταση",     "ani-019","vet-001"),
        ("mr-046",p1,"Εμβολιασμός Nobivac",         "Εμβολιασμός", "ani-019","vet-001"),
        # Mia (ani-020)
        ("mr-047",p5,"Ετήσια εξέταση",             "Εξέταση",     "ani-020","vet-001"),
        # Toby (ani-021)
        ("mr-048",p4,"Ετήσια εξέταση",             "Εξέταση",     "ani-021","vet-001"),
        ("mr-049",p2,"Εμβολιασμός Eurican",         "Εμβολιασμός", "ani-021","vet-001"),
        # Zoe (ani-022)
        ("mr-050",p3,"Ετήσια εξέταση",             "Εξέταση",     "ani-022","vet-001"),
        # Hector (ani-023)
        ("mr-051",p5,"Ετήσια εξέταση",             "Εξέταση",     "ani-023","vet-001"),
        ("mr-052",p3,"Εμβολιασμός Nobivac",         "Εμβολιασμός", "ani-023","vet-001"),
        # Daisy (ani-024)
        ("mr-053",p2,"Πρώτη επίσκεψη",             "Εξέταση",     "ani-024","vet-001"),
        # Paco (ani-025)
        ("mr-054",p7,"Ετήσια εξέταση",             "Εξέταση",     "ani-025","vet-001"),
        ("mr-055",p5,"Εμβολιασμός Nobivac",         "Εμβολιασμός", "ani-025","vet-001"),
        # Atlas (ani-026)
        ("mr-056",p6,"Ετήσια εξέταση",             "Εξέταση",     "ani-026","vet-002"),
        ("mr-057",p4,"Εμβολιασμός Nobivac",         "Εμβολιασμός", "ani-026","vet-002"),
        ("mr-058",p1,"Εξέταση - δυσπλασία ισχίου", "Εξέταση",    "ani-026","vet-002"),
        # Penny (ani-027)
        ("mr-059",p4,"Ετήσια εξέταση",             "Εξέταση",     "ani-027","vet-001"),
        ("mr-060",p2,"Εμβολιασμός Feligen",         "Εμβολιασμός", "ani-027","vet-001"),
        # Spike (ani-028)
        ("mr-061",p3,"Πρώτη επίσκεψη",             "Εξέταση",     "ani-028","vet-001"),
        ("mr-062",p1,"Εμβολιασμός Nobivac",         "Εμβολιασμός", "ani-028","vet-001"),
    ]
    for rid, rdate, notes, rtype, anid, vid in records:
        c.execute("INSERT OR IGNORE INTO medical_records (id,record_date,notes,record_type,animal_id,vet_id) VALUES (?,?,?,?,?,?)",
                  (rid, rdate, notes, rtype, anid, vid))

    conn.commit()

    # Examinations
    exams = [
        ("mr-001","Καλή υγεία γενικά, συνιστάται εμβολιασμός"),
        ("mr-003","Γαστρεντερίτιδα - χορηγήθηκε αγωγή Amoxil"),
        ("mr-005","Ελαφρά υπέρβαρο, προτείνεται δίαιτα"),
        ("mr-007","Ουρολοίμωξη - χορηγήθηκε Convenia"),
        ("mr-008","Δερματίτιδα αλλεργικής αιτιολογίας"),
        ("mr-010","Επιτυχής αποστείρωση, καλή ανάρρωση"),
        ("mr-011","Καλή υγεία"),
        ("mr-013","Άριστη κατάσταση υγείας"),
        ("mr-015","Αρθρίτιδα αριστερού ισχίου - Rimadyl"),
        ("mr-017","Υγιές ζώο - πρώτη επίσκεψη"),
        ("mr-019","Καλή υγεία"),
        ("mr-021","Δερματικό πρόβλημα - αλλεργία"),
        ("mr-022","Καλή υγεία"),
        ("mr-024","Ελαφρά υπέρβαρο"),
        ("mr-026","Καλή υγεία"),
        ("mr-028","Ωτίτιδα αριστερού ωτός - αγωγή"),
        ("mr-029","Άριστη κατάσταση"),
        ("mr-031","Καλή υγεία"),
        ("mr-032","Ελαφρά τρυγία δοντιών"),
        ("mr-034","Καθαρισμός δοντιών ολοκληρώθηκε"),
        ("mr-035","Καλή υγεία"),
        ("mr-036","Καλή υγεία"),
        ("mr-038","Υγιές ζώο"),
        ("mr-040","Πρόβλημα καρδιάς - παρακολούθηση"),
        ("mr-042","Καρδιολογική εξέταση - σταθερή κατάσταση"),
        ("mr-043","Καλή υγεία"),
        ("mr-045","Υγιές ζώο - πρώτη επίσκεψη"),
        ("mr-047","Καλή υγεία"),
        ("mr-048","Ελαφρά υπέρβαρο"),
        ("mr-050","Καλή υγεία"),
        ("mr-051","Άριστη κατάσταση"),
        ("mr-053","Υγιές ζώο - πρώτη επίσκεψη"),
        ("mr-054","Ελαφρά οδοντικά προβλήματα"),
        ("mr-056","Υπέρβαρο - δίαιτα"),
        ("mr-058","Δυσπλασία ισχίου - παρακολούθηση"),
        ("mr-059","Υγιές ζώο"),
        ("mr-061","Υγιές ζώο - πρώτη επίσκεψη"),
    ]
    for rid, diag in exams:
        c.execute("INSERT OR IGNORE INTO examinations (record_id,diagnosis) VALUES (?,?)", (rid, diag))

    # Vaccinations
    vax_records = [
        ("mr-002","Nobivac","BATCH2023-01",ny,0),
        ("mr-006","Feligen", "BATCH2023-02",ny,0),
        ("mr-009","Eurican", "BATCH2023-03",ny,0),
        ("mr-012","Feligen", "BATCH2024-01",ny,0),
        ("mr-014","Nobivac", "BATCH2024-02",ny,0),
        ("mr-018","Feligen", "BATCH2024-03",ny,0),
        ("mr-020","Nobivac", "BATCH2024-04",ny,0),
        ("mr-023","Feligen", "BATCH2024-05",ny,0),
        ("mr-025","Feligen", "BATCH2024-06",ny,0),
        ("mr-027","Eurican", "BATCH2024-07",ny,0),
        ("mr-030","Nobivac", "BATCH2024-08",ny,0),
        ("mr-033","Nobivac", "BATCH2024-09",ny,0),
        ("mr-037","Nobivac", "BATCH2024-10",ny,0),
        ("mr-039","Feligen", "BATCH2024-11",ny,0),
        ("mr-041","Nobivac", "BATCH2024-12",ny,0),
        ("mr-044","Feligen", "BATCH2025-01",ny,0),
        ("mr-046","Nobivac", "BATCH2025-02",ny,0),
        ("mr-049","Eurican", "BATCH2025-03",ny,0),
        ("mr-052","Nobivac", "BATCH2025-04",ny,0),
        ("mr-055","Nobivac", "BATCH2025-05",ny,0),
        ("mr-057","Nobivac", "BATCH2025-06",ny,0),
        ("mr-060","Feligen", "BATCH2025-07",ny,0),
        ("mr-062","Nobivac", "BATCH2025-08",ny,0),
    ]
    for row in vax_records:
        c.execute("INSERT OR IGNORE INTO vaccinations (record_id,vaccine_name,batch_number,next_due_date,allergy_reaction) VALUES (?,?,?,?,?)", row)

    conn.commit()

    # ── ΣΥΝΤΑΓΕΣ ─────────────────────────────────────────────────────────────
    prescriptions = [
        ("pres-001",p2,"ani-001","vet-001","mr-004"),
        ("pres-002",p2,"ani-005","vet-002","mr-016"),
    ]
    for row in prescriptions:
        c.execute("INSERT OR IGNORE INTO prescriptions (id,pres_date,animal_id,vet_id,record_id) VALUES (?,?,?,?,?)", row)

    pres_items = [
        ("pi-001","pres-001","med-001",14,"1 χάπι 2 φορές/ημέρα για 7 ημέρες"),
        ("pi-002","pres-002","med-002",30,"1 χάπι ημερησίως με φαγητό"),
    ]
    for row in pres_items:
        c.execute("INSERT OR IGNORE INTO prescription_items (id,prescription_id,medication_id,quantity,dosage) VALUES (?,?,?,?,?)", row)

    conn.commit()

    # ── ΡΑΝΤΕΒΟΥ ─────────────────────────────────────────────────────────────
    appointments = [
        # Επερχόμενα
        ("apt-001",t1,"09:00","Εξέταση ρουτίνας",        "Scheduled",1,"ani-001","vet-001"),
        ("apt-002",t1,"10:00","Εμβολιασμός Feligen",      "Scheduled",1,"ani-002","vet-001"),
        ("apt-003",t1,"11:00","Επανεξέταση αρθρώσεων",   "Scheduled",1,"ani-005","vet-002"),
        ("apt-004",t1,"12:00","Εξέταση ρουτίνας",        "Scheduled",1,"ani-011","vet-002"),
        ("apt-005",t2,"09:00","Εξέταση ρουτίνας",        "Scheduled",1,"ani-007","vet-001"),
        ("apt-006",t2,"10:00","Εμβολιασμός Nobivac",     "Scheduled",1,"ani-010","vet-001"),
        ("apt-007",t2,"11:00","Εξέταση - δέρμα",        "Scheduled",1,"ani-015","vet-002"),
        ("apt-008",t3,"09:00","Ετήσια εξέταση",          "Scheduled",1,"ani-003","vet-002"),
        ("apt-009",t3,"10:00","Εξέταση - πεπτικό",      "Scheduled",1,"ani-004","vet-001"),
        ("apt-010",t3,"11:30","Εμβολιασμός Eurican",     "Scheduled",1,"ani-023","vet-001"),
        ("apt-011",t4,"09:30","Εξέταση ρουτίνας",       "Scheduled",1,"ani-013","vet-001"),
        ("apt-012",t4,"10:30","Εμβολιασμός Feligen",    "Scheduled",1,"ani-016","vet-001"),
        ("apt-013",t4,"11:30","Επανεξέταση ωτίτιδας",  "Scheduled",1,"ani-010","vet-001"),
        ("apt-014",t5,"09:00","Εμβολιασμός Nobivac",    "Scheduled",1,"ani-019","vet-001"),
        ("apt-015",t5,"10:00","Ετήσια εξέταση",         "Scheduled",1,"ani-022","vet-001"),
        ("apt-016",t7,"09:00","Εξέταση καρδιάς",        "Scheduled",1,"ani-017","vet-001"),
        ("apt-017",t7,"10:00","Εξέταση ισχίου",         "Scheduled",1,"ani-026","vet-002"),
        ("apt-018",t10,"09:00","Εμβολιασμός Feligen",  "Scheduled",1,"ani-027","vet-001"),
        ("apt-019",t14,"10:00","Ετήσια εξέταση",        "Scheduled",1,"ani-028","vet-001"),
        # Ολοκληρωμένα
        ("apt-020",p1,"10:00","Εξέταση ρουτίνας",       "Completed",1,"ani-001","vet-001"),
        ("apt-021",p2,"11:00","Εμβολιασμός",            "Completed",1,"ani-003","vet-002"),
        ("apt-022",p3,"09:00","Εξέταση ρουτίνας",       "Completed",1,"ani-007","vet-001"),
        ("apt-023",p4,"10:00","Ετήσια εξέταση",         "Completed",1,"ani-013","vet-001"),
    ]
    for row in appointments:
        c.execute("INSERT OR IGNORE INTO appointments (id,appt_date,time,reason,status,priority,animal_id,vet_id) VALUES (?,?,?,?,?,?,?,?)", row)

    conn.commit()

    # ── ΝΟΣΗΛΕΙΕΣ ────────────────────────────────────────────────────────────
    # Rocky (ani-003): ολοκληρωμένη
    c.execute("INSERT OR IGNORE INTO hospitalizations (id,admission_date,discharge_date,reason,status,animal_id,vet_id) VALUES (?,?,?,?,?,?,?)",
              ("hosp-001",p3,p2,"Μετεγχειρητική παρακολούθηση αποστείρωσης","Discharged","ani-003","vet-002"))
    c.execute("INSERT OR IGNORE INTO daily_logs (id,log_date,temperature,weight,medication,notes,hospitalization_id) VALUES (?,?,?,?,?,?,?)",
              ("dlog-001",p3,38.6,12.0,"Amoxil 2x","Σταθερή κατάσταση, καλή ανάρρωση","hosp-001"))
    c.execute("INSERT OR IGNORE INTO daily_logs (id,log_date,temperature,weight,medication,notes,hospitalization_id) VALUES (?,?,?,?,?,?,?)",
              ("dlog-002",p2,38.4,12.2,"Amoxil 1x","Εξαιρετική πρόοδος - έτοιμο για εξιτήριο","hosp-001"))

    # Zeus (ani-005): ενεργή
    c.execute("INSERT OR IGNORE INTO hospitalizations (id,admission_date,reason,status,animal_id,vet_id) VALUES (?,?,?,?,?,?)",
              ("hosp-002",p1,"Παρακολούθηση αρθρίτιδας ισχίου","Active","ani-005","vet-002"))
    c.execute("INSERT OR IGNORE INTO daily_logs (id,log_date,temperature,weight,medication,notes,hospitalization_id) VALUES (?,?,?,?,?,?,?)",
              ("dlog-003",p1,38.9,34.5,"Rimadyl 1x","Μέτρια κινητικότητα, παρακολούθηση","hosp-002"))
    c.execute("INSERT OR IGNORE INTO daily_logs (id,log_date,temperature,weight,medication,notes,hospitalization_id) VALUES (?,?,?,?,?,?,?)",
              ("dlog-004",today,38.7,34.8,"Rimadyl 1x","Βελτίωση κινητικότητας","hosp-002"))

    conn.commit()

    # ── ΠΛΗΡΩΜΕΣ ─────────────────────────────────────────────────────────────
    payments = [
        ("pay-001",60.0,"Μετρητά",p2,"Paid",  "apt-020","own-001"),
        ("pay-002",80.0,"Κάρτα",  p3,"Paid",  "apt-021","own-002"),
        ("pay-003",55.0,"Μετρητά",p3,"Paid",  "apt-022","own-004"),
        ("pay-004",70.0,"Κάρτα",  p4,"Paid",  "apt-023","own-007"),
        ("pay-005",45.0,"Μετρητά",p2,"Partial",None,    "own-006"),
        ("pay-006",30.0,"Κάρτα",  p1,"Partial",None,   "own-009"),
        ("pay-007",90.0,"Μετρητά",p4,"Paid",  None,    "own-014"),
    ]
    for row in payments:
        c.execute("INSERT OR IGNORE INTO payments (id,amount,method,pay_date,status,appointment_id,owner_id) VALUES (?,?,?,?,?,?,?)", row)

    conn.commit()

    # ── ΥΠΕΝΘΥΜΙΣΕΙΣ ─────────────────────────────────────────────────────────
    reminders = [
        ("rem-001",t1, "Ραντεβού","Υπενθύμιση ραντεβού αύριο 09:00 για Bella",         "Sent",   "own-001","ani-001"),
        ("rem-002",t1, "Εμβόλιο", "Υπενθύμιση: Εμβολιασμός Feligen για Luna",          "Sent",   "own-001","ani-002"),
        ("rem-003",t2, "Ραντεβού","Υπενθύμιση ραντεβού για Max",                       "Sent",   "own-004","ani-007"),
        ("rem-004",t2, "Εμβόλιο", "Υπενθύμιση: Εμβολιασμός Nobivac για Archi",        "Sent",   "own-005","ani-010"),
        ("rem-005",t3, "Ραντεβού","Υπενθύμιση ραντεβού για Rocky",                     "Sent",   "own-002","ani-003"),
        ("rem-006",t4, "Ραντεβού","Υπενθύμιση ραντεβού για Lola",                      "Pending","own-007","ani-013"),
        ("rem-007",t5, "Εμβόλιο", "Υπενθύμιση: Εμβολιασμός Nobivac για Duke",         "Pending","own-010","ani-019"),
        ("rem-008",t7, "Ραντεβού","Υπενθύμιση ραντεβού για Atlas",                     "Pending","own-014","ani-026"),
        ("rem-009",ny, "Εμβόλιο", "Ετήσιος εμβολιασμός Nobivac για Bella",            "Pending","own-001","ani-001"),
        ("rem-010",ny, "Εμβόλιο", "Ετήσιος εμβολιασμός Feligen για Luna",             "Pending","own-001","ani-002"),
        ("rem-011",t10,"Εμβόλιο", "Υπενθύμιση: Εμβολιασμός Feligen για Penny",       "Pending","own-015","ani-027"),
        ("rem-012",t14,"Ραντεβού","Υπενθύμιση ραντεβού για Spike",                    "Pending","own-015","ani-028"),
    ]
    for row in reminders:
        c.execute("INSERT OR IGNORE INTO reminders (id,send_date,reminder_type,message,status,owner_id,animal_id) VALUES (?,?,?,?,?,?,?)", row)

    conn.commit()
    conn.close()
    print("[DB] Demo data seeded: 15 ιδιοκτήτες, 28 ζώα, 62 ιατρικές εγγραφές, 19 ραντεβού")

if __name__ == "__main__":
    setup_database()
    seed_demo_data()
