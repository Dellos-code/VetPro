# VetPro — Veterinary Clinic Management System

> Advanced veterinary clinic management platform with heuristic scheduling
> and stochastic inventory forecasting engines.

## Architecture

```
VetPro/
├── src/                         # Java Spring Boot backend (CRUD + REST API)
│   └── main/java/com/vetpro/
│       ├── model/               # JPA entities
│       ├── repository/          # Spring Data repositories
│       ├── service/             # Business logic
│       ├── controller/          # REST controllers
│       └── config/              # Security, auth
├── engines/                     # Python algorithmic engines
│   ├── scheduler_engine.py      # Heuristic appointment optimizer
│   ├── inventory_engine.py      # Monte Carlo inventory forecaster
│   ├── api.py                   # FastAPI REST wrapper
│   └── tests/                   # Engine unit tests
└── pom.xml
```

## Roles

| Role | Description |
|------|-------------|
| **Owner** (Ιδιοκτήτης ζώου) | Pet owner — books appointments, views pet history, manages profile |
| **Vet** (Κτηνίατρος) | Veterinarian — diagnoses, prescribes, administers vaccines, manages hospitalizations |
| **Receptionist** (Ρεσεψιόν) | Front desk — schedules appointments, handles billing/payments |
| **Admin** (Διαχειριστής) | System administrator — manages users, medications, reports |

## Use Cases

| # | Use Case | API Path |
|---|----------|----------|
| 1 | Appointment Booking | `POST /api/appointments` |
| 2 | Animal History | `GET /api/medical-records/pet/{petId}` |
| 3 | Prescriptions | `POST /api/prescriptions` |
| 4 | Vaccine Management | `POST /api/vaccine-records` |
| 5 | Reminder Notifications | `GET /api/reminders/pending` |
| 6 | Billing & Payments | `POST /api/invoices`, `POST /api/payments` |
| 7 | Reports | `GET /api/reports/*` |
| 8 | Medication Stock | `GET /api/medications/low-stock` |
| 9 | Hospitalization | `POST /api/hospitalizations` |
| 10 | Owner Profile | `GET /api/users/{id}` |

## Algorithmic Engines

### Use Case A: Heuristic Scheduler Engine

**Problem**: Multi-constraint optimization — allocate *N* appointments across
*M* veterinarians and *K* rooms, respecting hard constraints (no overlaps,
working hours, vet competencies) while minimizing dead time and respecting
clinical priorities.

**Algorithm**:
1. **Priority sort** — EMERGENCY > URGENT > FOLLOW_UP > ROUTINE (SJF tie-break)
2. **Greedy construction** — For each appointment, evaluate all feasible
   (vet, room, time) triples and select the one minimizing the weighted
   objective function
3. **Emergency preemption** — Displace lowest-priority routine slots to
   accommodate emergencies without collapsing the schedule
4. **Local search refinement** — Pairwise swap neighbourhood search to
   improve the objective post-construction

**Objective function**:
```
minimize  w₁·Σᵥ(dead_time_v) + w₂·Σᵣ(idle_r) + w₃·Σᵢ(delay_i / priority_i) + w₄·makespan
```

**API**: `POST /api/engine/schedule`

### Use Case B: Stochastic Inventory Engine

**Problem**: Predict medication stockouts using probabilistic demand modelling
instead of deterministic thresholds.

**Mathematical model**:
```
D_daily  ~ Poisson(λ)                    — daily dispensing demand
L        ~ max(1, Normal(μ_L, σ_L))      — stochastic supplier lead time
D_lead   = Σ_{t=1}^{L} Poisson(λ)        — compound demand during lead time
```

**Algorithm** — Monte Carlo simulation:
1. Sample *N* lead-time values from the truncated normal distribution
2. For each lead time, sample total demand from Poisson(L·λ)
3. Build the empirical CDF of demand-during-lead-time
4. **Reorder point** R* = smallest R where P(D_lead ≤ R) ≥ target service level
5. **Stockout probability** = P(D_lead > current_stock)
6. **Value-at-Risk**: 95th and 99th percentiles of D_lead

**API**: `POST /api/engine/inventory/forecast`

## Getting Started

### Java Backend

```bash
mvn clean compile
mvn spring-boot:run          # starts on port 8080
```

### Python Engines

```bash
pip install -r engines/requirements.txt
uvicorn engines.api:app --port 8081    # starts on port 8081
```

### Run Engine Tests

```bash
python -m pytest engines/tests/ -v
```

## Technology Stack

- **Backend**: Java 17, Spring Boot 3.2, Spring Security, Spring Data JPA
- **Database**: H2 (development), PostgreSQL-ready
- **Engines**: Python 3.12, NumPy, SciPy, FastAPI
- **Algorithms**: Greedy CSP + Local Search, Monte Carlo Simulation
