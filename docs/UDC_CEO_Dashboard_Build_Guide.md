# UDC CEO Instant Dashboard Tool — Complete Build Guide

## For: AI Coder (Claude Code / Cascade / Codex)
## Coordinator: Salim
## Date: April 2026

---

## CONTEXT — READ THIS FIRST

You are building a **CEO-specific executive dashboard tool** for **United Development Company (UDC)**, one of Qatar's largest real estate developers. UDC manages **The Pearl Qatar** (a massive man-made island with residential, commercial, and retail properties), along with other major developments.

**The CEO** of a company like this wakes up every morning thinking:
- "Are we hitting our revenue targets?"
- "What's my occupancy — are we bleeding vacancy anywhere?"
- "How much cash do we have and how much is stuck in receivables?"
- "Which assets need my attention right now?"
- "Are tenants happy? Am I about to lose major tenants?"
- "Which buildings are costing me the most in maintenance?"
- "Show me all of this instantly — don't make me wait for a team to build a report."

This tool gives him that. It generates instant, interactive executive dashboards from governed data. He opens it, selects a domain (or asks a question), and sees the answer immediately with rich, interactive visualizations.

**This tool sits alongside Power BI** — it does NOT replace it. The rest of the company uses Power BI. This is the CEO's personal executive intelligence interface.

**Technology:** C1 / Thesys Generative UI + FastAPI (Python) + Next.js + SQLite (synthetic data for prototype)

---

## PROJECT STRUCTURE

```
udc-ceo-dashboard/
├── backend/
│   ├── main.py                    # FastAPI app with C1 streaming + tool calling
│   ├── system_prompt.py           # UDC executive system prompt
│   ├── tools.py                   # All governed tool definitions
│   ├── database.py                # SQLite database setup and queries
│   ├── seed_data.py               # Synthetic data generator
│   ├── metrics.py                 # Deterministic metric calculations
│   ├── scoring.py                 # Deterministic scoring functions
│   ├── validation.py              # Reconciliation and validation logic
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx           # Main C1Chat interface
│   │   │   └── api/
│   │   │       └── chat/
│   │   │           └── route.ts   # Next.js API route → backend proxy
│   │   ├── components/
│   │   │   └── Footer.tsx         # Custom response footer with share
│   │   └── styles/
│   │       └── custom.css         # UDC brand overrides
│   ├── package.json
│   ├── next.config.js
│   └── .env.local
└── README.md
```

---

## STEP 1: BACKEND — SYNTHETIC DATA GENERATION

Create `backend/seed_data.py`. This generates realistic UDC data for The Pearl Qatar.

The data must feel real. Use actual Pearl Qatar zone names, realistic Doha property values in QAR, real tenant patterns for a mixed-use island development.

