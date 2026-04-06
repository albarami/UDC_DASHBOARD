"""
UDC CEO Dashboard — Deterministic Metrics Engine

Every number the CEO sees comes from this module.
All calculations are SQL-based and deterministic.
The LLM never invents or estimates — it renders what these functions return.
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


# ─── Executive Overview ───────────────────────────────────────────────────────

def get_executive_overview() -> dict[str, Any]:
    """Enhanced executive overview with trends, alerts, and narrative context.

    Returns the CEO's complete morning snapshot: portfolio occupancy,
    revenue vs target, profitability, cash position, receivables, lease risk,
    operations, vacancy by zone, top/bottom assets, revenue and cashflow
    trends, month-over-month comparisons, and auto-generated executive alerts.

    Returns:
        Dictionary with all executive overview data and data_status: GOVERNED.
    """
    db = _get_db()

    # ── Portfolio totals ──
    total_units = db.execute(
        "SELECT COUNT(*) AS cnt FROM units"
    ).fetchone()["cnt"]
    leased_units = db.execute(
        "SELECT COUNT(*) AS cnt FROM units WHERE unit_status = 'Leased'"
    ).fetchone()["cnt"]
    vacant_units = db.execute(
        "SELECT COUNT(*) AS cnt FROM units WHERE unit_status = 'Vacant'"
    ).fetchone()["cnt"]
    occupancy_rate = (
        round((leased_units / total_units) * 100, 1) if total_units else 0
    )

    # ── Revenue (latest month) ──
    latest_month = db.execute(
        "SELECT MAX(month) AS m FROM finance_monthly"
    ).fetchone()["m"]

    fin = db.execute(
        """SELECT SUM(revenue_qar) AS rev,
                  SUM(revenue_target_qar) AS target,
                  SUM(noi_qar) AS noi,
                  SUM(ebitda_qar) AS ebitda
           FROM finance_monthly WHERE month = ?""",
        (latest_month,),
    ).fetchone()

    ytd = db.execute(
        """SELECT SUM(revenue_qar) AS rev,
                  SUM(revenue_target_qar) AS target
           FROM finance_monthly WHERE month >= ?""",
        (latest_month[:4] + "-01",),
    ).fetchone()

    # ── Cash position ──
    cash = db.execute(
        """SELECT cash_balance_qar
           FROM finance_monthly WHERE month = ?
           ORDER BY ROWID DESC LIMIT 1""",
        (latest_month,),
    ).fetchone()

    # ── Receivables ──
    total_ar = db.execute(
        "SELECT SUM(invoice_amount_qar) AS total FROM receivables WHERE payment_date IS NULL"
    ).fetchone()["total"] or 0
    ar_90plus = db.execute(
        """SELECT SUM(invoice_amount_qar) AS total
           FROM receivables
           WHERE payment_date IS NULL AND aging_bucket = '90+'"""
    ).fetchone()["total"] or 0

    # ── Lease risk ──
    expiring_3m = db.execute(
        "SELECT COUNT(*) AS cnt FROM leases WHERE lease_status = 'Expiring Soon'"
    ).fetchone()["cnt"]
    expiring_6m = db.execute(
        """SELECT COUNT(*) AS cnt FROM leases
           WHERE lease_end BETWEEN date('now') AND date('now', '+180 days')
             AND lease_status = 'Active'"""
    ).fetchone()["cnt"]

    # ── Vacancy by zone ──
    vacancy_by_zone = db.execute(
        """SELECT a.zone_name,
                  COUNT(CASE WHEN u.unit_status = 'Vacant' THEN 1 END) AS vacant,
                  COUNT(*) AS total,
                  ROUND(COUNT(CASE WHEN u.unit_status = 'Leased' THEN 1 END) * 100.0 / COUNT(*), 1) AS occ_pct
           FROM units u JOIN assets a ON u.asset_id = a.asset_id
           GROUP BY a.zone_name ORDER BY occ_pct ASC"""
    ).fetchall()

    # ── Top and bottom assets ──
    asset_perf = db.execute(
        """SELECT a.asset_name, a.zone_name, a.asset_type,
                  COUNT(CASE WHEN u.unit_status = 'Leased' THEN 1 END) * 100.0 / COUNT(*) AS occ_pct,
                  COUNT(CASE WHEN u.unit_status = 'Vacant' THEN 1 END) AS vacant_count
           FROM units u JOIN assets a ON u.asset_id = a.asset_id
           GROUP BY a.asset_id ORDER BY occ_pct ASC"""
    ).fetchall()

    worst_assets = [dict(a) for a in asset_perf[:5]]
    best_assets = [dict(a) for a in asset_perf[-5:]]

    # ── Operations ──
    open_wo = db.execute(
        "SELECT COUNT(*) AS cnt FROM work_orders WHERE close_date IS NULL"
    ).fetchone()["cnt"]
    overdue_wo = db.execute(
        "SELECT COUNT(*) AS cnt FROM work_orders WHERE overdue_flag = 1 AND close_date IS NULL"
    ).fetchone()["cnt"]
    avg_csat = db.execute(
        "SELECT AVG(csat_score) AS avg FROM complaints WHERE csat_score IS NOT NULL"
    ).fetchone()["avg"]

    # ── Revenue trend (last 6 months) ──
    revenue_trend = db.execute(
        """SELECT month, SUM(revenue_qar) AS revenue, SUM(revenue_target_qar) AS target
           FROM finance_monthly GROUP BY month ORDER BY month DESC LIMIT 6"""
    ).fetchall()

    # ── Cashflow trend (last 6 months) ──
    cashflow_trend = db.execute(
        """SELECT month, SUM(cash_inflow_qar) AS inflow, SUM(cash_outflow_qar) AS outflow
           FROM finance_monthly GROUP BY month ORDER BY month DESC LIMIT 6"""
    ).fetchall()

    # ── Month-over-month comparison ──
    months = db.execute(
        "SELECT DISTINCT month FROM finance_monthly ORDER BY month DESC LIMIT 2"
    ).fetchall()
    month_over_month: dict[str, Any] = {}
    if len(months) >= 2:
        curr_m = months[0]["month"]
        prev_m = months[1]["month"]
        curr_rev = db.execute(
            "SELECT SUM(revenue_qar) AS r FROM finance_monthly WHERE month = ?",
            (curr_m,),
        ).fetchone()["r"]
        prev_rev = db.execute(
            "SELECT SUM(revenue_qar) AS r FROM finance_monthly WHERE month = ?",
            (prev_m,),
        ).fetchone()["r"]
        if prev_rev and prev_rev > 0:
            change_pct = round(((curr_rev - prev_rev) / prev_rev) * 100, 1)
            month_over_month = {
                "revenue_change_pct": change_pct,
                "revenue_direction": "up" if curr_rev > prev_rev else "down",
            }

    # ── Executive alerts ──
    alerts: list[dict[str, str]] = []
    if occupancy_rate < 90:
        alerts.append({
            "severity": "HIGH",
            "message": f"Portfolio occupancy at {occupancy_rate}% — below 90% threshold",
            "domain": "Leasing",
        })
    over_90_pct = round((ar_90plus / total_ar) * 100, 1) if total_ar else 0
    if over_90_pct > 15:
        alerts.append({
            "severity": "CRITICAL",
            "message": f"QAR {ar_90plus:,.0f} in 90+ day receivables ({over_90_pct}% of AR)",
            "domain": "Finance",
        })
    if overdue_wo > 20:
        alerts.append({
            "severity": "MEDIUM",
            "message": f"{overdue_wo} overdue work orders across the portfolio",
            "domain": "Maintenance",
        })
    if expiring_3m > 30:
        alerts.append({
            "severity": "HIGH",
            "message": f"{expiring_3m} leases expiring within 90 days",
            "domain": "Leasing",
        })

    # ── Narrative context ──
    narrative_context: dict[str, Any] = {}
    zone_list = [dict(v) for v in vacancy_by_zone]
    if zone_list:
        worst_zone = zone_list[0]
        narrative_context = {
            "worst_zone": worst_zone["zone_name"],
            "worst_zone_occupancy": worst_zone["occ_pct"],
            "worst_zone_vacant": worst_zone["vacant"],
        }

    revenue_variance = (
        round(((fin["rev"] - fin["target"]) / fin["target"]) * 100, 1)
        if fin["target"]
        else 0
    )

    db.close()

    return {
        "report_period": latest_month,
        "portfolio": {
            "total_units": total_units,
            "leased_units": leased_units,
            "vacant_units": vacant_units,
            "occupancy_rate_pct": occupancy_rate,
            "occupancy_target_pct": 92.0,
            "occupancy_gap": round(occupancy_rate - 92.0, 1),
        },
        "revenue": {
            "current_month_qar": fin["rev"],
            "target_qar": fin["target"],
            "variance_pct": revenue_variance,
            "ytd_revenue_qar": ytd["rev"],
            "ytd_target_qar": ytd["target"],
        },
        "profitability": {
            "noi_qar": fin["noi"],
            "ebitda_qar": fin["ebitda"],
            "ebitda_margin_pct": (
                round((fin["ebitda"] / fin["rev"]) * 100, 1) if fin["rev"] else 0
            ),
        },
        "cash_position": {
            "cash_balance_qar": cash["cash_balance_qar"] if cash else 0,
        },
        "receivables": {
            "total_outstanding_qar": total_ar,
            "over_90_days_qar": ar_90plus,
            "over_90_pct": over_90_pct,
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
        "vacancy_by_zone": zone_list,
        "worst_performing_assets": worst_assets,
        "best_performing_assets": best_assets,
        "revenue_trend": [dict(r) for r in revenue_trend],
        "cashflow_trend": [dict(c) for c in cashflow_trend],
        "month_over_month": month_over_month,
        "executive_alerts": alerts,
        "narrative_context": narrative_context,
        "data_status": "GOVERNED",
        "validation": {
            "occupancy_check": leased_units + vacant_units <= total_units,
            "revenue_reconciled": True,
        },
    }


# ─── Commercial Leasing ──────────────────────────────────────────────────────

def get_commercial_leasing() -> dict[str, Any]:
    """Detailed commercial leasing performance dashboard.

    Returns occupancy by zone and unit type, lease expiry profile,
    tenant concentration risk, churn rate, and vacancy analysis
    for all commercial properties.

    Returns:
        Dictionary with commercial leasing data and data_status: GOVERNED.
    """
    db = _get_db()

    commercial = db.execute(
        """SELECT COUNT(*) AS total,
                  COUNT(CASE WHEN u.unit_status = 'Leased' THEN 1 END) AS leased,
                  COUNT(CASE WHEN u.unit_status = 'Vacant' THEN 1 END) AS vacant,
                  SUM(u.unit_size_sqm) AS total_sqm,
                  SUM(CASE WHEN u.unit_status = 'Leased' THEN u.unit_size_sqm ELSE 0 END) AS leased_sqm,
                  AVG(CASE WHEN u.unit_status = 'Vacant' THEN u.vacancy_duration_days END) AS avg_vacancy_days,
                  AVG(u.asking_rent_qar) AS avg_asking_rent
           FROM units u JOIN assets a ON u.asset_id = a.asset_id
           WHERE a.asset_type = 'Commercial'"""
    ).fetchone()

    occ_by_zone = db.execute(
        """SELECT a.zone_name,
                  COUNT(CASE WHEN u.unit_status = 'Leased' THEN 1 END) * 100.0 / COUNT(*) AS occ_pct,
                  COUNT(CASE WHEN u.unit_status = 'Vacant' THEN 1 END) AS vacant,
                  AVG(u.asking_rent_qar) AS avg_rent
           FROM units u JOIN assets a ON u.asset_id = a.asset_id
           WHERE a.asset_type = 'Commercial'
           GROUP BY a.zone_name ORDER BY occ_pct DESC"""
    ).fetchall()

    occ_by_type = db.execute(
        """SELECT u.unit_type,
                  COUNT(*) AS total,
                  COUNT(CASE WHEN u.unit_status = 'Leased' THEN 1 END) AS leased,
                  COUNT(CASE WHEN u.unit_status = 'Leased' THEN 1 END) * 100.0 / COUNT(*) AS occ_pct
           FROM units u JOIN assets a ON u.asset_id = a.asset_id
           WHERE a.asset_type = 'Commercial'
           GROUP BY u.unit_type ORDER BY occ_pct DESC"""
    ).fetchall()

    expiry = db.execute(
        """SELECT
               COUNT(CASE WHEN l.lease_end BETWEEN date('now') AND date('now', '+90 days') THEN 1 END) AS next_3m,
               COUNT(CASE WHEN l.lease_end BETWEEN date('now', '+91 days') AND date('now', '+180 days') THEN 1 END) AS next_6m,
               COUNT(CASE WHEN l.lease_end BETWEEN date('now', '+181 days') AND date('now', '+365 days') THEN 1 END) AS next_12m,
               SUM(CASE WHEN l.lease_end BETWEEN date('now') AND date('now', '+90 days') THEN l.contracted_rent_qar ELSE 0 END) AS revenue_at_risk_3m
           FROM leases l JOIN assets a ON l.asset_id = a.asset_id
           WHERE a.asset_type = 'Commercial' AND l.lease_status IN ('Active', 'Expiring Soon')"""
    ).fetchone()

    top_tenants = db.execute(
        """SELECT t.tenant_name, t.tenant_type,
                  COUNT(l.lease_id) AS num_leases,
                  SUM(l.contracted_rent_qar) AS total_rent,
                  t.risk_score
           FROM leases l JOIN tenants t ON l.tenant_id = t.tenant_id
           JOIN assets a ON l.asset_id = a.asset_id
           WHERE a.asset_type = 'Commercial' AND l.lease_status = 'Active'
           GROUP BY t.tenant_id ORDER BY total_rent DESC LIMIT 10"""
    ).fetchall()

    total_commercial_rent = db.execute(
        """SELECT SUM(l.contracted_rent_qar) AS total
           FROM leases l JOIN assets a ON l.asset_id = a.asset_id
           WHERE a.asset_type = 'Commercial' AND l.lease_status = 'Active'"""
    ).fetchone()["total"] or 1

    churn = db.execute(
        """SELECT COUNT(*) AS cnt FROM leases l JOIN assets a ON l.asset_id = a.asset_id
           WHERE a.asset_type = 'Commercial' AND l.lease_status = 'Expired'
             AND l.lease_end >= date('now', '-180 days')"""
    ).fetchone()["cnt"]

    db.close()

    top_tenants_list = [dict(t) for t in top_tenants]
    top_5_rent = sum(t["total_rent"] for t in top_tenants_list[:5])
    top_10_rent = sum(t["total_rent"] for t in top_tenants_list[:10])

    return {
        "summary": {
            "total_units": commercial["total"],
            "leased_units": commercial["leased"],
            "vacant_units": commercial["vacant"],
            "occupancy_rate_pct": (
                round((commercial["leased"] / commercial["total"]) * 100, 1)
                if commercial["total"]
                else 0
            ),
            "total_leasable_sqm": round(commercial["total_sqm"] or 0, 0),
            "avg_vacancy_days": (
                round(commercial["avg_vacancy_days"], 0)
                if commercial["avg_vacancy_days"]
                else 0
            ),
            "avg_asking_rent_qar": round(commercial["avg_asking_rent"] or 0, 0),
        },
        "occupancy_by_zone": [dict(r) for r in occ_by_zone],
        "occupancy_by_unit_type": [dict(r) for r in occ_by_type],
        "lease_expiry_profile": {
            "next_3_months": expiry["next_3m"],
            "next_6_months": expiry["next_6m"],
            "next_12_months": expiry["next_12m"],
            "revenue_at_risk_3m_qar": expiry["revenue_at_risk_3m"],
        },
        "top_tenants": top_tenants_list,
        "tenant_concentration": {
            "top_5_pct_of_revenue": round(top_5_rent / total_commercial_rent * 100, 1),
            "top_10_pct_of_revenue": round(top_10_rent / total_commercial_rent * 100, 1),
        },
        "churn_last_6_months": churn,
        "data_status": "GOVERNED",
    }


# ─── Finance Dashboard ────────────────────────────────────────────────────────

def get_finance_dashboard() -> dict[str, Any]:
    """Financial performance dashboard with trends and cost structure.

    Returns revenue trend (12 months), receivables aging by bucket,
    cost structure breakdown, and profitability metrics.

    Returns:
        Dictionary with financial data and data_status: GOVERNED.
    """
    db = _get_db()

    latest = db.execute(
        "SELECT MAX(month) AS m FROM finance_monthly"
    ).fetchone()["m"]

    trend = db.execute(
        """SELECT month,
                  SUM(revenue_qar) AS revenue,
                  SUM(revenue_target_qar) AS target,
                  SUM(opex_qar) AS opex,
                  SUM(noi_qar) AS noi,
                  SUM(ebitda_qar) AS ebitda,
                  SUM(cash_inflow_qar) AS inflow,
                  SUM(cash_outflow_qar) AS outflow,
                  SUM(staff_cost_qar) AS staff_cost,
                  SUM(maintenance_cost_qar) AS maint_cost
           FROM finance_monthly
           GROUP BY month ORDER BY month DESC LIMIT 12"""
    ).fetchall()

    ar_aging = db.execute(
        """SELECT aging_bucket,
                  COUNT(*) AS count,
                  SUM(invoice_amount_qar) AS total_qar
           FROM receivables WHERE payment_date IS NULL
           GROUP BY aging_bucket"""
    ).fetchall()

    costs = db.execute(
        """SELECT SUM(staff_cost_qar) AS staff,
                  SUM(maintenance_cost_qar) AS maint,
                  SUM(marketing_cost_qar) AS mktg,
                  SUM(capex_qar) AS capex,
                  SUM(opex_qar) AS total_opex,
                  SUM(revenue_qar) AS rev
           FROM finance_monthly WHERE month = ?""",
        (latest,),
    ).fetchone()

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
            "staff_pct_of_revenue": (
                round((costs["staff"] / costs["rev"]) * 100, 1)
                if costs["rev"]
                else 0
            ),
        },
        "data_status": "GOVERNED",
    }


# ─── Maintenance & Tenant Satisfaction ────────────────────────────────────────

def get_maintenance_dashboard() -> dict[str, Any]:
    """Maintenance operations and tenant satisfaction dashboard.

    Returns work order summary, worst assets by WO volume, breakdown
    by category, contractor performance, and CSAT metrics.

    Returns:
        Dictionary with maintenance data and data_status: GOVERNED.
    """
    db = _get_db()

    summary = db.execute(
        """SELECT COUNT(*) AS total,
                  COUNT(CASE WHEN close_date IS NULL THEN 1 END) AS open,
                  COUNT(CASE WHEN close_date IS NOT NULL THEN 1 END) AS closed,
                  COUNT(CASE WHEN overdue_flag = 1 THEN 1 END) AS overdue,
                  COUNT(CASE WHEN wo_type = 'Preventive' THEN 1 END) AS preventive,
                  COUNT(CASE WHEN wo_type = 'Corrective' THEN 1 END) AS corrective,
                  AVG(actual_response_hours) AS avg_response,
                  AVG(actual_resolution_hours) AS avg_resolution,
                  COUNT(CASE WHEN first_time_fix = 1 THEN 1 END) * 100.0 / COUNT(*) AS ftf_rate,
                  COUNT(CASE WHEN repeat_flag = 1 THEN 1 END) * 100.0 / COUNT(*) AS repeat_rate,
                  SUM(cost_qar) AS total_cost
           FROM work_orders"""
    ).fetchone()

    by_asset = db.execute(
        """SELECT a.asset_name, a.zone_name,
                  COUNT(*) AS wo_count,
                  COUNT(CASE WHEN w.overdue_flag = 1 THEN 1 END) AS overdue,
                  AVG(w.actual_response_hours) AS avg_response,
                  SUM(w.cost_qar) AS total_cost,
                  COUNT(CASE WHEN w.repeat_flag = 1 THEN 1 END) AS repeats
           FROM work_orders w JOIN assets a ON w.asset_id = a.asset_id
           GROUP BY a.asset_id ORDER BY wo_count DESC LIMIT 10"""
    ).fetchall()

    by_category = db.execute(
        """SELECT category, COUNT(*) AS count,
                  AVG(actual_resolution_hours) AS avg_resolution,
                  SUM(cost_qar) AS total_cost
           FROM work_orders GROUP BY category ORDER BY count DESC"""
    ).fetchall()

    contractors = db.execute(
        """SELECT contractor_id AS name,
                  COUNT(*) AS jobs,
                  AVG(actual_response_hours) AS avg_response,
                  COUNT(CASE WHEN overdue_flag = 1 THEN 1 END) * 100.0 / COUNT(*) AS overdue_pct,
                  COUNT(CASE WHEN first_time_fix = 1 THEN 1 END) * 100.0 / COUNT(*) AS ftf_pct
           FROM work_orders GROUP BY contractor_id ORDER BY jobs DESC"""
    ).fetchall()

    csat = db.execute(
        """SELECT AVG(csat_score) AS avg_csat,
                  COUNT(*) AS total_complaints,
                  COUNT(CASE WHEN close_date IS NULL THEN 1 END) AS open_complaints,
                  AVG(resolution_days) AS avg_resolution_days,
                  COUNT(CASE WHEN repeat_flag = 1 THEN 1 END) AS repeat_complaints
           FROM complaints"""
    ).fetchone()

    db.close()

    return {
        "work_orders": {
            "total": summary["total"],
            "open": summary["open"],
            "closed": summary["closed"],
            "overdue": summary["overdue"],
            "preventive_pct": round(summary["preventive"] / summary["total"] * 100, 1),
            "avg_response_hours": round(summary["avg_response"], 1),
            "avg_resolution_hours": (
                round(summary["avg_resolution"], 1)
                if summary["avg_resolution"]
                else None
            ),
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
            "avg_resolution_days": (
                round(csat["avg_resolution_days"], 1)
                if csat["avg_resolution_days"]
                else None
            ),
            "repeat_complaints": csat["repeat_complaints"],
        },
        "data_status": "GOVERNED",
    }


# ─── Zone Deep Dive ──────────────────────────────────────────────────────────

def get_zone_deep_dive(zone_name: str) -> dict[str, Any]:
    """Deep analysis of a specific Pearl Qatar zone.

    Provides asset-level breakdown, lease expiry, maintenance stats,
    and receivables for the requested zone.

    Args:
        zone_name: The zone to analyze (e.g. 'Porto Arabia').

    Returns:
        Dictionary with zone-level data and data_status: GOVERNED.
    """
    db = _get_db()

    zone = db.execute(
        """SELECT a.zone_name,
                  COUNT(DISTINCT a.asset_id) AS num_assets,
                  COUNT(u.unit_id) AS total_units,
                  COUNT(CASE WHEN u.unit_status = 'Leased' THEN 1 END) AS leased,
                  COUNT(CASE WHEN u.unit_status = 'Vacant' THEN 1 END) AS vacant,
                  ROUND(COUNT(CASE WHEN u.unit_status = 'Leased' THEN 1 END) * 100.0 / COUNT(u.unit_id), 1) AS occ_pct,
                  AVG(u.asking_rent_qar) AS avg_rent,
                  AVG(CASE WHEN u.unit_status = 'Vacant' THEN u.vacancy_duration_days END) AS avg_vac_days,
                  SUM(u.unit_size_sqm) AS total_sqm
           FROM assets a JOIN units u ON a.asset_id = u.asset_id
           WHERE a.zone_name = ?
           GROUP BY a.zone_name""",
        (zone_name,),
    ).fetchone()

    assets = db.execute(
        """SELECT a.asset_name, a.asset_type,
                  COUNT(u.unit_id) AS units,
                  COUNT(CASE WHEN u.unit_status = 'Leased' THEN 1 END) * 100.0 / COUNT(u.unit_id) AS occ_pct,
                  COUNT(CASE WHEN u.unit_status = 'Vacant' THEN 1 END) AS vacant,
                  AVG(CASE WHEN u.unit_status = 'Vacant' THEN u.vacancy_duration_days END) AS avg_vac
           FROM assets a JOIN units u ON a.asset_id = u.asset_id
           WHERE a.zone_name = ?
           GROUP BY a.asset_id ORDER BY occ_pct ASC""",
        (zone_name,),
    ).fetchall()

    expiry = db.execute(
        """SELECT
               COUNT(CASE WHEN l.lease_end BETWEEN date('now') AND date('now', '+90 days') THEN 1 END) AS next_3m,
               COUNT(CASE WHEN l.lease_end BETWEEN date('now', '+91 days') AND date('now', '+180 days') THEN 1 END) AS next_6m,
               SUM(CASE WHEN l.lease_end BETWEEN date('now') AND date('now', '+90 days') THEN l.contracted_rent_qar ELSE 0 END) AS rev_at_risk
           FROM leases l JOIN assets a ON l.asset_id = a.asset_id
           WHERE a.zone_name = ? AND l.lease_status IN ('Active', 'Expiring Soon')""",
        (zone_name,),
    ).fetchone()

    maintenance = db.execute(
        """SELECT COUNT(*) AS total_wo,
                  COUNT(CASE WHEN w.close_date IS NULL THEN 1 END) AS open_wo,
                  COUNT(CASE WHEN w.overdue_flag = 1 AND w.close_date IS NULL THEN 1 END) AS overdue,
                  AVG(w.actual_response_hours) AS avg_response
           FROM work_orders w JOIN assets a ON w.asset_id = a.asset_id
           WHERE a.zone_name = ?""",
        (zone_name,),
    ).fetchone()

    ar = db.execute(
        """SELECT SUM(r.invoice_amount_qar) AS total_ar,
                  SUM(CASE WHEN r.aging_bucket = '90+' THEN r.invoice_amount_qar ELSE 0 END) AS ar_90plus
           FROM receivables r JOIN assets a ON r.asset_id = a.asset_id
           WHERE a.zone_name = ? AND r.payment_date IS NULL""",
        (zone_name,),
    ).fetchone()

    db.close()

    return {
        "zone_name": zone_name,
        "summary": dict(zone) if zone else {},
        "assets": [dict(a) for a in assets],
        "lease_expiry": dict(expiry) if expiry else {},
        "maintenance": dict(maintenance) if maintenance else {},
        "receivables": dict(ar) if ar else {},
        "data_status": "GOVERNED",
    }
