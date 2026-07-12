# EcoSphere 🌱 — ESG Management Platform

**EcoSphere** is a full-stack ESG (Environmental, Social, Governance) management platform built for the Odoo Hackathon 2026. It integrates sustainability tracking directly into everyday operations — turning ERP-style transactional data into automated carbon accounting, employee CSR participation, governance compliance, and gamified engagement, all rolled up into live ESG scores.

Most ERP systems collect operational data but leave ESG reporting manual and disconnected. EcoSphere closes that gap: emissions are calculated automatically from operational records, employees earn XP and badges for sustainability actions, compliance issues are tracked to resolution, and management gets a real-time weighted ESG score across every department.

---

## Core Modules

- 🌍 **Environmental** — Emission factor configuration, automated carbon accounting from operational data, sustainability goals, and department-level carbon tracking
- 🤝 **Social** — CSR activity management, employee participation tracking with proof-of-completion, and engagement scoring
- ⚖️ **Governance** — Policy management, employee acknowledgements, audits, and compliance issue tracking with ownership and due dates
- 🏆 **Gamification** — Challenges with a full lifecycle (Draft → Active → Under Review → Completed), auto-awarded badges, redeemable rewards, and leaderboards
- 📊 **Reports & Analytics** — Environmental, Social, Governance, and ESG Summary reports with CSV export

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python, FastAPI, SQLAlchemy ORM, Alembic, JWT Auth |
| **Database** | PostgreSQL (SQLite for development) |
| **Frontend** | React, TypeScript, Vite, Tailwind CSS v3 |
| **Data Fetching** | TanStack Query |
| **Forms** | React Hook Form |
| **Charts** | Recharts |
| **Storage** | S3-compatible (local filesystem in dev) |

---

## Project Structure

```
EcoSphere-Odoo-Hackathon-2026/
├── backend/                        # FastAPI application
│   ├── app/
│   │   ├── api/v1/                 # Route handlers (one file per resource)
│   │   ├── core/                   # Config, security, database, dependencies
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   ├── schemas/                # Pydantic v2 request/response schemas
│   │   ├── services/               # Business logic layer
│   │   ├── repositories/           # Data access layer (repository pattern)
│   │   └── main.py                 # FastAPI entry point
│   ├── alembic/                    # Database migrations
│   ├── seed.py                     # Demo data seeder
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/                       # React + Vite application
    ├── src/
    │   ├── api/                    # TanStack Query hooks per feature
    │   ├── components/             # Shared UI components
    │   ├── features/
    │   │   ├── auth/               # Login, token management
    │   │   ├── dashboard/          # KPI cards, charts, quick actions
    │   │   ├── environmental/      # Emission factors, carbon transactions, goals
    │   │   ├── social/             # CSR activities, participations
    │   │   ├── governance/         # Policies, audits, compliance issues
    │   │   ├── gamification/       # Challenges, badges, rewards, leaderboard
    │   │   ├── reports/            # Report builder, exports
    │   │   └── settings/           # Users, departments, ESG weights
    │   ├── layouts/                # App shell, sidebar, top nav
    │   ├── types/                  # Shared TypeScript types
    │   └── main.tsx
    ├── tailwind.config.ts
    └── package.json
```

---

## Backend – Key Components

### Models (SQLAlchemy)

| Model | Description |
|---|---|
| `User`, `Role` | Auth and RBAC |
| `Department` | Org hierarchy |
| `Category` | Reusable tags for CSR / challenges |
| `EmissionFactor` | Carbon conversion values (kg CO₂e per unit) |
| `CarbonTransaction` | Auto-calculated emissions from ERP operations |
| `EnvironmentalGoal` | Sustainability targets with progress tracking |
| `ProductESGProfile` | ESG metadata per product |
| `CSRActivity` | Company CSR events |
| `EmployeeParticipation` | CSR participation with proof & approval |
| `ESGPolicy`, `PolicyAcknowledgement` | Governance policies and employee sign-offs |
| `Audit`, `ComplianceIssue` | Audit findings and violation tracking |
| `Challenge`, `ChallengeParticipation` | Gamified sustainability challenges |
| `Badge`, `UserBadge` | Auto-awarded achievement badges |
| `Reward`, `RewardRedemption` | Redeemable rewards with XP deduction |
| `DepartmentScore` | Computed ESG scores per department |
| `Notification` | In-app notification records |

### Services

| Service | Responsibility |
|---|---|
| `carbon_service` | Auto-calculate CO₂ from quantity × emission factor |
| `score_service` | Weighted ESG score: Env 40% + Social 30% + Gov 30% |
| `gamification_service` | XP award, badge unlock checks, reward redemption |
| `notification_service` | Create in-app notifications on key events |
| `report_service` | Aggregate data for report generation and CSV export |