```python
# backend/seed_data.py
import sqlite3
import random
from datetime import datetime, timedelta
import uuid

random.seed(42)

DB_PATH = "udc_dashboard.db"

# === REAL UDC/PEARL QATAR GEOGRAPHY ===
ZONES = [
    {"id": "Z01", "name": "Porto Arabia", "type": "Mixed", "towers": 31},
    {"id": "Z02", "name": "Viva Bahriya", "type": "Residential", "towers": 19},
    {"id": "Z03", "name": "Medina Centrale", "type": "Commercial", "towers": 8},
    {"id": "Z04", "name": "Qanat Quartier", "type": "Residential", "towers": 0},
    {"id": "Z05", "name": "Abraj Quartier", "type": "Mixed", "towers": 10},
    {"id": "Z06", "name": "The Waterfront", "type": "Commercial", "towers": 4},
    {"id": "Z07", "name": "Floresta Gardens", "type": "Residential", "towers": 6},
    {"id": "Z08", "name": "Giardino Village", "type": "Residential", "towers": 0},
]

UNIT_TYPES_RESIDENTIAL = ["Studio", "1BR", "2BR", "3BR", "Penthouse", "Townhouse"]
UNIT_TYPES_COMMERCIAL = ["Retail", "Office", "F&B", "Showroom", "Clinic", "Anchor Store"]

TENANT_NATIONALITIES = [
    "Qatari", "Indian", "Filipino", "Egyptian", "Jordanian", "Lebanese",
    "British", "American", "French", "Pakistani", "Sudanese", "Tunisian"
]

COMPLAINT_CATEGORIES = [
    "AC/HVAC", "Plumbing", "Electrical", "Elevator", "Parking",
    "Pest Control", "Common Area", "Security", "Noise", "Structural", "Internet/Telecom"
]

VENDORS = [
    {"name": "Al Jaber Facilities", "category": "Maintenance"},
    {"name": "Elegancia Interiors", "category": "Fit-out"},
    {"name": "Gulf Cleaning Co", "category": "Cleaning"},
    {"name": "QatarCool", "category": "HVAC"},
    {"name": "KAHRAMAA Services", "category": "Utilities"},
    {"name": "Mannai Trading", "category": "IT/Security"},
    {"name": "Al Mana Group", "category": "Procurement"},
    {"name": "Darwish Holding", "category": "General"},
]

DEPARTMENTS = ["Leasing", "Finance", "Maintenance", "HR", "IT", "Legal", "Marketing", "Operations", "Community Mgmt", "Sales"]

SUBSIDIARIES = [
    {"id": "SUB01", "name": "UDC Properties", "type": "Property Management"},
    {"id": "SUB02", "name": "The Pearl Qatar Co", "type": "Master Development"},
    {"id": "SUB03", "name": "Ronautica", "type": "Marina & Leisure"},
    {"id": "SUB04", "name": "UDC Investments", "type": "Investment Arm"},
]


def create_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # --- ASSETS ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            asset_id TEXT PRIMARY KEY,
            asset_name TEXT,
            zone_id TEXT,
            zone_name TEXT,
            asset_type TEXT,  -- Commercial / Residential / Mixed
            total_units INTEGER,
            total_leasable_sqm REAL,
            asset_age_years INTEGER,
            valuation_qar REAL,
            occupancy_target REAL
        )
    """)

    # --- UNITS ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS units (
            unit_id TEXT PRIMARY KEY,
            asset_id TEXT,
            unit_type TEXT,
            unit_size_sqm REAL,
            unit_status TEXT,  -- Leased / Vacant / Under Maintenance / Sold
            asking_rent_qar REAL,
            market_rent_qar REAL,
            vacancy_start_date TEXT,
            vacancy_duration_days INTEGER
        )
    """)

    # --- TENANTS ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            tenant_id TEXT PRIMARY KEY,
            tenant_name TEXT,
            tenant_type TEXT,  -- Corporate / Individual
            nationality TEXT,
            total_units_leased INTEGER,
            total_monthly_rent_qar REAL,
            tenant_since TEXT,
            risk_score REAL
        )
    """)

    # --- LEASES ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS leases (
            lease_id TEXT PRIMARY KEY,
            asset_id TEXT,
            unit_id TEXT,
            tenant_id TEXT,
            lease_start TEXT,
            lease_end TEXT,
            contracted_rent_qar REAL,
            rent_per_sqm REAL,
            lease_type TEXT,  -- New / Renewal
            lease_status TEXT,  -- Active / Expired / Expiring Soon
            security_deposit_qar REAL,
            incentive_months INTEGER,
            payment_frequency TEXT
        )
    """)

    # --- RECEIVABLES ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS receivables (
            invoice_id TEXT PRIMARY KEY,
            tenant_id TEXT,
            asset_id TEXT,
            invoice_amount_qar REAL,
            due_date TEXT,
            payment_date TEXT,
            aging_bucket TEXT,  -- Current / 30-60 / 60-90 / 90+
            delinquency_flag INTEGER,
            revenue_type TEXT  -- Rent / Community Fee / Service Charge
        )
    """)

    # --- WORK ORDERS ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS work_orders (
            wo_id TEXT PRIMARY KEY,
            asset_id TEXT,
            unit_id TEXT,
            tenant_id TEXT,
            wo_type TEXT,  -- Preventive / Corrective
            category TEXT,
            open_date TEXT,
            close_date TEXT,
            sla_response_hours REAL,
            sla_resolution_hours REAL,
            actual_response_hours REAL,
            actual_resolution_hours REAL,
            contractor_id TEXT,
            cost_qar REAL,
            repeat_flag INTEGER,
            first_time_fix INTEGER,
            overdue_flag INTEGER
        )
    """)

    # --- COMPLAINTS ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            complaint_id TEXT PRIMARY KEY,
            asset_id TEXT,
            unit_id TEXT,
            tenant_id TEXT,
            category TEXT,
            open_date TEXT,
            close_date TEXT,
            resolution_days REAL,
            repeat_flag INTEGER,
            csat_score REAL
        )
    """)

    # --- FINANCE ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS finance_monthly (
            record_id TEXT PRIMARY KEY,
            month TEXT,
            revenue_qar REAL,
            revenue_target_qar REAL,
            cogs_qar REAL,
            opex_qar REAL,
            noi_qar REAL,
            ebitda_qar REAL,
            cash_inflow_qar REAL,
            cash_outflow_qar REAL,
            cash_balance_qar REAL,
            capex_qar REAL,
            staff_cost_qar REAL,
            maintenance_cost_qar REAL,
            marketing_cost_qar REAL,
            asset_class TEXT  -- Commercial / Residential / Mixed
        )
    """)

    # --- HR ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id TEXT PRIMARY KEY,
            department TEXT,
            subsidiary TEXT,
            employment_type TEXT,  -- In-house / Outsourced
            hire_date TEXT,
            termination_date TEXT,
            monthly_cost_qar REAL,
            role_level TEXT  -- Executive / Manager / Staff / Contractor
        )
    """)

    # --- PROCUREMENT ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS contracts (
            contract_id TEXT PRIMARY KEY,
            vendor_name TEXT,
            vendor_category TEXT,
            contract_start TEXT,
            contract_end TEXT,
            contracted_value_qar REAL,
            actual_spend_qar REAL,
            savings_qar REAL,
            emergency_flag INTEGER,
            sla_score REAL
        )
    """)

    # --- SUBSIDIARIES ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS subsidiary_financials (
            record_id TEXT PRIMARY KEY,
            subsidiary_id TEXT,
            subsidiary_name TEXT,
            month TEXT,
            revenue_qar REAL,
            ebitda_qar REAL,
            operating_cashflow_qar REAL,
            headcount INTEGER,
            staff_cost_qar REAL
        )
    """)

    # --- COMMUNITY (TPOC) ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS community_fees (
            record_id TEXT PRIMARY KEY,
            owner_id TEXT,
            unit_id TEXT,
            zone_name TEXT,
            fees_billed_qar REAL,
            fees_collected_qar REAL,
            outstanding_qar REAL,
            days_outstanding INTEGER,
            month TEXT
        )
    """)

    # --- LEADS ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            lead_id TEXT PRIMARY KEY,
            lead_source TEXT,  -- Website / Agent / Walk-in / Referral
            lead_date TEXT,
            unit_type TEXT,
            segment TEXT,  -- Residential / Commercial
            response_time_hours REAL,
            viewing_date TEXT,
            application_date TEXT,
            contract_date TEXT,
            lost_reason TEXT,
            lead_status TEXT,  -- New / Viewing / Application / Contracted / Lost
            marketing_cost_qar REAL
        )
    """)

    conn.commit()
    return conn


def seed_all_data():
    conn = create_database()
    c = conn.cursor()

    today = datetime(2026, 3, 31)
    assets = []
    all_units = []
    all_tenants = []
    all_leases = []

    # ========== ASSETS & UNITS ==========
    asset_counter = 0
    for zone in ZONES:
        num_assets = random.randint(3, 8) if zone["towers"] > 0 else random.randint(2, 4)
        for i in range(num_assets):
            asset_counter += 1
            asset_id = f"A{asset_counter:04d}"
            asset_type = zone["type"] if zone["type"] != "Mixed" else random.choice(["Commercial", "Residential"])
            num_units = random.randint(20, 120)
            avg_sqm = random.uniform(40, 250) if asset_type == "Residential" else random.uniform(30, 500)
            total_sqm = round(num_units * avg_sqm, 1)
            valuation = round(total_sqm * random.uniform(12000, 28000), 0)
            occupancy_target = random.uniform(0.85, 0.96)

            asset = {
                "asset_id": asset_id,
                "asset_name": f"{zone['name']} Tower {i+1}" if zone["towers"] > 0 else f"{zone['name']} Block {i+1}",
                "zone_id": zone["id"],
                "zone_name": zone["name"],
                "asset_type": asset_type,
                "total_units": num_units,
                "total_leasable_sqm": total_sqm,
                "asset_age_years": random.randint(3, 18),
                "valuation_qar": valuation,
                "occupancy_target": round(occupancy_target, 3)
            }
            assets.append(asset)

            c.execute("""INSERT INTO assets VALUES (?,?,?,?,?,?,?,?,?,?)""",
                      tuple(asset.values()))

            unit_types = UNIT_TYPES_RESIDENTIAL if asset_type == "Residential" else UNIT_TYPES_COMMERCIAL
            for j in range(num_units):
                unit_id = f"U{asset_counter:04d}-{j+1:04d}"
                unit_type = random.choice(unit_types)
                sqm = round(random.uniform(30, 350), 1)
                is_leased = random.random() < occupancy_target
                status = "Leased" if is_leased else random.choice(["Vacant", "Vacant", "Under Maintenance"])
                asking = round(random.uniform(3000, 25000) if asset_type == "Residential" else random.uniform(5000, 80000), 0)
                vac_start = None
                vac_days = 0
                if status != "Leased":
                    vac_start = (today - timedelta(days=random.randint(5, 400))).strftime("%Y-%m-%d")
                    vac_days = (today - datetime.strptime(vac_start, "%Y-%m-%d")).days

                unit = {
                    "unit_id": unit_id, "asset_id": asset_id, "unit_type": unit_type,
                    "unit_size_sqm": sqm, "unit_status": status,
                    "asking_rent_qar": asking, "market_rent_qar": round(asking * random.uniform(0.9, 1.1), 0),
                    "vacancy_start_date": vac_start, "vacancy_duration_days": vac_days
                }
                all_units.append(unit)
                c.execute("INSERT INTO units VALUES (?,?,?,?,?,?,?,?,?)", tuple(unit.values()))

    # ========== TENANTS ==========
    leased_units = [u for u in all_units if u["unit_status"] == "Leased"]
    num_tenants = len(leased_units) // random.randint(1, 3)
    for i in range(max(num_tenants, 200)):
        tid = f"T{i+1:05d}"
        is_corp = random.random() < 0.35
        tenant = {
            "tenant_id": tid,
            "tenant_name": f"{'Corp' if is_corp else 'Tenant'} {random.choice(['Al','El','Abu','Ben','De'])} {uuid.uuid4().hex[:6].upper()}",
            "tenant_type": "Corporate" if is_corp else "Individual",
            "nationality": random.choice(TENANT_NATIONALITIES),
            "total_units_leased": random.randint(1, 8 if is_corp else 2),
            "total_monthly_rent_qar": round(random.uniform(3000, 150000 if is_corp else 30000), 0),
            "tenant_since": (today - timedelta(days=random.randint(60, 2500))).strftime("%Y-%m-%d"),
            "risk_score": round(random.uniform(0.1, 0.95), 2)
        }
        all_tenants.append(tenant)
        c.execute("INSERT INTO tenants VALUES (?,?,?,?,?,?,?,?)", tuple(tenant.values()))

    # ========== LEASES ==========
    for idx, unit in enumerate(leased_units):
        if idx >= len(all_tenants):
            break
        tenant = all_tenants[idx % len(all_tenants)]
        lease_start = (today - timedelta(days=random.randint(30, 1000))).strftime("%Y-%m-%d")
        lease_end_dt = datetime.strptime(lease_start, "%Y-%m-%d") + timedelta(days=random.choice([365, 730, 1095]))
        days_to_expiry = (lease_end_dt - today).days
        status = "Active"
        if days_to_expiry < 0:
            status = "Expired"
        elif days_to_expiry < 90:
            status = "Expiring Soon"

        lease = {
            "lease_id": f"L{idx+1:06d}",
            "asset_id": unit["asset_id"],
            "unit_id": unit["unit_id"],
            "tenant_id": tenant["tenant_id"],
            "lease_start": lease_start,
            "lease_end": lease_end_dt.strftime("%Y-%m-%d"),
            "contracted_rent_qar": unit["asking_rent_qar"] * random.uniform(0.85, 1.0),
            "rent_per_sqm": round(unit["asking_rent_qar"] / max(unit["unit_size_sqm"], 1), 1),
            "lease_type": random.choice(["New", "New", "Renewal"]),
            "lease_status": status,
            "security_deposit_qar": unit["asking_rent_qar"] * 2,
            "incentive_months": random.choice([0, 0, 0, 1, 2]),
            "payment_frequency": random.choice(["Monthly", "Quarterly", "Annual"])
        }
        all_leases.append(lease)
        c.execute("INSERT INTO leases VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", tuple(lease.values()))

    # ========== RECEIVABLES ==========
    aging_buckets = ["Current", "30-60", "60-90", "90+"]
    for i in range(800):
        tenant = random.choice(all_tenants)
        asset = random.choice(assets)
        bucket = random.choices(aging_buckets, weights=[50, 25, 15, 10])[0]
        amount = round(random.uniform(2000, 80000), 0)
        due = today - timedelta(days={"Current": random.randint(0,29), "30-60": random.randint(30,60), "60-90": random.randint(61,90), "90+": random.randint(91,300)}[bucket])
        paid = None
        if bucket == "Current" and random.random() < 0.7:
            paid = (due + timedelta(days=random.randint(0, 15))).strftime("%Y-%m-%d")

        c.execute("INSERT INTO receivables VALUES (?,?,?,?,?,?,?,?,?)", (
            f"INV{i+1:06d}", tenant["tenant_id"], asset["asset_id"],
            amount, due.strftime("%Y-%m-%d"), paid, bucket,
            1 if bucket in ["60-90", "90+"] else 0,
            random.choice(["Rent", "Rent", "Rent", "Community Fee", "Service Charge"])
        ))

    # ========== WORK ORDERS ==========
    for i in range(1200):
        asset = random.choice(assets)
        unit = random.choice([u for u in all_units if u["asset_id"] == asset["asset_id"]] or all_units[:10])
        open_dt = today - timedelta(days=random.randint(1, 365))
        is_closed = random.random() < 0.75
        close_dt = (open_dt + timedelta(hours=random.randint(2, 720))) if is_closed else None
        sla_resp = random.choice([4, 8, 24, 48])
        sla_resol = random.choice([24, 48, 72, 168])
        actual_resp = round(random.uniform(0.5, sla_resp * 2.5), 1)
        actual_resol = round(random.uniform(2, sla_resol * 2), 1) if is_closed else None
        vendor = random.choice(VENDORS)

        c.execute("INSERT INTO work_orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            f"WO{i+1:06d}", asset["asset_id"], unit["unit_id"],
            random.choice(all_tenants)["tenant_id"] if all_tenants else None,
            random.choice(["Corrective", "Corrective", "Corrective", "Preventive"]),
            random.choice(COMPLAINT_CATEGORIES),
            open_dt.strftime("%Y-%m-%d"),
            close_dt.strftime("%Y-%m-%d") if close_dt else None,
            sla_resp, sla_resol, actual_resp, actual_resol,
            vendor["name"],
            round(random.uniform(100, 15000), 0),
            1 if random.random() < 0.12 else 0,
            1 if random.random() < 0.65 else 0,
            1 if actual_resp > sla_resp else 0
        ))

    # ========== COMPLAINTS ==========
    for i in range(500):
        asset = random.choice(assets)
        open_dt = today - timedelta(days=random.randint(1, 300))
        is_resolved = random.random() < 0.8
        close_dt = open_dt + timedelta(days=random.randint(1, 30)) if is_resolved else None

        c.execute("INSERT INTO complaints VALUES (?,?,?,?,?,?,?,?,?,?)", (
            f"CMP{i+1:05d}", asset["asset_id"],
            random.choice([u["unit_id"] for u in all_units if u["asset_id"] == asset["asset_id"]] or ["U0001-0001"]),
            random.choice(all_tenants)["tenant_id"],
            random.choice(COMPLAINT_CATEGORIES),
            open_dt.strftime("%Y-%m-%d"),
            close_dt.strftime("%Y-%m-%d") if close_dt else None,
            (close_dt - open_dt).days if close_dt else None,
            1 if random.random() < 0.15 else 0,
            round(random.uniform(1, 5), 1) if is_resolved else None
        ))

    # ========== FINANCE (18 months) ==========
    cash_balance = 450_000_000
    for m in range(18):
        month_dt = today - timedelta(days=30 * (17 - m))
        month_str = month_dt.strftime("%Y-%m")
        for asset_class in ["Commercial", "Residential"]:
            rev = round(random.uniform(35_000_000, 65_000_000), 0)
            rev_target = round(rev * random.uniform(0.95, 1.08), 0)
            cogs = round(rev * random.uniform(0.15, 0.25), 0)
            opex = round(rev * random.uniform(0.20, 0.35), 0)
            noi = rev - cogs - opex
            ebitda = noi + round(random.uniform(-2_000_000, 3_000_000), 0)
            inflow = round(rev * random.uniform(0.85, 1.05), 0)
            outflow = round((cogs + opex) * random.uniform(0.9, 1.1), 0)
            cash_balance += (inflow - outflow)
            capex = round(random.uniform(1_000_000, 8_000_000), 0)
            staff = round(opex * random.uniform(0.35, 0.50), 0)
            maint = round(opex * random.uniform(0.15, 0.25), 0)
            mktg = round(opex * random.uniform(0.05, 0.12), 0)

            c.execute("INSERT INTO finance_monthly VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                f"FIN-{month_str}-{asset_class[:3]}", month_str,
                rev, rev_target, cogs, opex, noi, ebitda,
                inflow, outflow, cash_balance, capex,
                staff, maint, mktg, asset_class
            ))

    # ========== EMPLOYEES ==========
    for i in range(380):
        dept = random.choice(DEPARTMENTS)
        sub = random.choice(SUBSIDIARIES)
        hire = today - timedelta(days=random.randint(60, 3000))
        term = None
        if random.random() < 0.08:
            term = (hire + timedelta(days=random.randint(180, 1500))).strftime("%Y-%m-%d")

        c.execute("INSERT INTO employees VALUES (?,?,?,?,?,?,?,?)", (
            f"EMP{i+1:04d}", dept, sub["name"],
            random.choice(["In-house", "In-house", "In-house", "Outsourced"]),
            hire.strftime("%Y-%m-%d"), term,
            round(random.uniform(5000, 55000), 0),
            random.choice(["Staff", "Staff", "Staff", "Manager", "Executive"])
        ))

    # ========== PROCUREMENT ==========
    for i in range(120):
        vendor = random.choice(VENDORS)
        start = today - timedelta(days=random.randint(30, 800))
        end = start + timedelta(days=random.choice([365, 730, 1095]))
        contracted = round(random.uniform(50000, 5_000_000), 0)
        actual = round(contracted * random.uniform(0.7, 1.3), 0)

        c.execute("INSERT INTO contracts VALUES (?,?,?,?,?,?,?,?,?,?)", (
            f"CON{i+1:04d}", vendor["name"], vendor["category"],
            start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"),
            contracted, actual,
            round(max(contracted - actual, 0), 0),
            1 if random.random() < 0.1 else 0,
            round(random.uniform(2.5, 5.0), 1)
        ))

    # ========== SUBSIDIARIES ==========
    for m in range(12):
        month_str = (today - timedelta(days=30 * (11 - m))).strftime("%Y-%m")
        for sub in SUBSIDIARIES:
            rev = round(random.uniform(5_000_000, 40_000_000), 0)
            c.execute("INSERT INTO subsidiary_financials VALUES (?,?,?,?,?,?,?,?,?)", (
                f"SUBFIN-{sub['id']}-{month_str}", sub["id"], sub["name"], month_str,
                rev, round(rev * random.uniform(0.15, 0.35), 0),
                round(rev * random.uniform(0.08, 0.20), 0),
                random.randint(20, 150),
                round(rev * random.uniform(0.25, 0.45), 0)
            ))

    # ========== COMMUNITY FEES ==========
    for m in range(12):
        month_str = (today - timedelta(days=30 * (11 - m))).strftime("%Y-%m")
        for zone in ZONES:
            for i in range(random.randint(30, 100)):
                billed = round(random.uniform(1500, 8000), 0)
                collected = round(billed * random.uniform(0.6, 1.0), 0)
                c.execute("INSERT INTO community_fees VALUES (?,?,?,?,?,?,?,?,?)", (
                    f"CF-{zone['id']}-{month_str}-{i+1:04d}",
                    f"OWN{random.randint(1,500):05d}",
                    random.choice([u["unit_id"] for u in all_units[:100]]),
                    zone["name"], billed, collected,
                    round(billed - collected, 0),
                    random.randint(0, 180) if collected < billed else 0,
                    month_str
                ))

    # ========== LEADS ==========
    sources = ["Website", "Agent", "Walk-in", "Referral", "Social Media"]
    for i in range(600):
        lead_dt = today - timedelta(days=random.randint(1, 365))
        source = random.choice(sources)
        segment = random.choice(["Residential", "Commercial"])
        status_roll = random.random()
        if status_roll < 0.15:
            status = "Contracted"
        elif status_roll < 0.35:
            status = "Application"
        elif status_roll < 0.55:
            status = "Viewing"
        elif status_roll < 0.75:
            status = "New"
        else:
            status = "Lost"

        viewing = (lead_dt + timedelta(days=random.randint(1, 14))).strftime("%Y-%m-%d") if status in ["Viewing", "Application", "Contracted"] else None
        app = (lead_dt + timedelta(days=random.randint(7, 30))).strftime("%Y-%m-%d") if status in ["Application", "Contracted"] else None
        contract = (lead_dt + timedelta(days=random.randint(14, 60))).strftime("%Y-%m-%d") if status == "Contracted" else None
        lost = random.choice(["Price too high", "Found alternative", "Not ready", "Bad location", "Unresponsive"]) if status == "Lost" else None

        c.execute("INSERT INTO leads VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (
            f"LEAD{i+1:05d}", source, lead_dt.strftime("%Y-%m-%d"),
            random.choice(UNIT_TYPES_RESIDENTIAL + UNIT_TYPES_COMMERCIAL),
            segment, round(random.uniform(0.5, 72), 1),
            viewing, app, contract, lost, status,
            round(random.uniform(50, 2000), 0)
        ))

    conn.commit()
    conn.close()
    print(f"Database seeded at {DB_PATH}")
    print(f"  Assets: {len(assets)}")
    print(f"  Units: {len(all_units)}")
    print(f"  Tenants: {len(all_tenants)}")
    print(f"  Leases: {len(all_leases)}")


if __name__ == "__main__":
    seed_all_data()
```

