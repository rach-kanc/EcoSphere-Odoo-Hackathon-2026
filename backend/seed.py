"""EcoSphere seed script — populates SQLite with realistic demo data.

Run once after creating the schema:
    python -X utf8 seed.py

Safe to re-run: checks for existing data before inserting.

Includes teammate's seed_categories() for compatibility.
"""
from __future__ import annotations

import sys
import io
from datetime import date, timedelta

# Force UTF-8 output on Windows so emoji print correctly
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Make sure the app package is importable when running from backend/
sys.path.insert(0, ".")

from app.core.database import Base, SessionLocal, engine
import app.models  # noqa: F401 — registers all models on Base.metadata

from app.models.user import User, UserRole
from app.models.department import Department, DeptStatus
from app.models.category import Category, CategoryType, CategoryStatus
from app.models.emission_factor import EmissionFactor, ActivityType
from app.models.carbon_transaction import CarbonTransaction, TransactionSource
from app.models.environmental_goal import EnvironmentalGoal, GoalStatus
from app.models.csr_activity import CSRActivity, ActivityStatus, EmployeeParticipation, ParticipationStatus
from app.models.policy import ESGPolicy, PolicyType, PolicyStatus, PolicyAcknowledgement
from app.models.audit import Audit, AuditStatus, ComplianceIssue, IssueSeverity, IssueStatus
from app.models.challenge import Challenge, ChallengeDifficulty, ChallengeStatus, ChallengeParticipation
from app.models.challenge import ParticipationStatus as ChallengeParticipationStatus
from app.models.badge import Badge, BadgeRarity, UserBadge
from app.models.reward import Reward, RewardStatus, RewardRedemption, RedemptionStatus
from app.models.department_score import DepartmentScore
from app.models.notification import Notification, NotificationType

TODAY = date.today()