### API Routes (`/api/v1/`)

`auth` · `users` · `departments` · `categories` · `emission-factors` · `carbon-transactions` · `environmental-goals` · `csr-activities` · `employee-participations` · `policies` · `policy-acknowledgements` · `audits` · `compliance-issues` · `challenges` · `challenge-participations` · `badges` · `rewards` · `department-scores` · `notifications` · `dashboard` · `reports`

---

## Frontend – Feature Modules

### Dashboard
- ESG Score KPI cards (Environmental / Social / Governance / Total)
- Carbon Trend line chart
- Department ESG Ranking bar chart
- Quick Actions panel
- Live data from aggregated dashboard endpoint

### Environmental
- Emission Factors list + CRUD
- Carbon Transactions table with department/date filters
- Product ESG Profiles
- Environmental Goals with progress bars
- Department carbon heatmap

### Social
- CSR Activities management (create, view, manage participation)
- Employee Participation with proof upload and approval workflow
- Engagement scoring per department

### Governance
- ESG Policies with status badges
- Policy Acknowledgements tracking per employee
- Audits with findings log
- Compliance Issues with severity, owner, due date — overdue items highlighted

### Gamification
- Challenges board grouped by lifecycle state (Draft / Active / Under Review / Completed)
- Leaderboard table sorted by XP
- Badge gallery with unlock rules
- Reward catalog with one-click redemption (XP deducted automatically)

### Reports
- Pre-built report cards: Environmental, Social, Governance, ESG Summary
- Custom Report Builder with filters (department, date range, employee, module)
- CSV export

### Settings
- User management + role assignment
- Department configuration
- ESG weight configuration (Environmental / Social / Governance %)
- Notification preferences

---

## ESG Score Formula

```
Department Score = (Environmental × 0.40) + (Social × 0.30) + (Governance × 0.30)
Organization Score = Average of all Department Scores
```

> Weights are configurable via Settings.

---

## Gamification Rules

| Action | Reward |
|---|---|
| Complete a Challenge | XP defined per challenge |
| Participate in CSR Activity | Fixed XP on approval |
| Acknowledge ESG Policy | Compliance XP |
| Submit proof for sustainability activity | Bonus XP |

XP thresholds auto-unlock **Badges**. Accumulated XP can be redeemed for **Rewards** (stock-limited). Redemption deducts XP automatically.

---

## User Roles

| Role | Access |
|---|---|
| **System Admin** | Full access — configure everything |
| **ESG Manager** | Manage all ESG modules and reports |
| **Department Manager** | Manage department activities and view scores |
| **Employee** | Join challenges, CSR activities, earn XP |
| **Auditor** | Perform audits and compliance reviews |

---

## Development Phases

| Phase | Scope | Status |
|---|---|---|
| 1 | Authentication, Users, Departments, Categories | 🔲 Planned |
| 2 | Environmental Module, Carbon Calculations, Goals | 🔲 Planned |
| 3 | Social Module, CSR, Employee Participation | 🔲 Planned |
| 4 | Governance Module, Policies, Audits, Compliance | 🔲 Planned |
| 5 | Gamification (Challenges, Badges, Rewards, Leaderboard) | 🔲 Planned |
| 6 | Dashboard (Live KPIs, Charts, Rankings) | 🔲 Planned |
| 7 | Reports & Analytics (Pre-built + Custom Builder) | 🔲 Planned |
| 8 | Notifications (In-App + Email) | 🔲 Planned |
| 9 | Optimization, Testing, Deployment | 🔲 Planned |

---

## Getting Started

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Configure your database URL and secret key
alembic upgrade head            # Run migrations
python seed.py                  # Load demo data
uvicorn app.main:app --reload   # Start API server → http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev                     # Start dev server → http://localhost:5173
```

### API Docs

Interactive Swagger UI available at: `http://localhost:8000/docs`

---

## Non-Functional Requirements

- ✅ Responsive, dark-themed enterprise UI
- ✅ Role-Based Access Control (RBAC)
- ✅ Clean Architecture — Repository → Service → API separation
- ✅ Type-safe API contracts via Pydantic v2
- ✅ Database migrations with Alembic (zero-downtime schema changes)
- ✅ Audit logging on key entities
- ✅ Modular, extensible feature structure

---

## Future Enhancements

- 🤖 AI Sustainability Recommendations
- 📈 Predictive Carbon Analytics
- 📱 Mobile Application
- 🔌 IoT Integration
- 🔗 ERP Connectors (Odoo, SAP)
- 💬 Microsoft Teams / Slack Integration
- 📊 Power BI Connector
- 🏅 ESG Benchmarking against industry standards