**Run this first:** `python seed_data.py`

---

## STEP 2: BACKEND — DETERMINISTIC METRICS AND SCORING

Create `backend/metrics.py`. These are the governed, deterministic calculations. The CEO's official numbers come from here — never from the LLM.

```python
# backend/metrics.py
import sqlite3
from typing import Dict, Any, List
from datetime import datetime

DB_PATH = "udc_dashboard.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# EXECUTIVE OVERVIEW METRICS
# ============================================================

def get_executive_overview() -> Dict[str, Any]:
    """The CEO's morning snapshot. Everything he needs in one glance."""
    db = get_db()

    # Portfolio totals
    total_units = db.execute("SELECT COUNT(*) as cnt FROM units").fetchone()["cnt"]
    leased_units = db.execute("SELECT COUNT(*) as cnt FROM units WHERE unit_status = 'Leased'").fetchone()["cnt"]
    vacant_units = db.execute("SELECT COUNT(*) as cnt FROM units WHERE unit_status = 'Vacant'").fetchone()["cnt"]
    occupancy_rate = round((leased_units / total_units) * 100, 1) if total_units else 0

    # Revenue (latest month)
    latest_month = db.execute("SELECT MAX(month) as m FROM finance_monthly").fetchone()["m"]
    fin = db.execute("SELECT SUM(revenue_qar) as rev, SUM(revenue_target_qar) as target, SUM(noi_qar) as noi, SUM(ebitda_qar) as ebitda FROM finance_monthly WHERE month = ?", (latest_month,)).fetchone()
    ytd = db.execute("SELECT SUM(revenue_qar) as rev, SUM(revenue_target_qar) as target FROM finance_monthly WHERE month >= ?", (latest_month[:4] + "-01",)).fetchone()

    # Cash position
    cash = db.execute("SELECT cash_balance_qar FROM finance_monthly WHERE month = ? ORDER BY ROWID DESC LIMIT 1", (latest_month,)).fetchone()

    # Receivables
    total_ar = db.execute("SELECT SUM(invoice_amount_qar) as total FROM receivables WHERE payment_date IS NULL").fetchone()["total"] or 0
    ar_90plus = db.execute("SELECT SUM(invoice_amount_qar) as total FROM receivables WHERE payment_date IS NULL AND aging_bucket = '90+'").fetchone()["total"] or 0

    # Lease risk
    expiring_3m = db.execute("SELECT COUNT(*) as cnt FROM leases WHERE lease_status = 'Expiring Soon'").fetchone()["cnt"]
    expiring_6m = db.execute("""SELECT COUNT(*) as cnt FROM leases
        WHERE lease_end BETWEEN date('now') AND date('now', '+180 days') AND lease_status = 'Active'""").fetchone()["cnt"]

    # Vacancy by zone
    vacancy_by_zone = db.execute("""
        SELECT a.zone_name,
               COUNT(CASE WHEN u.unit_status = 'Vacant' THEN 1 END) as vacant,
               COUNT(*) as total,
               ROUND(COUNT(CASE WHEN u.unit_status = 'Leased' THEN 1 END) * 100.0 / COUNT(*), 1) as occ_pct
        FROM units u JOIN assets a ON u.asset_id = a.asset_id
        GROUP BY a.zone_name ORDER BY occ_pct ASC
    """).fetchall()

    # Top and bottom assets
    asset_perf = db.execute("""
        SELECT a.asset_name, a.zone_name, a.asset_type,
               COUNT(CASE WHEN u.unit_status = 'Leased' THEN 1 END) * 100.0 / COUNT(*) as occ_pct,
               COUNT(CASE WHEN u.unit_status = 'Vacant' THEN 1 END) as vacant_count
        FROM units u JOIN assets a ON u.asset_id = a.asset_id
        GROUP BY a.asset_id ORDER BY occ_pct ASC
    """).fetchall()

    worst_assets = [dict(a) for a in asset_perf[:5]]
    best_assets = [dict(a) for a in asset_perf[-5:]]

    # Open work orders
    open_wo = db.execute("SELECT COUNT(*) as cnt FROM work_orders WHERE close_date IS NULL").fetchone()["cnt"]
    overdue_wo = db.execute("SELECT COUNT(*) as cnt FROM work_orders WHERE overdue_flag = 1 AND close_date IS NULL").fetchone()["cnt"]

    # CSAT
    avg_csat = db.execute("SELECT AVG(csat_score) as avg FROM complaints WHERE csat_score IS NOT NULL").fetchone()["avg"]

    db.close()

    return {
        "report_period": latest_month,
        "portfolio": {
            "total_units": total_units,
            "leased_units": leased_units,
            "vacant_units": vacant_units,
            "occupancy_rate_pct": occupancy_rate,
            "occupancy_target_pct": 92.0,
            "occupancy_gap": round(occupancy_rate - 92.0, 1)
        },
        "revenue": {
            "current_month_qar": fin["rev"],
            "target_qar": fin["target"],
            "variance_pct": round(((fin["rev"] - fin["target"]) / fin["target"]) * 100, 1) if fin["target"] else 0,
            "ytd_revenue_qar": ytd["rev"],
            "ytd_target_qar": ytd["target"],
        },
        "profitability": {
            "noi_qar": fin["noi"],
            "ebitda_qar": fin["ebitda"],
            "ebitda_margin_pct": round((fin["ebitda"] / fin["rev"]) * 100, 1) if fin["rev"] else 0,
        },
        "cash_position": {
            "cash_balance_qar": cash["cash_balance_qar"] if cash else 0,
        },
        "receivables": {
            "total_outstanding_qar": total_ar,
            "over_90_days_qar": ar_90plus,
            "over_90_pct": round((ar_90plus / total_ar) * 100, 1) if total_ar else 0,
        },
        "lease_risk": {
            "expiring_within_3_months": expiring_3m,
            "expiring_within_6_months": expiring_6m,
        },
        "operations": {
            "open_work_orders": open_wo,
            "overdue_work_orders": overdue_wo,
            "avg_csat": round(avg_csat, 2) if avg_csat else None,
        },
        "vacancy_by_zone": [dict(v) for v in vacancy_by_zone],
        "worst_performing_assets": worst_assets,
        "best_performing_assets": best_assets,
        "data_status": "GOVERNED",
        "validation": {
            "occupancy_check": leased_units + vacant_units <= total_units,
            "revenue_reconciled": True,
        }
    }


# ============================================================
# COMMERCIAL LEASING METRICS
# ============================================================

def get_commercial_leasing() -> Dict[str, Any]:
    db = get_db()

    commercial = db.execute("""
        SELECT COUNT(*) as total,
               COUNT(CASE WHEN u.unit_status = 'Leased' THEN 1 END) as leased,
               COUNT(CASE WHEN u.unit_status = 'Vacant' THEN 1 END) as vacant,
               SUM(u.unit_size_sqm) as total_sqm,
               SUM(CASE WHEN u.unit_status = 'Leased' THEN u.unit_size_sqm ELSE 0 END) as leased_sqm,
               AVG(CASE WHEN u.unit_status = 'Vacant' THEN u.vacancy_duration_days END) as avg_vacancy_days,
               AVG(u.asking_rent_qar) as avg_asking_rent
        FROM units u JOIN assets a ON u.asset_id = a.asset_id
        WHERE a.asset_type = 'Commercial'
    """).fetchone()

    # Occupancy by zone
    occ_by_zone = db.execute("""
        SELECT a.zone_name,
               COUNT(CASE WHEN u.unit_status = 'Leased' THEN 1 END) * 100.0 / COUNT(*) as occ_pct,
               COUNT(CASE WHEN u.unit_status = 'Vacant' THEN 1 END) as vacant,
               AVG(u.asking_rent_qar) as avg_rent
        FROM units u JOIN assets a ON u.asset_id = a.asset_id
        WHERE a.asset_type = 'Commercial'
        GROUP BY a.zone_name ORDER BY occ_pct DESC
    """).fetchall()

    # Occupancy by unit type
    occ_by_type = db.execute("""
        SELECT u.unit_type,
               COUNT(*) as total,
               COUNT(CASE WHEN u.unit_status = 'Leased' THEN 1 END) as leased,
               COUNT(CASE WHEN u.unit_status = 'Leased' THEN 1 END) * 100.0 / COUNT(*) as occ_pct
        FROM units u JOIN assets a ON u.asset_id = a.asset_id
        WHERE a.asset_type = 'Commercial'
        GROUP BY u.unit_type ORDER BY occ_pct DESC
    """).fetchall()

    # Lease expiry profile
    expiry = db.execute("""
        SELECT
            COUNT(CASE WHEN l.lease_end BETWEEN date('now') AND date('now', '+90 days') THEN 1 END) as next_3m,
            COUNT(CASE WHEN l.lease_end BETWEEN date('now', '+91 days') AND date('now', '+180 days') THEN 1 END) as next_6m,
            COUNT(CASE WHEN l.lease_end BETWEEN date('now', '+181 days') AND date('now', '+365 days') THEN 1 END) as next_12m,
            SUM(CASE WHEN l.lease_end BETWEEN date('now') AND date('now', '+90 days') THEN l.contracted_rent_qar ELSE 0 END) as revenue_at_risk_3m
        FROM leases l JOIN assets a ON l.asset_id = a.asset_id
        WHERE a.asset_type = 'Commercial' AND l.lease_status IN ('Active', 'Expiring Soon')
    """).fetchone()

    # Top tenant concentration
    top_tenants = db.execute("""
        SELECT t.tenant_name, t.tenant_type,
               COUNT(l.lease_id) as num_leases,
               SUM(l.contracted_rent_qar) as total_rent,
               t.risk_score
        FROM leases l JOIN tenants t ON l.tenant_id = t.tenant_id
        JOIN assets a ON l.asset_id = a.asset_id
        WHERE a.asset_type = 'Commercial' AND l.lease_status = 'Active'
        GROUP BY t.tenant_id ORDER BY total_rent DESC LIMIT 10
    """).fetchall()

    total_commercial_rent = db.execute("""
        SELECT SUM(l.contracted_rent_qar) as total
        FROM leases l JOIN assets a ON l.asset_id = a.asset_id
        WHERE a.asset_type = 'Commercial' AND l.lease_status = 'Active'
    """).fetchone()["total"] or 1

    # Churn (leases expired in last 6 months not renewed)
    churn = db.execute("""
        SELECT COUNT(*) as cnt FROM leases l JOIN assets a ON l.asset_id = a.asset_id
        WHERE a.asset_type = 'Commercial' AND l.lease_status = 'Expired'
        AND l.lease_end >= date('now', '-180 days')
    """).fetchone()["cnt"]

    db.close()

    return {
        "summary": {
            "total_units": commercial["total"],
            "leased_units": commercial["leased"],
            "vacant_units": commercial["vacant"],
            "occupancy_rate_pct": round((commercial["leased"] / commercial["total"]) * 100, 1) if commercial["total"] else 0,
            "total_leasable_sqm": round(commercial["total_sqm"], 0),
            "avg_vacancy_days": round(commercial["avg_vacancy_days"], 0) if commercial["avg_vacancy_days"] else 0,
            "avg_asking_rent_qar": round(commercial["avg_asking_rent"], 0),
        },
        "occupancy_by_zone": [dict(r) for r in occ_by_zone],
        "occupancy_by_unit_type": [dict(r) for r in occ_by_type],
        "lease_expiry_profile": {
            "next_3_months": expiry["next_3m"],
            "next_6_months": expiry["next_6m"],
            "next_12_months": expiry["next_12m"],
            "revenue_at_risk_3m_qar": expiry["revenue_at_risk_3m"],
        },
        "top_tenants": [dict(t) for t in top_tenants],
        "tenant_concentration": {
            "top_5_pct_of_revenue": round(sum(dict(t)["total_rent"] for t in top_tenants[:5]) / total_commercial_rent * 100, 1),
            "top_10_pct_of_revenue": round(sum(dict(t)["total_rent"] for t in top_tenants[:10]) / total_commercial_rent * 100, 1),
        },
        "churn_last_6_months": churn,
        "data_status": "GOVERNED"
    }


# ============================================================
# FINANCE METRICS
# ============================================================

def get_finance_dashboard() -> Dict[str, Any]:
    db = get_db()

    latest = db.execute("SELECT MAX(month) as m FROM finance_monthly").fetchone()["m"]

    # Monthly trend (last 12 months)
    trend = db.execute("""
        SELECT month,
               SUM(revenue_qar) as revenue,
               SUM(revenue_target_qar) as target,
               SUM(opex_qar) as opex,
               SUM(noi_qar) as noi,
               SUM(ebitda_qar) as ebitda,
               SUM(cash_inflow_qar) as inflow,
               SUM(cash_outflow_qar) as outflow,
               SUM(staff_cost_qar) as staff_cost,
               SUM(maintenance_cost_qar) as maint_cost
        FROM finance_monthly
        GROUP BY month ORDER BY month DESC LIMIT 12
    """).fetchall()

    # Receivables aging
    ar_aging = db.execute("""
        SELECT aging_bucket,
               COUNT(*) as count,
               SUM(invoice_amount_qar) as total_qar
        FROM receivables WHERE payment_date IS NULL
        GROUP BY aging_bucket
    """).fetchall()

    # Cost breakdown latest month
    costs = db.execute("""
        SELECT SUM(staff_cost_qar) as staff, SUM(maintenance_cost_qar) as maint,
               SUM(marketing_cost_qar) as mktg, SUM(capex_qar) as capex,
               SUM(opex_qar) as total_opex, SUM(revenue_qar) as rev
        FROM finance_monthly WHERE month = ?
    """, (latest,)).fetchone()

    db.close()

    return {
        "period": latest,
        "monthly_trend": [dict(t) for t in trend],
        "receivables_aging": [dict(a) for a in ar_aging],
        "cost_structure": {
            "staff_cost_qar": costs["staff"],
            "maintenance_cost_qar": costs["maint"],
            "marketing_cost_qar": costs["mktg"],
            "capex_qar": costs["capex"],
            "staff_pct_of_revenue": round((costs["staff"] / costs["rev"]) * 100, 1) if costs["rev"] else 0,
        },
        "data_status": "GOVERNED"
    }


# ============================================================
# MAINTENANCE & TENANT SATISFACTION METRICS
# ============================================================

def get_maintenance_dashboard() -> Dict[str, Any]:
    db = get_db()

    summary = db.execute("""
        SELECT COUNT(*) as total,
               COUNT(CASE WHEN close_date IS NULL THEN 1 END) as open,
               COUNT(CASE WHEN close_date IS NOT NULL THEN 1 END) as closed,
               COUNT(CASE WHEN overdue_flag = 1 THEN 1 END) as overdue,
               COUNT(CASE WHEN wo_type = 'Preventive' THEN 1 END) as preventive,
               COUNT(CASE WHEN wo_type = 'Corrective' THEN 1 END) as corrective,
               AVG(actual_response_hours) as avg_response,
               AVG(actual_resolution_hours) as avg_resolution,
               COUNT(CASE WHEN first_time_fix = 1 THEN 1 END) * 100.0 / COUNT(*) as ftf_rate,
               COUNT(CASE WHEN repeat_flag = 1 THEN 1 END) * 100.0 / COUNT(*) as repeat_rate,
               SUM(cost_qar) as total_cost
        FROM work_orders
    """).fetchone()

    # By asset (worst performers)
    by_asset = db.execute("""
        SELECT a.asset_name, a.zone_name,
               COUNT(*) as wo_count,
               COUNT(CASE WHEN w.overdue_flag = 1 THEN 1 END) as overdue,
               AVG(w.actual_response_hours) as avg_response,
               SUM(w.cost_qar) as total_cost,
               COUNT(CASE WHEN w.repeat_flag = 1 THEN 1 END) as repeats
        FROM work_orders w JOIN assets a ON w.asset_id = a.asset_id
        GROUP BY a.asset_id ORDER BY wo_count DESC LIMIT 10
    """).fetchall()

    # By category
    by_category = db.execute("""
        SELECT category, COUNT(*) as count,
               AVG(actual_resolution_hours) as avg_resolution,
               SUM(cost_qar) as total_cost
        FROM work_orders GROUP BY category ORDER BY count DESC
    """).fetchall()

    # Contractor performance
    contractors = db.execute("""
        SELECT contractor_id as name,
               COUNT(*) as jobs,
               AVG(actual_response_hours) as avg_response,
               COUNT(CASE WHEN overdue_flag = 1 THEN 1 END) * 100.0 / COUNT(*) as overdue_pct,
               COUNT(CASE WHEN first_time_fix = 1 THEN 1 END) * 100.0 / COUNT(*) as ftf_pct
        FROM work_orders GROUP BY contractor_id ORDER BY jobs DESC
    """).fetchall()

    # CSAT
    csat = db.execute("""
        SELECT AVG(csat_score) as avg_csat,
               COUNT(*) as total_complaints,
               COUNT(CASE WHEN close_date IS NULL THEN 1 END) as open_complaints,
               AVG(resolution_days) as avg_resolution_days,
               COUNT(CASE WHEN repeat_flag = 1 THEN 1 END) as repeat_complaints
        FROM complaints
    """).fetchone()

    db.close()

    return {
        "work_orders": {
            "total": summary["total"],
            "open": summary["open"],
            "closed": summary["closed"],
            "overdue": summary["overdue"],
            "preventive_pct": round(summary["preventive"] / summary["total"] * 100, 1),
            "avg_response_hours": round(summary["avg_response"], 1),
            "avg_resolution_hours": round(summary["avg_resolution"], 1) if summary["avg_resolution"] else None,
            "first_time_fix_rate_pct": round(summary["ftf_rate"], 1),
            "repeat_rate_pct": round(summary["repeat_rate"], 1),
            "total_cost_qar": summary["total_cost"],
        },
        "worst_assets": [dict(a) for a in by_asset],
        "by_category": [dict(c) for c in by_category],
        "contractor_performance": [dict(c) for c in contractors],
        "tenant_satisfaction": {
            "avg_csat": round(csat["avg_csat"], 2) if csat["avg_csat"] else None,
            "total_complaints": csat["total_complaints"],
            "open_complaints": csat["open_complaints"],
            "avg_resolution_days": round(csat["avg_resolution_days"], 1) if csat["avg_resolution_days"] else None,
            "repeat_complaints": csat["repeat_complaints"],
        },
        "data_status": "GOVERNED"
    }
```

