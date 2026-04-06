"""
UDC CEO Dashboard — Synthetic Data Generator

Generates realistic data for The Pearl Qatar across 13 governed tables.
Uses actual Pearl Qatar zone names, realistic QAR property values,
and real tenant patterns for a mixed-use island development.

Run once: python seed_data.py
Output: udc_dashboard.db (SQLite)
"""

import sqlite3
import random
from datetime import datetime, timedelta
from typing import Any

from config import DB_PATH

random.seed(42)

# ─── Real UDC / Pearl Qatar Geography ────────────────────────────────────────

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
    "British", "American", "French", "Pakistani", "Sudanese", "Tunisian",
]

COMPLAINT_CATEGORIES = [
    "AC/HVAC", "Plumbing", "Electrical", "Elevator", "Parking",
    "Pest Control", "Common Area", "Security", "Noise", "Structural",
    "Internet/Telecom",
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

DEPARTMENTS = [
    "Leasing", "Finance", "Maintenance", "HR", "IT",
    "Legal", "Marketing", "Operations", "Community Mgmt", "Sales",
]

SUBSIDIARIES = [
    {"id": "SUB01", "name": "UDC Properties", "type": "Property Management"},
    {"id": "SUB02", "name": "The Pearl Qatar Co", "type": "Master Development"},
    {"id": "SUB03", "name": "Ronautica", "type": "Marina & Leisure"},
    {"id": "SUB04", "name": "UDC Investments", "type": "Investment Arm"},
]

LEAD_SOURCES = ["Website", "Agent", "Walk-in", "Referral", "Social Media"]

LOST_REASONS = [
    "Price too high", "Found alternative", "Not ready",
    "Bad location", "Unresponsive",
]

# Corporate tenant name prefixes for realistic naming
CORP_PREFIXES = [
    "Al Fardan", "Doha", "Gulf", "Pearl", "Qatar", "Oryx",
    "Falcon", "Barwa", "Ezdan", "Msheireb",
]
CORP_SUFFIXES = [
    "Trading", "Holdings", "Group", "Enterprises", "Solutions",
    "International", "Services", "Properties", "Investments", "Corp",
]

INDIVIDUAL_FIRST = [
    "Ahmed", "Mohammed", "Fatima", "Ali", "Hassan", "Omar",
    "Khalid", "Noor", "Sara", "Youssef", "Ibrahim", "Layla",
    "Tariq", "Aisha", "Hamad", "Maryam", "Rashid", "Huda",
]
INDIVIDUAL_LAST = [
    "Al-Thani", "Al-Sulaiti", "Al-Naimi", "Al-Kuwari", "Al-Dosari",
    "Al-Marri", "Al-Hajri", "Al-Mohannadi", "Al-Ansari", "Al-Emadi",
    "Sharma", "Santos", "Garcia", "Smith", "Dubois", "Khan",
]


# ─── Schema Creation ─────────────────────────────────────────────────────────

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS assets (
    asset_id TEXT PRIMARY KEY,
    asset_name TEXT NOT NULL,
    zone_id TEXT NOT NULL,
    zone_name TEXT NOT NULL,
    asset_type TEXT NOT NULL CHECK(asset_type IN ('Commercial', 'Residential')),
    total_units INTEGER NOT NULL,
    total_leasable_sqm REAL NOT NULL,
    asset_age_years INTEGER NOT NULL,
    valuation_qar REAL NOT NULL,
    occupancy_target REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS units (
    unit_id TEXT PRIMARY KEY,
    asset_id TEXT NOT NULL REFERENCES assets(asset_id),
    unit_type TEXT NOT NULL,
    unit_size_sqm REAL NOT NULL,
    unit_status TEXT NOT NULL CHECK(unit_status IN ('Leased', 'Vacant', 'Under Maintenance', 'Sold')),
    asking_rent_qar REAL NOT NULL,
    market_rent_qar REAL NOT NULL,
    vacancy_start_date TEXT,
    vacancy_duration_days INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS tenants (
    tenant_id TEXT PRIMARY KEY,
    tenant_name TEXT NOT NULL,
    tenant_type TEXT NOT NULL CHECK(tenant_type IN ('Corporate', 'Individual')),
    nationality TEXT NOT NULL,
    total_units_leased INTEGER NOT NULL,
    total_monthly_rent_qar REAL NOT NULL,
    tenant_since TEXT NOT NULL,
    risk_score REAL NOT NULL CHECK(risk_score BETWEEN 0.0 AND 1.0)
);

CREATE TABLE IF NOT EXISTS leases (
    lease_id TEXT PRIMARY KEY,
    asset_id TEXT NOT NULL REFERENCES assets(asset_id),
    unit_id TEXT NOT NULL REFERENCES units(unit_id),
    tenant_id TEXT NOT NULL REFERENCES tenants(tenant_id),
    lease_start TEXT NOT NULL,
    lease_end TEXT NOT NULL,
    contracted_rent_qar REAL NOT NULL,
    rent_per_sqm REAL NOT NULL,
    lease_type TEXT NOT NULL CHECK(lease_type IN ('New', 'Renewal')),
    lease_status TEXT NOT NULL CHECK(lease_status IN ('Active', 'Expired', 'Expiring Soon')),
    security_deposit_qar REAL NOT NULL,
    incentive_months INTEGER NOT NULL DEFAULT 0,
    payment_frequency TEXT NOT NULL CHECK(payment_frequency IN ('Monthly', 'Quarterly', 'Annual'))
);

CREATE TABLE IF NOT EXISTS receivables (
    invoice_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(tenant_id),
    asset_id TEXT NOT NULL REFERENCES assets(asset_id),
    invoice_amount_qar REAL NOT NULL,
    due_date TEXT NOT NULL,
    payment_date TEXT,
    aging_bucket TEXT NOT NULL CHECK(aging_bucket IN ('Current', '30-60', '60-90', '90+')),
    delinquency_flag INTEGER NOT NULL DEFAULT 0,
    revenue_type TEXT NOT NULL CHECK(revenue_type IN ('Rent', 'Community Fee', 'Service Charge'))
);

CREATE TABLE IF NOT EXISTS work_orders (
    wo_id TEXT PRIMARY KEY,
    asset_id TEXT NOT NULL REFERENCES assets(asset_id),
    unit_id TEXT NOT NULL,
    tenant_id TEXT,
    wo_type TEXT NOT NULL CHECK(wo_type IN ('Preventive', 'Corrective')),
    category TEXT NOT NULL,
    open_date TEXT NOT NULL,
    close_date TEXT,
    sla_response_hours REAL NOT NULL,
    sla_resolution_hours REAL NOT NULL,
    actual_response_hours REAL NOT NULL,
    actual_resolution_hours REAL,
    contractor_id TEXT NOT NULL,
    cost_qar REAL NOT NULL,
    repeat_flag INTEGER NOT NULL DEFAULT 0,
    first_time_fix INTEGER NOT NULL DEFAULT 0,
    overdue_flag INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS complaints (
    complaint_id TEXT PRIMARY KEY,
    asset_id TEXT NOT NULL REFERENCES assets(asset_id),
    unit_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL REFERENCES tenants(tenant_id),
    category TEXT NOT NULL,
    open_date TEXT NOT NULL,
    close_date TEXT,
    resolution_days REAL,
    repeat_flag INTEGER NOT NULL DEFAULT 0,
    csat_score REAL CHECK(csat_score IS NULL OR (csat_score BETWEEN 1.0 AND 5.0))
);

CREATE TABLE IF NOT EXISTS finance_monthly (
    record_id TEXT PRIMARY KEY,
    month TEXT NOT NULL,
    revenue_qar REAL NOT NULL,
    revenue_target_qar REAL NOT NULL,
    cogs_qar REAL NOT NULL,
    opex_qar REAL NOT NULL,
    noi_qar REAL NOT NULL,
    ebitda_qar REAL NOT NULL,
    cash_inflow_qar REAL NOT NULL,
    cash_outflow_qar REAL NOT NULL,
    cash_balance_qar REAL NOT NULL,
    capex_qar REAL NOT NULL,
    staff_cost_qar REAL NOT NULL,
    maintenance_cost_qar REAL NOT NULL,
    marketing_cost_qar REAL NOT NULL,
    asset_class TEXT NOT NULL CHECK(asset_class IN ('Commercial', 'Residential'))
);

CREATE TABLE IF NOT EXISTS employees (
    employee_id TEXT PRIMARY KEY,
    department TEXT NOT NULL,
    subsidiary TEXT NOT NULL,
    employment_type TEXT NOT NULL CHECK(employment_type IN ('In-house', 'Outsourced')),
    hire_date TEXT NOT NULL,
    termination_date TEXT,
    monthly_cost_qar REAL NOT NULL,
    role_level TEXT NOT NULL CHECK(role_level IN ('Executive', 'Manager', 'Staff', 'Contractor'))
);

CREATE TABLE IF NOT EXISTS contracts (
    contract_id TEXT PRIMARY KEY,
    vendor_name TEXT NOT NULL,
    vendor_category TEXT NOT NULL,
    contract_start TEXT NOT NULL,
    contract_end TEXT NOT NULL,
    contracted_value_qar REAL NOT NULL,
    actual_spend_qar REAL NOT NULL,
    savings_qar REAL NOT NULL,
    emergency_flag INTEGER NOT NULL DEFAULT 0,
    sla_score REAL NOT NULL CHECK(sla_score BETWEEN 0.0 AND 5.0)
);

CREATE TABLE IF NOT EXISTS subsidiary_financials (
    record_id TEXT PRIMARY KEY,
    subsidiary_id TEXT NOT NULL,
    subsidiary_name TEXT NOT NULL,
    month TEXT NOT NULL,
    revenue_qar REAL NOT NULL,
    ebitda_qar REAL NOT NULL,
    operating_cashflow_qar REAL NOT NULL,
    headcount INTEGER NOT NULL,
    staff_cost_qar REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS community_fees (
    record_id TEXT PRIMARY KEY,
    owner_id TEXT NOT NULL,
    unit_id TEXT NOT NULL,
    zone_name TEXT NOT NULL,
    fees_billed_qar REAL NOT NULL,
    fees_collected_qar REAL NOT NULL,
    outstanding_qar REAL NOT NULL,
    days_outstanding INTEGER NOT NULL DEFAULT 0,
    month TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS leads (
    lead_id TEXT PRIMARY KEY,
    lead_source TEXT NOT NULL,
    lead_date TEXT NOT NULL,
    unit_type TEXT NOT NULL,
    segment TEXT NOT NULL CHECK(segment IN ('Residential', 'Commercial')),
    response_time_hours REAL NOT NULL,
    viewing_date TEXT,
    application_date TEXT,
    contract_date TEXT,
    lost_reason TEXT,
    lead_status TEXT NOT NULL CHECK(lead_status IN ('New', 'Viewing', 'Application', 'Contracted', 'Lost')),
    marketing_cost_qar REAL NOT NULL
);
"""


# ─── Helper Functions ─────────────────────────────────────────────────────────

def _date_str(dt: datetime) -> str:
    """Format a datetime as YYYY-MM-DD string."""
    return dt.strftime("%Y-%m-%d")


def _month_str(dt: datetime) -> str:
    """Format a datetime as YYYY-MM string."""
    return dt.strftime("%Y-%m")


def _months_back(today: datetime, n: int) -> datetime:
    """Step back exactly n calendar months from today.

    Args:
        today: Reference date.
        n: Number of months to go back.

    Returns:
        datetime on the 1st of the target month.
    """
    year = today.year
    month = today.month - n
    while month <= 0:
        month += 12
        year -= 1
    return datetime(year, month, 1)


def _generate_corp_name() -> str:
    """Generate a realistic Qatari corporate tenant name."""
    return f"{random.choice(CORP_PREFIXES)} {random.choice(CORP_SUFFIXES)}"


def _generate_individual_name() -> str:
    """Generate a realistic individual tenant name."""
    return f"{random.choice(INDIVIDUAL_FIRST)} {random.choice(INDIVIDUAL_LAST)}"


# ─── Data Seeding ─────────────────────────────────────────────────────────────

def create_database() -> sqlite3.Connection:
    """Create the SQLite database with all 13 tables.

    Returns:
        Open database connection with tables created.
    """
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(CREATE_TABLES_SQL)
    conn.commit()
    return conn


def seed_assets_and_units(
    conn: sqlite3.Connection,
    today: datetime,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Seed assets and units tables with realistic Pearl Qatar data.

    Args:
        conn: Database connection.
        today: Reference date for calculations.

    Returns:
        Tuple of (assets list, units list).
    """
    c = conn.cursor()
    assets: list[dict[str, Any]] = []
    all_units: list[dict[str, Any]] = []
    asset_counter = 0

    for zone in ZONES:
        num_assets = random.randint(3, 8) if zone["towers"] > 0 else random.randint(2, 4)

        for i in range(num_assets):
            asset_counter += 1
            asset_id = f"A{asset_counter:04d}"

            if zone["type"] == "Mixed":
                asset_type = random.choice(["Commercial", "Residential"])
            else:
                asset_type = zone["type"]

            num_units = random.randint(20, 120)

            if asset_type == "Residential":
                avg_sqm = random.uniform(40, 250)
            else:
                avg_sqm = random.uniform(30, 500)

            total_sqm = round(num_units * avg_sqm, 1)
            valuation = round(total_sqm * random.uniform(12000, 28000), 0)
            occupancy_target = round(random.uniform(0.85, 0.96), 3)

            asset_name = (
                f"{zone['name']} Tower {i + 1}"
                if zone["towers"] > 0
                else f"{zone['name']} Block {i + 1}"
            )

            asset = {
                "asset_id": asset_id,
                "asset_name": asset_name,
                "zone_id": zone["id"],
                "zone_name": zone["name"],
                "asset_type": asset_type,
                "total_units": num_units,
                "total_leasable_sqm": total_sqm,
                "asset_age_years": random.randint(3, 18),
                "valuation_qar": valuation,
                "occupancy_target": occupancy_target,
            }
            assets.append(asset)
            c.execute(
                "INSERT INTO assets VALUES (?,?,?,?,?,?,?,?,?,?)",
                tuple(asset.values()),
            )

            unit_types = (
                UNIT_TYPES_RESIDENTIAL
                if asset_type == "Residential"
                else UNIT_TYPES_COMMERCIAL
            )

            for j in range(num_units):
                unit_id = f"U{asset_counter:04d}-{j + 1:04d}"
                unit_type = random.choice(unit_types)
                sqm = round(random.uniform(30, 350), 1)
                is_leased = random.random() < occupancy_target

                if is_leased:
                    status = "Leased"
                else:
                    status = random.choices(
                        ["Vacant", "Under Maintenance"],
                        weights=[80, 20],
                    )[0]

                if asset_type == "Residential":
                    asking = round(random.uniform(3000, 25000), 0)
                else:
                    asking = round(random.uniform(5000, 80000), 0)

                vac_start = None
                vac_days = 0
                if status != "Leased":
                    vac_start_dt = today - timedelta(days=random.randint(5, 400))
                    vac_start = _date_str(vac_start_dt)
                    vac_days = (today - vac_start_dt).days

                unit = {
                    "unit_id": unit_id,
                    "asset_id": asset_id,
                    "unit_type": unit_type,
                    "unit_size_sqm": sqm,
                    "unit_status": status,
                    "asking_rent_qar": asking,
                    "market_rent_qar": round(asking * random.uniform(0.9, 1.1), 0),
                    "vacancy_start_date": vac_start,
                    "vacancy_duration_days": vac_days,
                }
                all_units.append(unit)
                c.execute(
                    "INSERT INTO units VALUES (?,?,?,?,?,?,?,?,?)",
                    tuple(unit.values()),
                )

    conn.commit()
    return assets, all_units


def seed_tenants(
    conn: sqlite3.Connection,
    today: datetime,
    leased_count: int,
) -> list[dict[str, Any]]:
    """Seed tenants table with realistic corporate and individual tenants.

    Args:
        conn: Database connection.
        today: Reference date for calculations.
        leased_count: Number of leased units (drives tenant count).

    Returns:
        List of tenant dicts.
    """
    c = conn.cursor()
    all_tenants: list[dict[str, Any]] = []

    num_tenants = max(leased_count // 2, 200)

    for i in range(num_tenants):
        tid = f"T{i + 1:05d}"
        is_corp = random.random() < 0.35

        if is_corp:
            name = _generate_corp_name()
            units_leased = random.randint(1, 8)
            monthly_rent = round(random.uniform(15000, 150000), 0)
        else:
            name = _generate_individual_name()
            units_leased = random.randint(1, 2)
            monthly_rent = round(random.uniform(3000, 30000), 0)

        tenant = {
            "tenant_id": tid,
            "tenant_name": name,
            "tenant_type": "Corporate" if is_corp else "Individual",
            "nationality": random.choice(TENANT_NATIONALITIES),
            "total_units_leased": units_leased,
            "total_monthly_rent_qar": monthly_rent,
            "tenant_since": _date_str(today - timedelta(days=random.randint(60, 2500))),
            "risk_score": round(random.uniform(0.1, 0.95), 2),
        }
        all_tenants.append(tenant)
        c.execute(
            "INSERT INTO tenants VALUES (?,?,?,?,?,?,?,?)",
            tuple(tenant.values()),
        )

    conn.commit()
    return all_tenants


def seed_leases(
    conn: sqlite3.Connection,
    today: datetime,
    leased_units: list[dict[str, Any]],
    all_tenants: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Seed leases table linking tenants to leased units.

    Args:
        conn: Database connection.
        today: Reference date for calculations.
        leased_units: Units with status 'Leased'.
        all_tenants: All tenant records.

    Returns:
        List of lease dicts.
    """
    c = conn.cursor()
    all_leases: list[dict[str, Any]] = []

    for idx, unit in enumerate(leased_units):
        tenant = all_tenants[idx % len(all_tenants)]
        lease_start_dt = today - timedelta(days=random.randint(30, 1000))
        lease_duration = random.choice([365, 730, 1095])
        lease_end_dt = lease_start_dt + timedelta(days=lease_duration)
        days_to_expiry = (lease_end_dt - today).days

        if days_to_expiry < 0:
            status = "Expired"
        elif days_to_expiry < 90:
            status = "Expiring Soon"
        else:
            status = "Active"

        contracted_rent = round(unit["asking_rent_qar"] * random.uniform(0.85, 1.0), 0)
        rent_per_sqm = round(
            contracted_rent / max(unit["unit_size_sqm"], 1), 1
        )

        lease = {
            "lease_id": f"L{idx + 1:06d}",
            "asset_id": unit["asset_id"],
            "unit_id": unit["unit_id"],
            "tenant_id": tenant["tenant_id"],
            "lease_start": _date_str(lease_start_dt),
            "lease_end": _date_str(lease_end_dt),
            "contracted_rent_qar": contracted_rent,
            "rent_per_sqm": rent_per_sqm,
            "lease_type": random.choices(["New", "Renewal"], weights=[65, 35])[0],
            "lease_status": status,
            "security_deposit_qar": round(unit["asking_rent_qar"] * 2, 0),
            "incentive_months": random.choice([0, 0, 0, 1, 2]),
            "payment_frequency": random.choice(["Monthly", "Quarterly", "Annual"]),
        }
        all_leases.append(lease)
        c.execute(
            "INSERT INTO leases VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            tuple(lease.values()),
        )

    conn.commit()
    return all_leases


def seed_receivables(
    conn: sqlite3.Connection,
    today: datetime,
    all_tenants: list[dict[str, Any]],
    assets: list[dict[str, Any]],
) -> None:
    """Seed receivables table with realistic aging distribution.

    Args:
        conn: Database connection.
        today: Reference date for calculations.
        all_tenants: All tenant records.
        assets: All asset records.
    """
    c = conn.cursor()
    aging_buckets = ["Current", "30-60", "60-90", "90+"]
    aging_weights = [50, 25, 15, 10]
    aging_day_ranges = {
        "Current": (0, 29),
        "30-60": (30, 60),
        "60-90": (61, 90),
        "90+": (91, 300),
    }

    for i in range(800):
        tenant = random.choice(all_tenants)
        asset = random.choice(assets)
        bucket = random.choices(aging_buckets, weights=aging_weights)[0]
        amount = round(random.uniform(2000, 80000), 0)

        day_range = aging_day_ranges[bucket]
        due_dt = today - timedelta(days=random.randint(*day_range))

        paid = None
        if bucket == "Current" and random.random() < 0.7:
            paid = _date_str(due_dt + timedelta(days=random.randint(0, 15)))

        delinquent = 1 if bucket in ("60-90", "90+") else 0
        rev_type = random.choices(
            ["Rent", "Community Fee", "Service Charge"],
            weights=[60, 25, 15],
        )[0]

        c.execute(
            "INSERT INTO receivables VALUES (?,?,?,?,?,?,?,?,?)",
            (
                f"INV{i + 1:06d}",
                tenant["tenant_id"],
                asset["asset_id"],
                amount,
                _date_str(due_dt),
                paid,
                bucket,
                delinquent,
                rev_type,
            ),
        )

    conn.commit()


def seed_work_orders(
    conn: sqlite3.Connection,
    today: datetime,
    assets: list[dict[str, Any]],
    all_units: list[dict[str, Any]],
    all_tenants: list[dict[str, Any]],
) -> None:
    """Seed work orders table with realistic maintenance data.

    Args:
        conn: Database connection.
        today: Reference date for calculations.
        assets: All asset records.
        all_units: All unit records.
        all_tenants: All tenant records.
    """
    c = conn.cursor()

    units_by_asset: dict[str, list[dict[str, Any]]] = {}
    for u in all_units:
        units_by_asset.setdefault(u["asset_id"], []).append(u)

    for i in range(1200):
        asset = random.choice(assets)
        asset_units = units_by_asset.get(asset["asset_id"], all_units[:10])
        unit = random.choice(asset_units)

        open_dt = today - timedelta(days=random.randint(1, 365))
        is_closed = random.random() < 0.75
        close_dt = (
            open_dt + timedelta(hours=random.randint(2, 720))
            if is_closed
            else None
        )

        sla_resp = random.choice([4, 8, 24, 48])
        sla_resol = random.choice([24, 48, 72, 168])
        actual_resp = round(random.uniform(0.5, sla_resp * 2.5), 1)
        actual_resol = (
            round(random.uniform(2, sla_resol * 2), 1) if is_closed else None
        )
        vendor = random.choice(VENDORS)

        wo_type = random.choices(
            ["Corrective", "Preventive"], weights=[75, 25]
        )[0]

        c.execute(
            "INSERT INTO work_orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                f"WO{i + 1:06d}",
                asset["asset_id"],
                unit["unit_id"],
                random.choice(all_tenants)["tenant_id"] if all_tenants else None,
                wo_type,
                random.choice(COMPLAINT_CATEGORIES),
                _date_str(open_dt),
                _date_str(close_dt) if close_dt else None,
                sla_resp,
                sla_resol,
                actual_resp,
                actual_resol,
                vendor["name"],
                round(random.uniform(100, 15000), 0),
                1 if random.random() < 0.12 else 0,
                1 if random.random() < 0.65 else 0,
                1 if actual_resp > sla_resp else 0,
            ),
        )

    conn.commit()


def seed_complaints(
    conn: sqlite3.Connection,
    today: datetime,
    assets: list[dict[str, Any]],
    all_units: list[dict[str, Any]],
    all_tenants: list[dict[str, Any]],
) -> None:
    """Seed complaints table with realistic tenant complaint data.

    Args:
        conn: Database connection.
        today: Reference date for calculations.
        assets: All asset records.
        all_units: All unit records.
        all_tenants: All tenant records.
    """
    c = conn.cursor()

    units_by_asset: dict[str, list[str]] = {}
    for u in all_units:
        units_by_asset.setdefault(u["asset_id"], []).append(u["unit_id"])

    for i in range(500):
        asset = random.choice(assets)
        unit_ids = units_by_asset.get(asset["asset_id"], ["U0001-0001"])
        unit_id = random.choice(unit_ids)

        open_dt = today - timedelta(days=random.randint(1, 300))
        is_resolved = random.random() < 0.8
        close_dt = (
            open_dt + timedelta(days=random.randint(1, 30))
            if is_resolved
            else None
        )
        resolution_days = (close_dt - open_dt).days if close_dt else None
        csat = round(random.uniform(1, 5), 1) if is_resolved else None

        c.execute(
            "INSERT INTO complaints VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                f"CMP{i + 1:05d}",
                asset["asset_id"],
                unit_id,
                random.choice(all_tenants)["tenant_id"],
                random.choice(COMPLAINT_CATEGORIES),
                _date_str(open_dt),
                _date_str(close_dt) if close_dt else None,
                resolution_days,
                1 if random.random() < 0.15 else 0,
                csat,
            ),
        )

    conn.commit()


def seed_finance(conn: sqlite3.Connection, today: datetime) -> None:
    """Seed 18 months of financial data for Commercial and Residential classes.

    Args:
        conn: Database connection.
        today: Reference date for calculations.
    """
    c = conn.cursor()
    cash_balance = 450_000_000.0

    for m in range(18):
        month_dt = _months_back(today, 17 - m)
        month_str = _month_str(month_dt)

        for asset_class in ["Commercial", "Residential"]:
            rev = round(random.uniform(35_000_000, 65_000_000), 0)
            rev_target = round(rev * random.uniform(0.95, 1.08), 0)
            cogs = round(rev * random.uniform(0.15, 0.25), 0)
            opex = round(rev * random.uniform(0.20, 0.35), 0)
            noi = rev - cogs - opex
            ebitda = noi + round(random.uniform(-2_000_000, 3_000_000), 0)
            inflow = round(rev * random.uniform(0.85, 1.05), 0)
            outflow = round((cogs + opex) * random.uniform(0.9, 1.1), 0)
            cash_balance += inflow - outflow
            capex = round(random.uniform(1_000_000, 8_000_000), 0)
            staff = round(opex * random.uniform(0.35, 0.50), 0)
            maint = round(opex * random.uniform(0.15, 0.25), 0)
            mktg = round(opex * random.uniform(0.05, 0.12), 0)

            c.execute(
                "INSERT INTO finance_monthly VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    f"FIN-{month_str}-{asset_class[:3]}",
                    month_str,
                    rev, rev_target, cogs, opex, noi, ebitda,
                    inflow, outflow, cash_balance, capex,
                    staff, maint, mktg, asset_class,
                ),
            )

    conn.commit()


def seed_employees(conn: sqlite3.Connection, today: datetime) -> None:
    """Seed employees table with realistic HR data across subsidiaries.

    Args:
        conn: Database connection.
        today: Reference date for calculations.
    """
    c = conn.cursor()

    for i in range(380):
        dept = random.choice(DEPARTMENTS)
        sub = random.choice(SUBSIDIARIES)
        hire_dt = today - timedelta(days=random.randint(60, 3000))
        term = None
        if random.random() < 0.08:
            term_dt = hire_dt + timedelta(days=random.randint(180, 1500))
            if term_dt < today:
                term = _date_str(term_dt)

        emp_type = random.choices(
            ["In-house", "Outsourced"], weights=[75, 25]
        )[0]
        role = random.choices(
            ["Staff", "Manager", "Executive", "Contractor"],
            weights=[60, 20, 5, 15],
        )[0]

        cost_ranges = {
            "Executive": (35000, 55000),
            "Manager": (18000, 38000),
            "Staff": (5000, 20000),
            "Contractor": (4000, 15000),
        }
        low, high = cost_ranges[role]

        c.execute(
            "INSERT INTO employees VALUES (?,?,?,?,?,?,?,?)",
            (
                f"EMP{i + 1:04d}",
                dept,
                sub["name"],
                emp_type,
                _date_str(hire_dt),
                term,
                round(random.uniform(low, high), 0),
                role,
            ),
        )

    conn.commit()


def seed_contracts(conn: sqlite3.Connection, today: datetime) -> None:
    """Seed procurement contracts table.

    Args:
        conn: Database connection.
        today: Reference date for calculations.
    """
    c = conn.cursor()

    for i in range(120):
        vendor = random.choice(VENDORS)
        start_dt = today - timedelta(days=random.randint(30, 800))
        end_dt = start_dt + timedelta(days=random.choice([365, 730, 1095]))
        contracted = round(random.uniform(50000, 5_000_000), 0)
        actual = round(contracted * random.uniform(0.7, 1.3), 0)

        c.execute(
            "INSERT INTO contracts VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                f"CON{i + 1:04d}",
                vendor["name"],
                vendor["category"],
                _date_str(start_dt),
                _date_str(end_dt),
                contracted,
                actual,
                round(max(contracted - actual, 0), 0),
                1 if random.random() < 0.1 else 0,
                round(random.uniform(2.5, 5.0), 1),
            ),
        )

    conn.commit()


def seed_subsidiary_financials(conn: sqlite3.Connection, today: datetime) -> None:
    """Seed 12 months of subsidiary financial data.

    Args:
        conn: Database connection.
        today: Reference date for calculations.
    """
    c = conn.cursor()

    for m in range(12):
        month_str = _month_str(_months_back(today, 11 - m))

        for sub in SUBSIDIARIES:
            rev = round(random.uniform(5_000_000, 40_000_000), 0)
            c.execute(
                "INSERT INTO subsidiary_financials VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    f"SUBFIN-{sub['id']}-{month_str}",
                    sub["id"],
                    sub["name"],
                    month_str,
                    rev,
                    round(rev * random.uniform(0.15, 0.35), 0),
                    round(rev * random.uniform(0.08, 0.20), 0),
                    random.randint(20, 150),
                    round(rev * random.uniform(0.25, 0.45), 0),
                ),
            )

    conn.commit()


def seed_community_fees(
    conn: sqlite3.Connection,
    today: datetime,
    all_units: list[dict[str, Any]],
) -> None:
    """Seed 12 months of community fee data across all zones.

    Args:
        conn: Database connection.
        today: Reference date for calculations.
        all_units: All unit records (for unit_id references).
    """
    c = conn.cursor()
    sample_unit_ids = [u["unit_id"] for u in all_units[:100]]

    for m in range(12):
        month_str = _month_str(_months_back(today, 11 - m))

        for zone in ZONES:
            num_owners = random.randint(30, 100)
            for i in range(num_owners):
                billed = round(random.uniform(1500, 8000), 0)
                collected = round(billed * random.uniform(0.6, 1.0), 0)
                outstanding = round(billed - collected, 0)

                c.execute(
                    "INSERT INTO community_fees VALUES (?,?,?,?,?,?,?,?,?)",
                    (
                        f"CF-{zone['id']}-{month_str}-{i + 1:04d}",
                        f"OWN{random.randint(1, 500):05d}",
                        random.choice(sample_unit_ids),
                        zone["name"],
                        billed,
                        collected,
                        outstanding,
                        random.randint(0, 180) if outstanding > 0 else 0,
                        month_str,
                    ),
                )

    conn.commit()


def seed_leads(conn: sqlite3.Connection, today: datetime) -> None:
    """Seed leads table with realistic lead-to-lease funnel data.

    Args:
        conn: Database connection.
        today: Reference date for calculations.
    """
    c = conn.cursor()
    all_unit_types = UNIT_TYPES_RESIDENTIAL + UNIT_TYPES_COMMERCIAL

    status_weights = {
        "Contracted": 0.15,
        "Application": 0.20,
        "Viewing": 0.20,
        "New": 0.20,
        "Lost": 0.25,
    }
    statuses = list(status_weights.keys())
    weights = list(status_weights.values())

    for i in range(600):
        lead_dt = today - timedelta(days=random.randint(1, 365))
        status = random.choices(statuses, weights=weights)[0]
        segment = random.choice(["Residential", "Commercial"])

        viewing = None
        app = None
        contract = None
        lost = None

        if status in ("Viewing", "Application", "Contracted"):
            viewing = _date_str(lead_dt + timedelta(days=random.randint(1, 14)))
        if status in ("Application", "Contracted"):
            app = _date_str(lead_dt + timedelta(days=random.randint(7, 30)))
        if status == "Contracted":
            contract = _date_str(lead_dt + timedelta(days=random.randint(14, 60)))
        if status == "Lost":
            lost = random.choice(LOST_REASONS)

        c.execute(
            "INSERT INTO leads VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                f"LEAD{i + 1:05d}",
                random.choice(LEAD_SOURCES),
                _date_str(lead_dt),
                random.choice(all_unit_types),
                segment,
                round(random.uniform(0.5, 72), 1),
                viewing,
                app,
                contract,
                lost,
                status,
                round(random.uniform(50, 2000), 0),
            ),
        )

    conn.commit()


def seed_all_data() -> None:
    """Run the complete data seeding pipeline for all 13 tables.

    Creates the database, seeds all tables in dependency order,
    and prints summary statistics.
    """
    today = datetime(2026, 3, 31)

    print("Creating database...")
    conn = create_database()

    print("Seeding assets and units...")
    assets, all_units = seed_assets_and_units(conn, today)

    leased_units = [u for u in all_units if u["unit_status"] == "Leased"]

    print("Seeding tenants...")
    all_tenants = seed_tenants(conn, today, len(leased_units))

    print("Seeding leases...")
    all_leases = seed_leases(conn, today, leased_units, all_tenants)

    print("Seeding receivables...")
    seed_receivables(conn, today, all_tenants, assets)

    print("Seeding work orders...")
    seed_work_orders(conn, today, assets, all_units, all_tenants)

    print("Seeding complaints...")
    seed_complaints(conn, today, assets, all_units, all_tenants)

    print("Seeding finance (18 months)...")
    seed_finance(conn, today)

    print("Seeding employees...")
    seed_employees(conn, today)

    print("Seeding contracts...")
    seed_contracts(conn, today)

    print("Seeding subsidiary financials...")
    seed_subsidiary_financials(conn, today)

    print("Seeding community fees...")
    seed_community_fees(conn, today, all_units)

    print("Seeding leads...")
    seed_leads(conn, today)

    conn.close()

    print(f"\nDatabase seeded at {DB_PATH}")
    print(f"  Assets: {len(assets)}")
    print(f"  Units: {len(all_units)}")
    print(f"  Tenants: {len(all_tenants)}")
    print(f"  Leases: {len(all_leases)}")
    print(f"  Leased units: {len(leased_units)}")


if __name__ == "__main__":
    seed_all_data()
