"""
UDC Phase 1 Governed Metric Registry

Every official metric is defined here with formula, source, and owner.
No dashboard may define its own alternative formula.
"""

METRIC_REGISTRY = {
    # === OCCUPANCY (used in: Executive Overview, Commercial Leasing) ===
    "occupancy_rate": {
        "name": "Occupancy Rate",
        "formula": "COUNT(units WHERE status='Leased') / COUNT(units WHERE status IN ('Leased','Vacant')) * 100",
        "unit": "%",
        "dimensions": ["asset", "zone", "unit_type", "month"],
        "owner": "Head of Commercial Leasing",
        "refresh": "Daily",
        "validation": "numerator <= denominator; exclude non-rentable units",
        "version": "v1.0",
    },
    # === REVENUE (used in: Executive Overview, Finance) ===
    "revenue_vs_target": {
        "name": "Revenue vs Target",
        "formula": "SUM(revenue_qar) vs SUM(revenue_target_qar) for period",
        "unit": "QAR",
        "dimensions": ["asset_class", "month", "ytd"],
        "owner": "CFO",
        "refresh": "Monthly",
        "version": "v1.0",
    },
    # === EBITDA (used in: Executive Overview, Finance) ===
    "ebitda": {
        "name": "EBITDA",
        "formula": "NOI + non-cash adjustments (simplified: revenue - COGS - OPEX + adjustments)",
        "unit": "QAR",
        "dimensions": ["asset_class", "month"],
        "owner": "CFO",
        "refresh": "Monthly",
        "version": "v1.0",
    },
    "ebitda_margin": {
        "name": "EBITDA Margin",
        "formula": "EBITDA / Revenue * 100",
        "unit": "%",
        "owner": "CFO",
        "version": "v1.0",
    },
    # === NOI (used in: Executive Overview, Finance) ===
    "noi": {
        "name": "Net Operating Income",
        "formula": "Revenue - COGS - OPEX",
        "unit": "QAR",
        "dimensions": ["asset_class", "month"],
        "owner": "CFO",
        "version": "v1.0",
    },
    # === RECEIVABLES (used in: Executive Overview, Finance) ===
    "receivables_aging": {
        "name": "Receivables Aging",
        "formula": "SUM(invoice_amount) WHERE payment_date IS NULL, grouped by aging_bucket",
        "unit": "QAR",
        "dimensions": ["aging_bucket", "tenant", "asset"],
        "owner": "CFO / Collections",
        "version": "v1.0",
    },
    # === CSAT (used in: Executive Overview, Maintenance) ===
    "csat": {
        "name": "Tenant Satisfaction Score",
        "formula": "AVG(csat_score) from complaints/surveys WHERE csat_score IS NOT NULL",
        "unit": "1-5 scale",
        "dimensions": ["asset", "zone", "month"],
        "owner": "Head of Operations",
        "version": "v1.0",
    },
    # === LEASE EXPIRY (used in: Executive Overview, Commercial Leasing) ===
    "lease_expiry_exposure": {
        "name": "Lease Expiry Exposure",
        "formula": "COUNT(leases) WHERE lease_end within N months AND status IN ('Active','Expiring Soon')",
        "unit": "count + QAR at risk",
        "dimensions": ["3m", "6m", "12m", "asset", "zone"],
        "owner": "Head of Commercial Leasing",
        "version": "v1.0",
    },
    # === COMMERCIAL-SPECIFIC ===
    "tenant_concentration": {
        "name": "Tenant Concentration Risk",
        "formula": "SUM(rent from top N tenants) / SUM(all active rent) * 100",
        "unit": "%",
        "dimensions": ["top_5", "top_10"],
        "owner": "Head of Commercial Leasing",
        "version": "v1.0",
    },
    "vacancy_duration": {
        "name": "Average Vacancy Duration",
        "formula": "AVG(vacancy_duration_days) WHERE status='Vacant'",
        "unit": "days",
        "dimensions": ["asset", "zone", "unit_type"],
        "owner": "Head of Commercial Leasing",
        "version": "v1.0",
    },
    # === MAINTENANCE-SPECIFIC ===
    "first_time_fix_rate": {
        "name": "First-Time Fix Rate",
        "formula": "COUNT(WO WHERE first_time_fix=1) / COUNT(all closed WO) * 100",
        "unit": "%",
        "owner": "Head of Maintenance",
        "version": "v1.0",
    },
    "sla_compliance": {
        "name": "SLA Compliance Rate",
        "formula": "COUNT(WO WHERE actual_response <= sla_response) / COUNT(all WO) * 100",
        "unit": "%",
        "owner": "Head of Maintenance",
        "version": "v1.0",
    },
}

# === PHASE 1 SCORED OUTPUTS (only these 3 for prototype) ===
SCORED_OUTPUTS = {
    "asset_attention_index": {
        "name": "Asset Attention Index",
        "weights": {
            "vacancy_gap": 0.30,
            "overdue_work_orders": 0.20,
            "receivables_90plus": 0.20,
            "complaint_rate": 0.15,
            "lease_expiry_concentration": 0.15,
        },
        "scale": "0-100 (higher = more attention needed)",
        "owner": "COO",
        "version": "v1.0",
    },
    "collections_priority": {
        "name": "Collections Priority Score",
        "weights": {
            "amount_overdue": 0.40,
            "days_overdue": 0.30,
            "tenant_risk_score": 0.30,
        },
        "scale": "0-100",
        "owner": "CFO / Collections",
        "version": "v1.0",
    },
    "service_failure_severity": {
        "name": "Service Failure Severity Score",
        "weights": {
            "repeat_rate": 0.30,
            "overdue_rate": 0.25,
            "csat_below_threshold": 0.25,
            "cost_per_unit": 0.20,
        },
        "scale": "0-100",
        "owner": "Head of Operations",
        "version": "v1.0",
    },
}

# === DEFERRED ITEMS (do not implement in Phase 1) ===
DEFERRED = [
    "Contracted vs pipeline vs speculative revenue (needs business definition)",
    "Corporate account churn risk score (needs predictive model)",
    "Incentive retention uplift (needs attribution logic)",
    "DSCR (needs debt schedule data)",
    "Post-handover margin adjustment risk (needs handover/true-up data)",
]