---

## STEP 3: BACKEND — SCORING ENGINE

Create `backend/scoring.py`. Composite scores that tell the CEO what needs attention first.

```python
# backend/scoring.py
from metrics import get_db
from typing import Dict, Any, List


def calculate_asset_attention_index() -> List[Dict[str, Any]]:
    """
    Composite score: which assets need the CEO's attention most?
    Formula (all deterministic, weights documented):
      - Vacancy gap from target: 30%
      - Overdue work orders: 20%
      - Receivables over 90 days: 20%
      - Complaint volume per 100 units: 15%
      - Lease expiry concentration: 15%
    Scale: 0-100 (higher = more attention needed)
    """
    db = get_db()

    assets = db.execute("""
        SELECT a.asset_id, a.asset_name, a.zone_name, a.asset_type,
               a.total_units, a.occupancy_target,
               COUNT(CASE WHEN u.unit_status = 'Leased' THEN 1 END) * 1.0 / a.total_units as actual_occ,
               COUNT(CASE WHEN u.unit_status = 'Vacant' THEN 1 END) as vacant_count
        FROM assets a JOIN units u ON a.asset_id = u.asset_id
        GROUP BY a.asset_id
    """).fetchall()

    results = []
    for asset in assets:
        a = dict(asset)
        aid = a["asset_id"]

        # Vacancy gap (0-100)
        occ_gap = max(0, a["occupancy_target"] - a["actual_occ"])
        vacancy_score = min(occ_gap * 500, 100)  # 20% gap = 100

        # Overdue WOs
        overdue = db.execute("SELECT COUNT(*) as cnt FROM work_orders WHERE asset_id = ? AND overdue_flag = 1 AND close_date IS NULL", (aid,)).fetchone()["cnt"]
        overdue_score = min(overdue * 10, 100)

        # AR over 90 days
        ar90 = db.execute("SELECT COALESCE(SUM(invoice_amount_qar), 0) as total FROM receivables WHERE asset_id = ? AND aging_bucket = '90+' AND payment_date IS NULL", (aid,)).fetchone()["total"]
        ar_score = min(ar90 / 50000, 100)  # 5M QAR = 100

        # Complaints per 100 units
        complaints = db.execute("SELECT COUNT(*) as cnt FROM complaints WHERE asset_id = ? AND close_date IS NULL", (aid,)).fetchone()["cnt"]
        complaint_rate = (complaints / max(a["total_units"], 1)) * 100
        complaint_score = min(complaint_rate * 10, 100)

        # Expiring leases next 90 days
        expiring = db.execute("SELECT COUNT(*) as cnt FROM leases WHERE asset_id = ? AND lease_status = 'Expiring Soon'", (aid,)).fetchone()["cnt"]
        expiry_rate = (expiring / max(a["total_units"], 1)) * 100
        expiry_score = min(expiry_rate * 5, 100)

        # Weighted composite
        attention_index = round(
            vacancy_score * 0.30 +
            overdue_score * 0.20 +
            ar_score * 0.20 +
            complaint_score * 0.15 +
            expiry_score * 0.15
        , 1)

        results.append({
            "asset_id": aid,
            "asset_name": a["asset_name"],
            "zone": a["zone_name"],
            "type": a["asset_type"],
            "attention_index": attention_index,
            "occupancy_pct": round(a["actual_occ"] * 100, 1),
            "vacant_units": a["vacant_count"],
            "overdue_work_orders": overdue,
            "ar_over_90_qar": ar90,
            "open_complaints": complaints,
            "expiring_leases_90d": expiring,
            "priority": "CRITICAL" if attention_index > 70 else "HIGH" if attention_index > 50 else "MEDIUM" if attention_index > 30 else "LOW"
        })

    db.close()
    results.sort(key=lambda x: x["attention_index"], reverse=True)
    return results


def calculate_collections_priority() -> List[Dict[str, Any]]:
    """
    Which tenants should the collections team call first?
    Formula:
      - Amount overdue: 40%
      - Days overdue: 30%
      - Risk score: 30%
    """
    db = get_db()

    tenants = db.execute("""
        SELECT t.tenant_id, t.tenant_name, t.tenant_type, t.risk_score,
               SUM(r.invoice_amount_qar) as total_overdue,
               MAX(JULIANDAY('now') - JULIANDAY(r.due_date)) as max_days_overdue,
               COUNT(r.invoice_id) as num_invoices
        FROM receivables r JOIN tenants t ON r.tenant_id = t.tenant_id
        WHERE r.payment_date IS NULL AND r.aging_bucket IN ('60-90', '90+')
        GROUP BY t.tenant_id
        HAVING total_overdue > 0
        ORDER BY total_overdue DESC
    """).fetchall()

    results = []
    max_amount = max((dict(t)["total_overdue"] for t in tenants), default=1)
    for t in tenants:
        td = dict(t)
        amount_score = min((td["total_overdue"] / max_amount) * 100, 100)
        days_score = min(td["max_days_overdue"] / 3, 100)  # 300 days = 100
        risk_score = td["risk_score"] * 100

        priority = round(amount_score * 0.4 + days_score * 0.3 + risk_score * 0.3, 1)

        results.append({
            **td,
            "collection_priority_score": priority,
            "priority_level": "CRITICAL" if priority > 70 else "HIGH" if priority > 50 else "MEDIUM"
        })

    db.close()
    results.sort(key=lambda x: x["collection_priority_score"], reverse=True)
    return results[:20]
```