# ---------------------------------------------------------------------------
# Teammate-compatible helper (kept for import compatibility with category stack)
# ---------------------------------------------------------------------------
def seed_categories() -> None:
    """Seed default CSR categories — compatible with category_service.seed_default_csr_categories."""
    from app.services.category_service import CategoryService
    db = SessionLocal()
    try:
        service = CategoryService(db)
        service.seed_default_csr_categories(
            ["Environment", "Education", "Health", "Community"]
        )
        db.commit()
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Full demo seed
# ---------------------------------------------------------------------------
def seed() -> None:
    # Create all tables
    Base.metadata.create_all(engine)

    with SessionLocal() as db:
        # Guard: skip if already seeded
        if db.query(User).count() > 0:
            print("Database already seeded - skipping.")
            return

        print("Seeding EcoSphere demo data...")

        # ── Departments ──────────────────────────────────────────────────────
        depts = {
            "ENG": Department(name="Engineering", code="ENG", employee_count=42, status=DeptStatus.ACTIVE),
            "OPS": Department(name="Operations", code="OPS", employee_count=35, status=DeptStatus.ACTIVE),
            "HR":  Department(name="Human Resources", code="HR", employee_count=18, status=DeptStatus.ACTIVE),
            "FIN": Department(name="Finance", code="FIN", employee_count=22, status=DeptStatus.ACTIVE),
            "SCM": Department(name="Supply Chain", code="SCM", employee_count=28, status=DeptStatus.ACTIVE),
        }
        for d in depts.values():
            db.add(d)
        db.flush()

        # ── Users ────────────────────────────────────────────────────────────
        # Passwords are plain "password123" — for demo only
        DEMO_HASH = "$2b$12$KIX8J4FfIpuUfTdvmHklHuZ5QfEovTWQ7fYgvJ4m3rA9yH9Y5KLo6"

        admin = User(email="admin@ecosphere.dev", hashed_password=DEMO_HASH,
                     full_name="System Admin", role=UserRole.SYSTEM_ADMIN,
                     department_id=depts["ENG"].id, xp_points=0)
        mgr_esg = User(email="esg.manager@ecosphere.dev", hashed_password=DEMO_HASH,
                       full_name="Priya Sharma", role=UserRole.ESG_MANAGER,
                       department_id=depts["HR"].id, xp_points=200)
        mgr_dept = User(email="dept.manager@ecosphere.dev", hashed_password=DEMO_HASH,
                        full_name="Arjun Mehta", role=UserRole.DEPT_MANAGER,
                        department_id=depts["ENG"].id, xp_points=450)
        auditor = User(email="auditor@ecosphere.dev", hashed_password=DEMO_HASH,
                       full_name="Kavita Nair", role=UserRole.AUDITOR,
                       department_id=depts["FIN"].id, xp_points=100)

        # Employees with varied XP for leaderboard
        emp1 = User(email="jane.smith@ecosphere.dev", hashed_password=DEMO_HASH,
                    full_name="Jane Smith", role=UserRole.EMPLOYEE,
                    department_id=depts["ENG"].id, xp_points=2450, level=24)
        emp2 = User(email="raj.kumar@ecosphere.dev", hashed_password=DEMO_HASH,
                    full_name="Raj Kumar", role=UserRole.EMPLOYEE,
                    department_id=depts["OPS"].id, xp_points=1890, level=18)
        emp3 = User(email="alice.wong@ecosphere.dev", hashed_password=DEMO_HASH,
                    full_name="Alice Wong", role=UserRole.EMPLOYEE,
                    department_id=depts["HR"].id, xp_points=1600, level=16)
        emp4 = User(email="sameer.patel@ecosphere.dev", hashed_password=DEMO_HASH,
                    full_name="Sameer Patel", role=UserRole.EMPLOYEE,
                    department_id=depts["SCM"].id, xp_points=1200, level=12)
        emp5 = User(email="linda.chen@ecosphere.dev", hashed_password=DEMO_HASH,
                    full_name="Linda Chen", role=UserRole.EMPLOYEE,
                    department_id=depts["FIN"].id, xp_points=980, level=9)
        emp6 = User(email="tom.baker@ecosphere.dev", hashed_password=DEMO_HASH,
                    full_name="Tom Baker", role=UserRole.EMPLOYEE,
                    department_id=depts["ENG"].id, xp_points=750, level=7)

        all_users = [admin, mgr_esg, mgr_dept, auditor, emp1, emp2, emp3, emp4, emp5, emp6]
        for u in all_users:
            db.add(u)
        db.flush()

        depts["ENG"].head_id = mgr_dept.id
        depts["HR"].head_id = mgr_esg.id
        db.flush()

        # ── Categories — use teammate's enum values (CSR_ACTIVITY / CHALLENGE) ──
        cats = {
            "tree":      Category(name="Tree Plantation", type=CategoryType.CSR_ACTIVITY, status=CategoryStatus.ACTIVE),
            "blood":     Category(name="Blood Donation", type=CategoryType.CSR_ACTIVITY, status=CategoryStatus.ACTIVE),
            "community": Category(name="Community Service", type=CategoryType.CSR_ACTIVITY, status=CategoryStatus.ACTIVE),
            "energy":    Category(name="Energy Saving", type=CategoryType.CHALLENGE, status=CategoryStatus.ACTIVE),
            "waste":     Category(name="Waste Reduction", type=CategoryType.CHALLENGE, status=CategoryStatus.ACTIVE),
            "transport": Category(name="Sustainable Transport", type=CategoryType.CHALLENGE, status=CategoryStatus.ACTIVE),
            "water":     Category(name="Water Conservation", type=CategoryType.CHALLENGE, status=CategoryStatus.ACTIVE),
        }
        for c in cats.values():
            db.add(c)
        db.flush()

        # ── Emission Factors ─────────────────────────────────────────────────
        factors = [
            EmissionFactor.new_version(db, factor_code="grid.electricity.in",
                name="India Grid Electricity", activity_type=ActivityType.ELECTRICITY,
                unit="kWh", co2e_per_unit=0.82, effective_start=date(2024, 1, 1), source="CEA 2024"),
            EmissionFactor.new_version(db, factor_code="fuel.diesel",
                name="Diesel (road)", activity_type=ActivityType.FUEL,
                unit="litre", co2e_per_unit=2.68, effective_start=date(2024, 1, 1), source="IPCC 2024"),
            EmissionFactor.new_version(db, factor_code="fuel.petrol",
                name="Petrol (road)", activity_type=ActivityType.FUEL,
                unit="litre", co2e_per_unit=2.31, effective_start=date(2024, 1, 1), source="IPCC 2024"),
            EmissionFactor.new_version(db, factor_code="travel.air.economy",
                name="Air Travel - Economy", activity_type=ActivityType.TRAVEL,
                unit="km", co2e_per_unit=0.15, effective_start=date(2024, 1, 1), source="DEFRA 2024"),
            EmissionFactor.new_version(db, factor_code="waste.landfill",
                name="Landfill Waste", activity_type=ActivityType.WASTE,
                unit="kg", co2e_per_unit=0.45, effective_start=date(2024, 1, 1), source="EPA 2024"),
            EmissionFactor.new_version(db, factor_code="water.supply",
                name="Water Supply & Treatment", activity_type=ActivityType.WATER,
                unit="m3", co2e_per_unit=0.34, effective_start=date(2024, 1, 1), source="WRAP 2024"),
        ]
        db.flush()
        ef_elec, ef_diesel, ef_petrol, ef_air, ef_waste, ef_water = factors

        # ── Carbon Transactions ───────────────────────────────────────────────
        txns = [
            CarbonTransaction(department_id=depts["ENG"].id, emission_factor_id=ef_elec.id,
                source=TransactionSource.MANUAL, quantity=5200, calculated_emission=4264.0,
                date=TODAY - timedelta(days=150), notes="Server room Q1"),
            CarbonTransaction(department_id=depts["ENG"].id, emission_factor_id=ef_elec.id,
                source=TransactionSource.MANUAL, quantity=4800, calculated_emission=3936.0,
                date=TODAY - timedelta(days=90)),
            CarbonTransaction(department_id=depts["ENG"].id, emission_factor_id=ef_elec.id,
                source=TransactionSource.MANUAL, quantity=4100, calculated_emission=3362.0,
                date=TODAY - timedelta(days=30)),
            CarbonTransaction(department_id=depts["OPS"].id, emission_factor_id=ef_diesel.id,
                source=TransactionSource.FLEET, quantity=800, calculated_emission=2144.0,
                date=TODAY - timedelta(days=120)),
            CarbonTransaction(department_id=depts["OPS"].id, emission_factor_id=ef_diesel.id,
                source=TransactionSource.FLEET, quantity=650, calculated_emission=1742.0,
                date=TODAY - timedelta(days=60)),
            CarbonTransaction(department_id=depts["FIN"].id, emission_factor_id=ef_air.id,
                source=TransactionSource.EXPENSE, quantity=12000, calculated_emission=1800.0,
                date=TODAY - timedelta(days=100), notes="Q1 client visits"),
            CarbonTransaction(department_id=depts["SCM"].id, emission_factor_id=ef_waste.id,
                source=TransactionSource.MANUAL, quantity=2000, calculated_emission=900.0,
                date=TODAY - timedelta(days=45)),
        ]
        for t in txns:
            db.add(t)
        db.flush()

        # ── Environmental Goals ───────────────────────────────────────────────
        goals = [
            EnvironmentalGoal(title="Reduce Electricity Emissions by 20%",
                description="Cut server room and office electricity by 20% vs 2024 baseline.",
                department_id=depts["ENG"].id,
                target_value=3200, current_value=3362, unit="kgCO2e",
                baseline_value=4264, deadline=date(2025, 12, 31), status=GoalStatus.AT_RISK),
            EnvironmentalGoal(title="Fleet Diesel Reduction - 15%",
                description="Transition 15% of fleet to CNG or EV.",
                department_id=depts["OPS"].id,
                target_value=1570, current_value=1742, unit="kgCO2e",
                baseline_value=2144, deadline=date(2025, 9, 30), status=GoalStatus.AT_RISK),
            EnvironmentalGoal(title="Net Zero by 2030",
                description="Organisation-wide carbon neutrality target.",
                target_value=0, current_value=18148, unit="kgCO2e",
                baseline_value=24000, deadline=date(2030, 12, 31), status=GoalStatus.ON_TRACK),
            EnvironmentalGoal(title="Zero Landfill Waste",
                description="Divert all waste from landfill via recycling and composting.",
                department_id=depts["SCM"].id,
                target_value=0, current_value=900, unit="kgCO2e",
                baseline_value=2000, deadline=date(2026, 6, 30), status=GoalStatus.ON_TRACK),
        ]
        for g in goals:
            db.add(g)
        db.flush()

        # ── CSR Activities ────────────────────────────────────────────────────
        csr1 = CSRActivity(title="City Tree Plantation Drive",
            description="Plant 500 native trees in the local park with community volunteers.",
            category_id=cats["tree"].id, date=TODAY - timedelta(days=20),
            location="Cubbon Park, Bengaluru", max_participants=50, xp_reward=150,
            evidence_required=True, status=ActivityStatus.COMPLETED)
        csr2 = CSRActivity(title="Blood Donation Camp",
            description="Quarterly blood donation drive in partnership with Red Cross.",
            category_id=cats["blood"].id, date=TODAY + timedelta(days=10),
            location="Company Premises", max_participants=100, xp_reward=200,
            evidence_required=False, status=ActivityStatus.UPCOMING)
        csr3 = CSRActivity(title="Community Clean-Up Weekend",
            description="Beach and park clean-up with local NGO.",
            category_id=cats["community"].id, date=TODAY - timedelta(days=5),
            location="Juhu Beach, Mumbai", max_participants=30, xp_reward=100,
            evidence_required=True, status=ActivityStatus.ONGOING)
        db.add_all([csr1, csr2, csr3])
        db.flush()

        parts = [
            EmployeeParticipation(employee_id=emp1.id, activity_id=csr1.id,
                proof_url="https://example.com/proof/csr1_emp1.jpg",
                status=ParticipationStatus.APPROVED, points_earned=150,
                completion_date=TODAY - timedelta(days=20), approved_by_id=mgr_esg.id),
            EmployeeParticipation(employee_id=emp2.id, activity_id=csr1.id,
                proof_url="https://example.com/proof/csr1_emp2.jpg",
                status=ParticipationStatus.APPROVED, points_earned=150,
                completion_date=TODAY - timedelta(days=20), approved_by_id=mgr_esg.id),
            EmployeeParticipation(employee_id=emp3.id, activity_id=csr3.id,
                status=ParticipationStatus.PENDING, points_earned=0),
            EmployeeParticipation(employee_id=emp4.id, activity_id=csr3.id,
                proof_url="https://example.com/proof/csr3_emp4.jpg",
                status=ParticipationStatus.PENDING, points_earned=0),
        ]
        for p in parts:
            db.add(p)
        db.flush()

        # ── ESG Policies ──────────────────────────────────────────────────────
        policies = [
            ESGPolicy(title="Anti-Bribery & Corruption Policy",
                type=PolicyType.ANTI_BRIBERY, version="2.1",
                content="Zero tolerance for bribery in all business dealings.",
                effective_date=date(2024, 1, 1), status=PolicyStatus.ACTIVE),
            ESGPolicy(title="Data Privacy Policy",
                type=PolicyType.DATA_PRIVACY, version="3.0",
                content="Compliant with GDPR and India PDPB 2023.",
                effective_date=date(2024, 3, 1), status=PolicyStatus.ACTIVE),
            ESGPolicy(title="Environmental Management Policy",
                type=PolicyType.ENVIRONMENTAL, version="1.5",
                content="Commitment to ISO 14001 and carbon reduction targets.",
                effective_date=date(2024, 6, 1), status=PolicyStatus.ACTIVE),
            ESGPolicy(title="Code of Conduct",
                type=PolicyType.CODE_OF_CONDUCT, version="4.0",
                content="Ethical standards for all employees and contractors.",
                effective_date=date(2025, 1, 1), status=PolicyStatus.DRAFT),
        ]
        for pol in policies:
            db.add(pol)
        db.flush()

        for emp in [emp1, emp2, emp3, emp4]:
            db.add(PolicyAcknowledgement(policy_id=policies[0].id, employee_id=emp.id,
                signature_text="I have read and accept this policy."))
            db.add(PolicyAcknowledgement(policy_id=policies[1].id, employee_id=emp.id,
                signature_text="I have read and accept this policy."))
        db.flush()

        # ── Audits & Compliance Issues ────────────────────────────────────────
        audit1 = Audit(title="Q1 2025 Environmental Compliance Audit",
            auditor_id=auditor.id, department_id=depts["OPS"].id,
            date=date(2025, 3, 15), status=AuditStatus.COMPLETED,
            notes="Reviewed fleet emissions and waste disposal processes.")
        audit2 = Audit(title="Data Privacy Audit - Engineering",
            auditor_id=auditor.id, department_id=depts["ENG"].id,
            date=TODAY + timedelta(days=15), status=AuditStatus.PLANNED)
        db.add_all([audit1, audit2])
        db.flush()

        issues = [
            ComplianceIssue(audit_id=audit1.id,
                title="Diesel vehicles not tracked in ERP",
                description="3 fleet vehicles missing from emission tracking system.",
                severity=IssueSeverity.HIGH, owner_id=mgr_dept.id,
                due_date=TODAY - timedelta(days=5), status=IssueStatus.OVERDUE),
            ComplianceIssue(audit_id=audit1.id,
                title="Waste disposal records incomplete",
                description="Q4 2024 waste manifests missing for 2 sites.",
                severity=IssueSeverity.MEDIUM, owner_id=emp4.id,
                due_date=TODAY + timedelta(days=14), status=IssueStatus.IN_PROGRESS),
            ComplianceIssue(audit_id=audit1.id,
                title="Training records not updated",
                description="Environmental training completion records outdated.",
                severity=IssueSeverity.LOW, owner_id=mgr_esg.id,
                due_date=TODAY + timedelta(days=30), status=IssueStatus.OPEN),
        ]
        for i in issues:
            db.add(i)
        db.flush()

        # ── Challenges ────────────────────────────────────────────────────────
        challenges = [
            Challenge(title="30-Day Zero Single-Use Plastic",
                description="Eliminate single-use plastic from your daily routine for 30 days. Document your journey.",
                category_id=cats["waste"].id, xp_reward=300,
                difficulty=ChallengeDifficulty.MEDIUM,
                deadline=TODAY + timedelta(days=30), evidence_required=True,
                status=ChallengeStatus.ACTIVE, created_by_id=mgr_esg.id),
            Challenge(title="Cycle to Work Week",
                description="Cycle or walk to work every day for a full week. Earn extra XP for each day logged.",
                category_id=cats["transport"].id, xp_reward=200,
                difficulty=ChallengeDifficulty.EASY,
                deadline=TODAY + timedelta(days=14), evidence_required=False,
                status=ChallengeStatus.ACTIVE, created_by_id=mgr_esg.id),
            Challenge(title="Office Energy Detective",
                description="Identify and fix 5 energy waste sources in your office area. Submit a report.",
                category_id=cats["energy"].id, xp_reward=500,
                difficulty=ChallengeDifficulty.HARD,
                deadline=TODAY + timedelta(days=60), evidence_required=True,
                status=ChallengeStatus.ACTIVE, created_by_id=mgr_esg.id),
            Challenge(title="Green Lunch Challenge",
                description="Bring a plant-based lunch every day for 2 weeks. Share photos in the team channel.",
                category_id=cats["waste"].id, xp_reward=150,
                difficulty=ChallengeDifficulty.EASY,
                deadline=TODAY - timedelta(days=2), evidence_required=False,
                status=ChallengeStatus.UNDER_REVIEW, created_by_id=mgr_esg.id),
            Challenge(title="Water Footprint Audit",
                description="Measure and report your team's monthly water usage and suggest 3 reduction strategies.",
                category_id=cats["water"].id, xp_reward=400,
                difficulty=ChallengeDifficulty.HARD,
                deadline=TODAY + timedelta(days=90), evidence_required=True,
                status=ChallengeStatus.DRAFT, created_by_id=mgr_esg.id),
            Challenge(title="Paperless Office Sprint",
                description="Go completely paperless for one month. Track every instance where you replaced paper.",
                category_id=cats["waste"].id, xp_reward=250,
                difficulty=ChallengeDifficulty.MEDIUM,
                deadline=TODAY - timedelta(days=30), evidence_required=True,
                status=ChallengeStatus.COMPLETED, created_by_id=mgr_esg.id),
        ]
        for ch in challenges:
            db.add(ch)
        db.flush()

        PS = ChallengeParticipationStatus
        cp_data = [
            ChallengeParticipation(challenge_id=challenges[0].id, employee_id=emp1.id,
                progress=65, status=PS.IN_PROGRESS, xp_awarded=0),
            ChallengeParticipation(challenge_id=challenges[0].id, employee_id=emp2.id,
                progress=40, status=PS.IN_PROGRESS, xp_awarded=0),
            ChallengeParticipation(challenge_id=challenges[1].id, employee_id=emp3.id,
                progress=100, proof_url="https://example.com/proof/ch2_emp3.jpg",
                status=PS.SUBMITTED, xp_awarded=0),
            ChallengeParticipation(challenge_id=challenges[3].id, employee_id=emp1.id,
                progress=100, proof_url="https://example.com/proof/ch4_emp1.jpg",
                status=PS.SUBMITTED, xp_awarded=0),
            ChallengeParticipation(challenge_id=challenges[5].id, employee_id=emp4.id,
                progress=100, proof_url="https://example.com/proof/ch6_emp4.jpg",
                status=PS.APPROVED, xp_awarded=250),
            ChallengeParticipation(challenge_id=challenges[5].id, employee_id=emp5.id,
                progress=100, status=PS.APPROVED, xp_awarded=250),
        ]
        for cp in cp_data:
            db.add(cp)
        db.flush()

        # ── Badges ────────────────────────────────────────────────────────────
        badges = [
            Badge(name="First Step", description="Earn your first 100 XP.",
                icon_url="leaf", rarity=BadgeRarity.COMMON,
                unlock_rule={"type": "xp_threshold", "value": 100}),
            Badge(name="Quick Starter", description="Reach 500 XP.",
                icon_url="zap", rarity=BadgeRarity.COMMON,
                unlock_rule={"type": "xp_threshold", "value": 500}),
            Badge(name="Rising Star", description="Reach 1000 XP.",
                icon_url="star", rarity=BadgeRarity.RARE,
                unlock_rule={"type": "xp_threshold", "value": 1000}),
            Badge(name="Sustainability Champion", description="Reach 2000 XP.",
                icon_url="trophy", rarity=BadgeRarity.EPIC,
                unlock_rule={"type": "xp_threshold", "value": 2000}),
            Badge(name="ESG Legend", description="Reach 5000 XP.",
                icon_url="gem", rarity=BadgeRarity.LEGENDARY,
                unlock_rule={"type": "xp_threshold", "value": 5000}),
            Badge(name="Challenge Starter", description="Complete your first challenge.",
                icon_url="target", rarity=BadgeRarity.COMMON,
                unlock_rule={"type": "challenges_completed", "value": 1}),
            Badge(name="Challenge Master", description="Complete 5 challenges.",
                icon_url="flame", rarity=BadgeRarity.RARE,
                unlock_rule={"type": "challenges_completed", "value": 5}),
            Badge(name="CSR Hero", description="Participate in 3 CSR activities.",
                icon_url="handshake", rarity=BadgeRarity.RARE,
                unlock_rule={"type": "csr_count", "value": 3}),
        ]
        for b in badges:
            db.add(b)
        db.flush()

        earned = [
            UserBadge(user_id=emp1.id, badge_id=badges[0].id),
            UserBadge(user_id=emp1.id, badge_id=badges[1].id),
            UserBadge(user_id=emp1.id, badge_id=badges[2].id),
            UserBadge(user_id=emp1.id, badge_id=badges[3].id),
            UserBadge(user_id=emp2.id, badge_id=badges[0].id),
            UserBadge(user_id=emp2.id, badge_id=badges[1].id),
            UserBadge(user_id=emp2.id, badge_id=badges[2].id),
            UserBadge(user_id=emp3.id, badge_id=badges[0].id),
            UserBadge(user_id=emp3.id, badge_id=badges[1].id),
            UserBadge(user_id=emp4.id, badge_id=badges[0].id),
            UserBadge(user_id=emp5.id, badge_id=badges[0].id),
            UserBadge(user_id=emp4.id, badge_id=badges[5].id),
        ]
        for ub in earned:
            db.add(ub)
        db.flush()

        # ── Rewards ───────────────────────────────────────────────────────────
        rewards = [
            Reward(name="Plant a Tree in Your Name",
                description="We plant a native tree on your behalf and send you a certificate.",
                icon_url="tree", points_required=200, stock=500, status=RewardStatus.AVAILABLE),
            Reward(name="Coffee Voucher",
                description="Rs 200 coffee shop voucher.",
                icon_url="coffee", points_required=150, stock=50, status=RewardStatus.AVAILABLE),
            Reward(name="Eco T-Shirt",
                description="Organic cotton EcoSphere branded t-shirt.",
                icon_url="shirt", points_required=500, stock=30, status=RewardStatus.AVAILABLE),
            Reward(name="One Day WFH Pass",
                description="Extra work-from-home day, any Friday.",
                icon_url="home", points_required=800, stock=20, status=RewardStatus.AVAILABLE),
            Reward(name="Eco Tote Bag",
                description="Reusable jute shopping bag with EcoSphere branding.",
                icon_url="bag", points_required=100, stock=100, status=RewardStatus.AVAILABLE),
            Reward(name="Sustainability Masterclass",
                description="Access to a premium online sustainability certification course.",
                icon_url="book", points_required=1000, stock=10, status=RewardStatus.AVAILABLE),
        ]
        for r in rewards:
            db.add(r)
        db.flush()

        db.add(RewardRedemption(reward_id=rewards[0].id, employee_id=emp1.id,
            xp_spent=200, status=RedemptionStatus.FULFILLED))
        db.add(RewardRedemption(reward_id=rewards[1].id, employee_id=emp2.id,
            xp_spent=150, status=RedemptionStatus.PENDING))
        db.flush()

        # ── Department ESG Scores ─────────────────────────────────────────────
        score_data = [
            DepartmentScore(department_id=depts["ENG"].id, period=date(2025, 6, 1),
                environmental_score=62, social_score=74, governance_score=81,
                total_score=round(62*0.4 + 74*0.3 + 81*0.3, 1)),
            DepartmentScore(department_id=depts["OPS"].id, period=date(2025, 6, 1),
                environmental_score=48, social_score=70, governance_score=75,
                total_score=round(48*0.4 + 70*0.3 + 75*0.3, 1)),
            DepartmentScore(department_id=depts["HR"].id, period=date(2025, 6, 1),
                environmental_score=71, social_score=88, governance_score=90,
                total_score=round(71*0.4 + 88*0.3 + 90*0.3, 1)),
            DepartmentScore(department_id=depts["FIN"].id, period=date(2025, 6, 1),
                environmental_score=55, social_score=65, governance_score=85,
                total_score=round(55*0.4 + 65*0.3 + 85*0.3, 1)),
            DepartmentScore(department_id=depts["SCM"].id, period=date(2025, 6, 1),
                environmental_score=67, social_score=72, governance_score=78,
                total_score=round(67*0.4 + 72*0.3 + 78*0.3, 1)),
        ]
        for s in score_data:
            db.add(s)
        db.flush()

        # ── Notifications ─────────────────────────────────────────────────────
        notifs = [
            Notification(recipient_id=emp1.id, type=NotificationType.BADGE_UNLOCKED,
                title="Badge Unlocked: Sustainability Champion",
                message="You've earned 2000 XP! The Sustainability Champion badge is now yours.",
                is_read=False, related_id=badges[3].id),
            Notification(recipient_id=emp2.id, type=NotificationType.CHALLENGE_APPROVED,
                title="Challenge Approved",
                message="Your submission for 'Paperless Office Sprint' has been approved. +250 XP awarded!",
                is_read=True),
            Notification(recipient_id=mgr_dept.id, type=NotificationType.COMPLIANCE_ISSUE_OVERDUE,
                title="Compliance Issue Overdue",
                message="'Diesel vehicles not tracked in ERP' is past its due date. Immediate action required.",
                is_read=False, related_id=issues[0].id),
            Notification(recipient_id=emp3.id, type=NotificationType.CSR_APPROVED,
                title="CSR Participation Approved",
                message="Your participation in 'City Tree Plantation Drive' has been approved. +150 XP!",
                is_read=False),
        ]
        for n in notifs:
            db.add(n)

        db.commit()
        print("Seeding complete!")
        print(f"\n  Users:               {len(all_users)}")
        print(f"  Departments:         {len(depts)}")
        print(f"  Emission Factors:    {len(factors)}")
        print(f"  Carbon Transactions: {len(txns)}")
        print(f"  Environmental Goals: {len(goals)}")
        print(f"  CSR Activities:      3")
        print(f"  Policies:            {len(policies)}")
        print(f"  Challenges:          {len(challenges)}")
        print(f"  Badges:              {len(badges)}")
        print(f"  Rewards:             {len(rewards)}")
        print(f"  Department Scores:   {len(score_data)}")
        print(f"\n  Login: admin@ecosphere.dev / password123")
        print(f"  Login: jane.smith@ecosphere.dev / password123  (top employee)")


if __name__ == "__main__":
    seed()
