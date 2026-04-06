"""
UDC CEO Dashboard — Deterministic Scoring Engine

Composite scores that tell the CEO what needs attention first.
All weights are documented and deterministic — no LLM involvement.
"""

import sqlite3
from typing import Any

from config import DB_PATH


def _get_db() -> sqlite3.Connection:
    """Open a read-only database connection with Row factory.

    Returns:
        SQLite connection with row_factory set to sqlite3.Row.
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def calculate_asset_attention_index() -> list[dict[str, Any]]:
    """Rank all assets by how urgently they need the CEO's attention.

    Composite score (0-100, higher = more attention needed):
        - Vacancy gap from target: 30%
        - Overdue work orders: 20%
        - Receivables over 90 days: 20%
        - Complaint volume per 100 units: 15%
        - Lease expiry concentration: 15%

    Returns:
        List of asset dicts sorted by attention_index descending.
    """
    db = _get_db()

    assets = db.execute(
        """SELECT a.asset_id, a.asset_name, a.zone_name, a.asset_type,
                  a.total_units, a.occupancy_target,
                  COUNT(CASE WHEN u.unit_status = 'Leased' THEN 1 END) * 1.0 / a.total_units AS actual_occ,
                  COUNT(CASE WHEN u.unit_status = 'Vacant' THEN 1 END) AS vacant_count
           FROM assets a JOIN units u ON a.asset_id = u.asset_id
           GROUP BY a.asset_id"""
    ).fetchall()

    results: list[dict[str, Any]] = []

    for asset in assets:
        a = dict(asset)
        aid = a["asset_id"]

        # Vacancy gap (0-100): 20% gap = max score
        occ_gap = max(0, a["occupancy_target"] - a["actual_occ"])
        vacancy_score = min(occ_gap * 500, 100)

        # Overdue work orders (0-100): 10 overdue = max score
        overdue = db.execute(
            """SELECT COUNT(*) AS cnt FROM work_orders
               WHERE asset_id = ? AND overdue_flag = 1 AND close_date IS NULL""",
            (aid,),
        ).fetchone()["cnt"]
        overdue_score = min(overdue * 10, 100)

        # AR over 90 days (0-100): QAR 5M = max score
        ar90 = db.execute(
            """SELECT COALESCE(SUM(invoice_amount_qar), 0) AS total
               FROM receivables
               WHERE asset_id = ? AND aging_bucket = '90+' AND payment_date IS NULL""",
            (aid,),
        ).fetchone()["total"]
        ar_score = min(ar90 / 50000, 100)

        # Complaints per 100 units (0-100): 10 per 100 units = max score
        complaints = db.execute(
            """SELECT COUNT(*) AS cnt FROM complaints
               WHERE asset_id = ? AND close_date IS NULL""",
            (aid,),
        ).fetchone()["cnt"]
        complaint_rate = (complaints / max(a["total_units"], 1)) * 100
        complaint_score = min(complaint_rate * 10, 100)

        # Expiring leases next 90 days (0-100): 20% of units expiring = max score
        expiring = db.execute(
            """SELECT COUNT(*) AS cnt FROM leases
               WHERE asset_id = ? AND lease_status = 'Expiring Soon'""",
            (aid,),
        ).fetchone()["cnt"]
        expiry_rate = (expiring / max(a["total_units"], 1)) * 100
        expiry_score = min(expiry_rate * 5, 100)

        # Weighted composite
        attention_index = round(
            vacancy_score * 0.30
            + overdue_score * 0.20
            + ar_score * 0.20
            + complaint_score * 0.15
            + expiry_score * 0.15,
            1,
        )

        priority: str
        if attention_index > 70:
            priority = "CRITICAL"
        elif attention_index > 50:
            priority = "HIGH"
        elif attention_index > 30:
            priority = "MEDIUM"
        else:
            priority = "LOW"

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
            "priority": priority,
        })

    db.close()
    results.sort(key=lambda x: x["attention_index"], reverse=True)
    return results


def calculate_collections_priority() -> list[dict[str, Any]]:
    """Rank overdue tenants by collection urgency.

    Composite score (0-100):
        - Amount overdue: 40%
        - Days overdue: 30%
        - Tenant risk score: 30%

    Returns:
        Top 20 tenants sorted by collection_priority_score descending.
    """
    db = _get_db()

    tenants = db.execute(
        """SELECT t.tenant_id, t.tenant_name, t.tenant_type, t.risk_score,
                  SUM(r.invoice_amount_qar) AS total_overdue,
                  MAX(JULIANDAY('now') - JULIANDAY(r.due_date)) AS max_days_overdue,
                  COUNT(r.invoice_id) AS num_invoices
           FROM receivables r JOIN tenants t ON r.tenant_id = t.tenant_id
           WHERE r.payment_date IS NULL AND r.aging_bucket IN ('60-90', '90+')
           GROUP BY t.tenant_id
           HAVING total_overdue > 0
           ORDER BY total_overdue DESC"""
    ).fetchall()

    if not tenants:
        db.close()
        return []

    tenant_dicts = [dict(t) for t in tenants]
    max_amount = max(t["total_overdue"] for t in tenant_dicts)
    max_amount = max(max_amount, 1)

    results: list[dict[str, Any]] = []
    for td in tenant_dicts:
        amount_score = min((td["total_overdue"] / max_amount) * 100, 100)
        days_score = min(td["max_days_overdue"] / 3, 100)  # 300 days = max
        risk_score = td["risk_score"] * 100

        priority_score = round(
            amount_score * 0.4 + days_score * 0.3 + risk_score * 0.3, 1
        )

        priority_level: str
        if priority_score > 70:
            priority_level = "CRITICAL"
        elif priority_score > 50:
            priority_level = "HIGH"
        else:
            priority_level = "MEDIUM"

        results.append({
            "tenant_id": td["tenant_id"],
            "tenant_name": td["tenant_name"],
            "tenant_type": td["tenant_type"],
            "total_overdue": td["total_overdue"],
            "max_days_overdue": td["max_days_overdue"],
            "num_invoices": td["num_invoices"],
            "risk_score": td["risk_score"],
            "collection_priority_score": priority_score,
            "priority_level": priority_level,
        })

    db.close()
    results.sort(key=lambda x: x["collection_priority_score"], reverse=True)
    return results[:20]