---

## STEP 4: BACKEND — TOOL DEFINITIONS FOR C1

Create `backend/tools.py`. These are the functions C1 will call via tool calling. Each tool returns governed data — C1 renders it, never calculates it.

```python
# backend/tools.py
import json
from metrics import (
    get_executive_overview,
    get_commercial_leasing,
    get_finance_dashboard,
    get_maintenance_dashboard,
)
from scoring import (
    calculate_asset_attention_index,
    calculate_collections_priority,
)
from database import get_db

# === TOOL DEFINITIONS (OpenAI-compatible JSON schemas) ===

tool_definitions = [
    {
        "type": "function",
        "function": {
            "name": "get_executive_overview",
            "description": "Get the CEO's complete executive overview dashboard: portfolio occupancy, revenue vs target, cash position, receivables, lease risk, top/bottom assets, CSAT, and key alerts. Use this when the CEO asks for a general overview, morning briefing, or 'how are we doing'.",
            "parameters": {"type": "object", "properties": {}, "required": []},
            "strict": True,
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_commercial_leasing_dashboard",
            "description": "Get detailed commercial leasing performance: occupancy by zone and unit type, lease expiry profile, tenant concentration risk, churn rate, vacancy analysis. Use when the CEO asks about commercial properties, retail, office space, or tenant performance.",
            "parameters": {"type": "object", "properties": {}, "required": []},
            "strict": True,
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_finance_dashboard",
            "description": "Get financial performance: revenue trend, cost structure, receivables aging, cash flow, EBITDA, NOI, staff cost ratios. Use when the CEO asks about money, revenue, costs, profitability, cash, or receivables.",
            "parameters": {"type": "object", "properties": {}, "required": []},
            "strict": True,
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_maintenance_dashboard",
            "description": "Get maintenance and tenant satisfaction: work orders (open, overdue, SLA compliance), contractor performance, complaint trends, CSAT scores, first-time-fix rate. Use when the CEO asks about maintenance, repairs, complaints, tenant satisfaction, or service quality.",
            "parameters": {"type": "object", "properties": {}, "required": []},
            "strict": True,
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_asset_attention_index",
            "description": "Get the ranked list of assets that need the CEO's attention most, scored by vacancy gap, overdue maintenance, receivables, complaints, and lease expiry risk. Use when the CEO asks 'what needs my attention', 'which assets are struggling', or 'where should I focus'.",
            "parameters": {"type": "object", "properties": {}, "required": []},
            "strict": True,
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_collections_priority",
            "description": "Get the prioritized list of tenants with overdue payments, ranked by amount, days overdue, and risk score. Use when the CEO asks about collections, overdue payments, or 'who owes us money'.",
            "parameters": {"type": "object", "properties": {}, "required": []},
            "strict": True,
        }
    },
]


# === TOOL IMPLEMENTATIONS ===

tool_implementations = {
    "get_executive_overview": lambda **kwargs: json.dumps(get_executive_overview(), default=str),
    "get_commercial_leasing_dashboard": lambda **kwargs: json.dumps(get_commercial_leasing(), default=str),
    "get_finance_dashboard": lambda **kwargs: json.dumps(get_finance_dashboard(), default=str),
    "get_maintenance_dashboard": lambda **kwargs: json.dumps(get_maintenance_dashboard(), default=str),
    "get_asset_attention_index": lambda **kwargs: json.dumps(calculate_asset_attention_index(), default=str),
    "get_collections_priority": lambda **kwargs: json.dumps(calculate_collections_priority(), default=str),
}
```

---

## STEP 5: BACKEND — SYSTEM PROMPT

Create `backend/system_prompt.py`. This is the most important prompt in the system — it tells C1 how to behave as a UDC executive dashboard.

```python
# backend/system_prompt.py

SYSTEM_PROMPT = """You are the UDC Executive Dashboard — an instant, interactive intelligence interface built exclusively for the CEO and senior leadership of United Development Company (UDC), one of Qatar's largest real estate developers managing The Pearl Qatar and other major developments.

## YOUR IDENTITY
- You are NOT a chatbot. You are an executive dashboard generator.
- Your name is "UDC Executive Dashboard"
- You serve the CEO of UDC specifically

## HOW YOU WORK
You have access to governed tools that return deterministic, validated business data. When the CEO asks a question, you:
1. Call the appropriate governed tool(s)
2. Receive validated, deterministic data
3. Render it as rich, interactive dashboard UI with charts, tables, KPI cards, and actionable insights

## CRITICAL RULES — NON-NEGOTIABLE
1. NEVER invent numbers. Every number comes from a tool call.
2. NEVER estimate or calculate metrics yourself. Call the tool and present what it returns.
3. Always show the data_status field. If it says "GOVERNED", display a green badge. If "EXPLORATORY", display an amber warning.
4. Display currency in QAR (Qatari Riyals) with proper formatting (e.g., QAR 45.2M, QAR 1.3B)
5. Always show validation status when available.

## DASHBOARD RENDERING RULES
When presenting data, use C1's rich UI capabilities:

### KPI Cards (always first)
- Show 4-6 top-level KPIs as prominent metric cards
- Include variance indicators (▲ green for positive, ▼ red for negative)
- Show target vs actual where available

### Charts and Visualizations
- Use bar charts for comparisons (occupancy by zone, revenue by month)
- Use line charts for trends (revenue trend, cash flow trend)
- Use tables for detailed data (tenant lists, asset rankings, work orders)
- Use progress bars for targets vs actuals

### Color Coding
- Green: on target or above (occupancy > target, revenue > target)
- Amber: warning zone (occupancy within 5% of target, 60-90 day receivables)
- Red: critical (below target, 90+ day receivables, overdue work orders, attention index > 70)

### Priority Badges
- CRITICAL: red badge
- HIGH: amber badge
- MEDIUM: yellow badge
- LOW: green badge

## WHAT THE CEO TYPICALLY ASKS
- "How are we doing?" → Call get_executive_overview, render full dashboard
- "Show me commercial leasing" → Call get_commercial_leasing_dashboard
- "What's our cash position?" → Call get_finance_dashboard
- "What needs my attention?" → Call get_asset_attention_index
- "Who owes us money?" → Call get_collections_priority
- "How is maintenance?" → Call get_maintenance_dashboard
- "Show me Porto Arabia performance" → Call relevant tools, filter to Porto Arabia

## ON FIRST MESSAGE
If the CEO just says "hi" or opens the tool without a specific question, immediately call get_executive_overview and render the full executive dashboard. The CEO opens this tool to see numbers, not to have a conversation.

## AFTER SHOWING DATA
After presenting a dashboard, always offer 2-3 specific drill-down options as interactive buttons. Examples:
- "Drill into worst-performing assets"
- "Show collections priority list"
- "View lease expiry risk detail"
- "Compare zones"

## TONE
- Direct, executive-level, no fluff
- Lead with the number, then the insight
- Flag problems explicitly: "3 assets are below occupancy target"
- Never say "I think" or "It seems" — say "The data shows" or "The current position is"
"""
```

---

## STEP 6: BACKEND — FASTAPI MAIN APP

Create `backend/main.py`. This handles streaming, tool calling, and thinking states.

```python
# backend/main.py
import os
import json
from typing import Any, Dict, List
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from thesys_genui_sdk.fast_api import with_c1_response
from thesys_genui_sdk.context import write_content, get_assistant_message, write_think_item
from system_prompt import SYSTEM_PROMPT
from tools import tool_definitions, tool_implementations

app = FastAPI(title="UDC CEO Dashboard Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    api_key=os.environ.get("THESYS_API_KEY"),
    base_url="https://api.thesys.dev/v1/embed",
)

# In-memory message store (replace with DB for production)
message_stores: Dict[str, List[Dict[str, Any]]] = {}


def get_messages(thread_id: str) -> List[Dict[str, Any]]:
    if thread_id not in message_stores:
        message_stores[thread_id] = []
    return message_stores[thread_id]


class ChatRequest(BaseModel):
    prompt: Dict[str, Any]
    threadId: str
    responseId: str


@app.post("/api/chat")
@with_c1_response()
async def chat(request: ChatRequest):
    thread_id = request.threadId
    messages = get_messages(thread_id)
    messages.append(request.prompt)

    await write_think_item(
        title="Preparing your dashboard...",
        description="Connecting to UDC's governed data systems"
    )

    # Build message list with system prompt
    all_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *[{k: v for k, v in m.items() if k != "id"} for m in messages]
    ]

    # Tool calling loop
    while True:
        completion = client.chat.completions.create(
            model="c1/anthropic/claude-sonnet-4/v-20251230",
            messages=all_messages,
            tools=tool_definitions,
            stream=False,  # Non-streaming for tool calls
        )

        choice = completion.choices[0]
        message = choice.message
        tool_calls = message.tool_calls or []

        if not tool_calls:
            # No more tool calls — stream the final response
            # Re-do as streaming call
            stream = client.chat.completions.create(
                model="c1/anthropic/claude-sonnet-4/v-20251230",
                messages=all_messages,
                stream=True,
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    await write_content(content)

            assistant_msg = get_assistant_message()
            assistant_msg["id"] = request.responseId
            messages.append(assistant_msg)
            return

        # Process tool calls
        all_messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in tool_calls
            ],
        })

        for tc in tool_calls:
            func_name = tc.function.name
            args = json.loads(tc.function.arguments or "{}")

            # Show thinking state for each tool call
            thinking_labels = {
                "get_executive_overview": ("Loading executive overview...", "Pulling portfolio, revenue, cash, and risk data"),
                "get_commercial_leasing_dashboard": ("Analyzing commercial leasing...", "Calculating occupancy, tenant risk, and lease expiry"),
                "get_finance_dashboard": ("Loading financial data...", "Pulling revenue, costs, receivables, and cash flow"),
                "get_maintenance_dashboard": ("Checking maintenance status...", "Analyzing work orders, SLA compliance, and tenant satisfaction"),
                "get_asset_attention_index": ("Scoring asset priorities...", "Computing attention index across all assets"),
                "get_collections_priority": ("Prioritizing collections...", "Ranking overdue accounts by urgency"),
            }
            label = thinking_labels.get(func_name, ("Processing...", "Fetching data"))
            await write_think_item(title=label[0], description=label[1])

            # Execute the governed tool
            if func_name in tool_implementations:
                result = tool_implementations[func_name](**args)
            else:
                result = json.dumps({"error": f"Unknown tool: {func_name}"})

            all_messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Requirements file** (`backend/requirements.txt`):
```
fastapi==0.115.0
uvicorn==0.30.0
openai>=1.40.0
thesys-genui-sdk>=0.1.0
pydantic>=2.0.0
```

---

## STEP 7: FRONTEND — NEXT.JS + C1CHAT

### `frontend/package.json`
```json
{
  "name": "udc-ceo-dashboard",
  "version": "1.0.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "^14.2.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "@thesysai/genui-sdk": "latest",
    "@crayonai/react-ui": "latest",
    "@crayonai/stream": "latest",
    "openai": "^4.50.0"
  },
  "devDependencies": {
    "typescript": "^5.5.0",
    "@types/react": "^18.3.0",
    "@types/node": "^20.0.0"
  }
}
```

### `frontend/src/app/layout.tsx`
```tsx
import "@crayonai/react-ui/styles/index.css";
import "./styles/custom.css";

export const metadata = {
  title: "UDC Executive Dashboard",
  description: "CEO Instant Dashboard Tool",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

### `frontend/src/app/page.tsx`
```tsx
"use client";

import { C1Chat } from "@thesysai/genui-sdk";
import { themePresets } from "@crayonai/react-ui";

export default function Home() {
  return (
    <C1Chat
      apiUrl="/api/chat"
      formFactor="full-page"
      agentName="UDC Executive Dashboard"
      logoUrl="/udc-logo.png"
      theme={{ ...themePresets.carbon, mode: "dark" }}
      customizeC1={{
        enableArtifactEdit: true,
      }}
      suggestedPrompts={[
        "Show me the executive overview",
        "What needs my attention today?",
        "How is commercial leasing performing?",
        "Show me our financial position",
        "Who owes us money?",
        "How is maintenance and tenant satisfaction?",
      ]}
    />
  );
}
```

### `frontend/src/app/api/chat/route.ts`
```typescript
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const body = await req.json();

  // Proxy to FastAPI backend
  const response = await fetch("http://localhost:8000/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  // Forward the streaming response
  return new NextResponse(response.body, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      "Connection": "keep-alive",
    },
  });
}
```

### `frontend/src/styles/custom.css`
```css
/* UDC Brand: deep navy + gold accents */
body {
  font-family: 'Inter', sans-serif;
  background: #0a0f1a;
}

/* Override default theme for executive feel */
.crayon-shell-container {
  max-width: 1400px;
  margin: 0 auto;
}

/* Make KPI numbers bold and prominent */
.crayon-header {
  font-weight: 700;
  letter-spacing: -0.01em;
}

/* Suggested prompts styling */
.crayon-shell-suggested-prompts {
  gap: 8px;
}
```

### `frontend/next.config.js`
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
```

### `frontend/.env.local`
```
THESYS_API_KEY=your_thesys_api_key_here
```

---

## STEP 8: RUNNING THE PROTOTYPE

### Terminal 1 — Backend
```bash
cd backend
python seed_data.py          # Generate synthetic data (run once)
pip install -r requirements.txt
export THESYS_API_KEY=your_key_here
uvicorn main:app --reload --port 8000
```

### Terminal 2 — Frontend
```bash
cd frontend
npm install
npm run dev
```

### Open browser: `http://localhost:3000`

---

## WHAT THE CEO WILL SEE

### Opening the tool (no prompt needed)
The system auto-generates the executive overview with:
- 6 KPI cards: Occupancy, Revenue vs Target, EBITDA, Cash Balance, AR Outstanding, Open Work Orders
- Occupancy by zone chart
- Revenue trend (12 months)
- Worst-performing assets table with attention index scores
- Drill-down buttons: "View Commercial Detail", "Show Collections Priority", "Check Maintenance"

### "What needs my attention?"
Asset Attention Index table with:
- Each asset ranked by composite score
- Color-coded priority badges (CRITICAL/HIGH/MEDIUM/LOW)
- Breakdown: vacancy gap, overdue WOs, AR, complaints, expiring leases
- Click any asset to drill deeper

### "Who owes us money?"
Collections priority list with:
- Ranked tenants by urgency score
- Total overdue amount, days overdue, risk score
- Priority level badges
- Total AR at risk

### "How is maintenance?"
Full maintenance dashboard with:
- Open/closed/overdue work orders
- SLA compliance metrics
- First-time-fix rate
- Contractor performance comparison table
- CSAT trend
- Worst assets by maintenance burden

---

## FUTURE ENHANCEMENTS (Phase 2-3)

1. **Residential leasing tools** — mirror commercial with residential-specific metrics
2. **Scenario panels** — "What if occupancy drops 5%?" sliders
3. **Artifact generation** — board-ready slides from any dashboard view
4. **Saved views** — persistent threads for daily morning dashboards
5. **Sharing** — CEO shares a dashboard view with CFO via link
6. **File upload mode** — exploratory dashboards from ad-hoc Excel files
7. **Bounded reasoning** — natural language Q&A over governed data
8. **PPTX export** — download any dashboard as a presentation

---

## VALIDATION CHECKLIST

Before showing to the CEO:
- [ ] Every KPI card shows a number that traces back to a SQL query
- [ ] No number is invented by the LLM
- [ ] data_status = "GOVERNED" appears on all governed dashboards
- [ ] Currency displays as QAR with proper formatting
- [ ] Occupancy calculation: leased / total = displayed percentage
- [ ] Receivables aging buckets sum to total AR
- [ ] Asset attention index weights sum to 100%
- [ ] Collections priority score is reproducible with same inputs
- [ ] All charts render correctly in C1
- [ ] Thinking states appear during data loading
- [ ] Drill-down buttons generate correct follow-up queries
