# UDC CEO Dashboard — Build Guide Enhancement Pack

## IMPORTANT: This document supplements the main Build Guide
## Apply these changes ON TOP of the original build guide
## Priority: These changes make the difference between a demo and a tool the CEO actually uses

---

## ENHANCEMENT 1: CLEANED PHASE 1 KPI REGISTRY

Replace any loose KPI references in the codebase with this governed registry.
Every metric is defined ONCE here and referenced everywhere.

### Central Metric Definitions (define once, reuse everywhere)

```python
# backend/metric_registry.py
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
```

---

## ENHANCEMENT 2: UPGRADED SYSTEM PROMPT

This is the most important change. The original system prompt was functional but produced generic dashboard layouts. This version makes C1 generate beautiful, deep, analytical visual responses.

Replace `backend/system_prompt.py` entirely:

```python
# backend/system_prompt.py

SYSTEM_PROMPT = """You are the UDC Executive Dashboard — an instant, intelligent, visual executive interface built exclusively for the CEO of United Development Company (UDC), Qatar's premier real estate developer managing The Pearl Qatar.

## YOUR IDENTITY
You are NOT a chatbot. You are a visual executive intelligence system.
When the CEO asks a question, you produce rich, beautiful, interactive dashboards — not text paragraphs with numbers embedded in them.

## VISUAL-FIRST PHILOSOPHY
Every response must be VISUALLY DOMINANT. The CEO glances at your output and understands the situation in 3 seconds. Then drills deeper.

Your response structure for any data query must follow this pattern:

### Layer 1: HEADLINE INSIGHT (2 seconds to grasp)
A single bold statement summarizing the situation:
"Portfolio occupancy is 91.4% — 0.6% below target. Three assets in Porto Arabia are driving the gap."
"Collections exposure has grown 18% month-on-month. QAR 4.2M is now over 90 days."

### Layer 2: KPI CARDS (5 seconds to scan)
4-6 prominent metric cards showing the most important numbers.
Each card MUST include:
- The metric name
- The current value (large, bold)
- The target or comparison value (smaller, grey)
- A trend indicator: ▲ +2.3% (green) or ▼ -1.8% (red) or → 0% (grey)
- A colored status border: green (on target), amber (warning), red (critical)

Format large QAR numbers as: QAR 45.2M, QAR 1.3B, QAR 892K
Never show raw numbers like 45200000.

### Layer 3: VISUAL ANALYSIS (15-30 seconds to understand)
Charts and tables that tell the analytical story:

USE BAR CHARTS for:
- Occupancy by zone (horizontal bars, sorted worst-to-best)
- Revenue by asset class
- Cost breakdown by category
- Contractor performance comparison
- Tenant concentration (stacked or grouped bars)

USE LINE CHARTS for:
- Revenue trend over 12 months (with target line overlay)
- Cash flow trend (inflow vs outflow)
- Occupancy trend
- CSAT trend

USE TABLES for:
- Asset rankings with attention scores (with color-coded priority column)
- Top tenant lists with rent and risk data
- Work order detail with SLA compliance
- Receivables aging breakdown
- Collections priority list

USE PROGRESS BARS for:
- Occupancy vs target
- Revenue vs target
- Budget utilization

USE HEATMAPS or GROUPED COMPARISONS for:
- Zone-by-zone performance comparison
- Asset-by-asset occupancy matrix

### Layer 4: SMART NARRATIVE
After the visuals, add 2-4 sentences of executive-grade analysis:
- What is the situation?
- What is causing it?
- What should the CEO pay attention to?
- What are the 1-2 recommended actions?

Do NOT write generic summaries. Be specific:
WRONG: "Occupancy is below target in some areas."
RIGHT: "Medina Centrale occupancy dropped to 78.3%, driven by 12 vacant retail units averaging 145 days on market. Three units have been vacant for over 300 days — these may need repositioning or incentive packages."

### Layer 5: DRILL-DOWN ACTIONS
Always end with 2-4 interactive buttons offering the next logical question:
- If showing overview → offer "Drill into worst assets", "Show collections risk", "View lease expiry detail"
- If showing commercial → offer "Compare zones", "Show tenant concentration", "View expiry timeline"
- If showing finance → offer "Show receivables aging", "View cost trend", "Compare asset class profitability"
- If showing maintenance → offer "Worst assets by maintenance", "Contractor performance", "CSAT deep dive"

## COLOR LANGUAGE
Use color consistently and meaningfully:
- 🟢 Green: On or above target. Good performance. Low risk.
- 🟡 Amber: Within 5% of target. Moderate risk. Needs monitoring.
- 🔴 Red: Below target. High risk. Needs action.
- 🔵 Blue: Informational. Neutral comparisons.

## PRIORITY BADGES
When showing scored outputs (attention index, collections priority, severity):
- CRITICAL (score > 70): Red badge, bold
- HIGH (score 50-70): Amber badge
- MEDIUM (score 30-50): Yellow badge
- LOW (score < 30): Green badge

## HANDLING DIFFERENT TYPES OF QUESTIONS

### Broad questions ("How are we doing?", "Morning briefing", "Overview")
→ Call get_executive_overview
→ Render the full executive dashboard with all 5 layers
→ This is the default when the CEO opens the tool

### Domain questions ("Show me commercial leasing", "Finance update")
→ Call the specific domain tool
→ Render a deep domain dashboard with zone/type breakdowns

### Problem-finding questions ("What needs my attention?", "Where are the problems?")
→ Call get_asset_attention_index
→ Render a ranked table with color-coded priorities
→ Add narrative explaining the top 3 problem areas specifically

### Collections questions ("Who owes us money?", "Receivables?")
→ Call get_collections_priority
→ Render ranked list with amounts, days overdue, risk scores
→ Show total exposure prominently

### Comparison questions ("Compare zones", "Porto Arabia vs Viva Bahriya")
→ Call relevant tools
→ Render side-by-side comparison with charts
→ Highlight where one outperforms the other

### Drill-down questions ("Tell me more about Porto Arabia", "Why is occupancy low?")
→ Call relevant tools with filters
→ Render detailed breakdown for that specific entity
→ Offer further drill-downs

### Causal questions ("Why?", "What's driving this?")
→ This is where you add the most value
→ Pull multiple data points and connect them
→ Example: "Occupancy dropped because 14 leases expired in Q1, renewal rate was only 62%, and average vacancy duration is 98 days — suggesting pricing or condition issues"

## CRITICAL RULES
1. NEVER invent or estimate numbers. Every number comes from a tool call.
2. NEVER say "I think" — say "The data shows" or "Current position:"
3. ALWAYS show data_status. Governed = green badge. Exploratory = amber warning.
4. ALWAYS format currency as QAR with M/B/K suffixes.
5. ALWAYS include validation status when available.
6. ALWAYS offer drill-down buttons after every response.
7. NEVER produce a text-only response when data is available — ALWAYS use visual components.
8. On first open with no specific question → immediately call get_executive_overview and render the full dashboard.

## TONE
- Direct. Executive-grade. Zero fluff.
- Lead with the number. Then the insight. Then the action.
- Be specific about problems: name the asset, the zone, the tenant, the amount.
- The CEO respects precision and dislikes vagueness.
"""
```

---

## ENHANCEMENT 3: RICHER TOOL RESPONSES

The tools need to return more analytical context so C1 can generate deeper visuals. Add these enhanced functions to `backend/metrics.py`:

```python
# Add to metrics.py — enhanced versions with analytical depth

def get_executive_overview_enhanced() -> Dict[str, Any]:
    """Enhanced executive overview with trend data and comparisons for richer visuals."""
    base = get_executive_overview()  # Get the original data
    db = get_db()

    # Add revenue trend (last 6 months for sparkline)
    revenue_trend = db.execute("""
        SELECT month, SUM(revenue_qar) as revenue, SUM(revenue_target_qar) as target
        FROM finance_monthly GROUP BY month ORDER BY month DESC LIMIT 6
    """).fetchall()
    base["revenue_trend"] = [dict(r) for r in revenue_trend]

    # Add cash flow trend
    cashflow_trend = db.execute("""
        SELECT month, SUM(cash_inflow_qar) as inflow, SUM(cash_outflow_qar) as outflow
        FROM finance_monthly GROUP BY month ORDER BY month DESC LIMIT 6
    """).fetchall()
    base["cashflow_trend"] = [dict(c) for c in cashflow_trend]

    # Add month-over-month comparisons
    months = db.execute("SELECT DISTINCT month FROM finance_monthly ORDER BY month DESC LIMIT 2").fetchall()
    if len(months) >= 2:
        curr = months[0]["month"]
        prev = months[1]["month"]
        curr_rev = db.execute("SELECT SUM(revenue_qar) as r FROM finance_monthly WHERE month=?", (curr,)).fetchone()["r"]
        prev_rev = db.execute("SELECT SUM(revenue_qar) as r FROM finance_monthly WHERE month=?", (prev,)).fetchone()["r"]
        curr_occ = base["portfolio"]["occupancy_rate_pct"]
        base["month_over_month"] = {
            "revenue_change_pct": round(((curr_rev - prev_rev) / prev_rev) * 100, 1) if prev_rev else 0,
            "revenue_direction": "up" if curr_rev > prev_rev else "down",
        }

    # Add top 3 alerts / executive flags
    alerts = []
    if base["portfolio"]["occupancy_rate_pct"] < 90:
        alerts.append({
            "severity": "HIGH",
            "message": f"Portfolio occupancy at {base['portfolio']['occupancy_rate_pct']}% — below 90% threshold",
            "domain": "Leasing"
        })
    if base["receivables"]["over_90_pct"] > 15:
        alerts.append({
            "severity": "CRITICAL",
            "message": f"QAR {base['receivables']['over_90_days_qar']:,.0f} in 90+ day receivables ({base['receivables']['over_90_pct']}% of AR)",
            "domain": "Finance"
        })
    if base["operations"]["overdue_work_orders"] > 20:
        alerts.append({
            "severity": "MEDIUM",
            "message": f"{base['operations']['overdue_work_orders']} overdue work orders across the portfolio",
            "domain": "Maintenance"
        })
    if base["lease_risk"]["expiring_within_3_months"] > 30:
        alerts.append({
            "severity": "HIGH",
            "message": f"{base['lease_risk']['expiring_within_3_months']} leases expiring within 90 days",
            "domain": "Leasing"
        })
    base["executive_alerts"] = alerts

    # Add worst zone detail for narrative
    worst_zone = base["vacancy_by_zone"][0] if base["vacancy_by_zone"] else None
    if worst_zone:
        base["narrative_context"] = {
            "worst_zone": worst_zone["zone_name"],
            "worst_zone_occupancy": worst_zone["occ_pct"],
            "worst_zone_vacant": worst_zone["vacant"],
        }

    db.close()
    return base


def get_zone_deep_dive(zone_name: str) -> Dict[str, Any]:
    """Deep analysis of a specific zone — for drill-down from overview."""
    db = get_db()

    # Zone-level metrics
    zone = db.execute("""
        SELECT a.zone_name,
               COUNT(DISTINCT a.asset_id) as num_assets,
               COUNT(u.unit_id) as total_units,
               COUNT(CASE WHEN u.unit_status = 'Leased' THEN 1 END) as leased,
               COUNT(CASE WHEN u.unit_status = 'Vacant' THEN 1 END) as vacant,
               ROUND(COUNT(CASE WHEN u.unit_status = 'Leased' THEN 1 END) * 100.0 / COUNT(u.unit_id), 1) as occ_pct,
               AVG(u.asking_rent_qar) as avg_rent,
               AVG(CASE WHEN u.unit_status = 'Vacant' THEN u.vacancy_duration_days END) as avg_vac_days,
               SUM(u.unit_size_sqm) as total_sqm
        FROM assets a JOIN units u ON a.asset_id = u.asset_id
        WHERE a.zone_name = ?
        GROUP BY a.zone_name
    """, (zone_name,)).fetchone()

    # Asset breakdown within zone
    assets = db.execute("""
        SELECT a.asset_name, a.asset_type,
               COUNT(u.unit_id) as units,
               COUNT(CASE WHEN u.unit_status = 'Leased' THEN 1 END) * 100.0 / COUNT(u.unit_id) as occ_pct,
               COUNT(CASE WHEN u.unit_status = 'Vacant' THEN 1 END) as vacant,
               AVG(CASE WHEN u.unit_status = 'Vacant' THEN u.vacancy_duration_days END) as avg_vac
        FROM assets a JOIN units u ON a.asset_id = u.asset_id
        WHERE a.zone_name = ?
        GROUP BY a.asset_id ORDER BY occ_pct ASC
    """, (zone_name,)).fetchall()

    # Lease expiry in this zone
    expiry = db.execute("""
        SELECT COUNT(CASE WHEN l.lease_end BETWEEN date('now') AND date('now', '+90 days') THEN 1 END) as next_3m,
               COUNT(CASE WHEN l.lease_end BETWEEN date('now', '+91 days') AND date('now', '+180 days') THEN 1 END) as next_6m,
               SUM(CASE WHEN l.lease_end BETWEEN date('now') AND date('now', '+90 days') THEN l.contracted_rent_qar ELSE 0 END) as rev_at_risk
        FROM leases l JOIN assets a ON l.asset_id = a.asset_id
        WHERE a.zone_name = ? AND l.lease_status IN ('Active', 'Expiring Soon')
    """, (zone_name,)).fetchone()

    # Maintenance in this zone
    maintenance = db.execute("""
        SELECT COUNT(*) as total_wo,
               COUNT(CASE WHEN w.close_date IS NULL THEN 1 END) as open_wo,
               COUNT(CASE WHEN w.overdue_flag = 1 AND w.close_date IS NULL THEN 1 END) as overdue,
               AVG(w.actual_response_hours) as avg_response
        FROM work_orders w JOIN assets a ON w.asset_id = a.asset_id
        WHERE a.zone_name = ?
    """, (zone_name,)).fetchone()

    # Receivables in this zone
    ar = db.execute("""
        SELECT SUM(r.invoice_amount_qar) as total_ar,
               SUM(CASE WHEN r.aging_bucket = '90+' THEN r.invoice_amount_qar ELSE 0 END) as ar_90plus
        FROM receivables r JOIN assets a ON r.asset_id = a.asset_id
        WHERE a.zone_name = ? AND r.payment_date IS NULL
    """, (zone_name,)).fetchone()

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
```

### Add the new tools to `tools.py`:

```python
# Add to tool_definitions list:
{
    "type": "function",
    "function": {
        "name": "get_zone_deep_dive",
        "description": "Deep dive into a specific Pearl Qatar zone showing assets, occupancy, lease expiry, maintenance, and receivables for that zone. Use when the CEO asks about a specific zone like Porto Arabia, Viva Bahriya, Medina Centrale, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "zone_name": {
                    "type": "string",
                    "description": "The zone name, e.g. 'Porto Arabia', 'Viva Bahriya', 'Medina Centrale', 'Qanat Quartier', 'Abraj Quartier', 'The Waterfront', 'Floresta Gardens', 'Giardino Village'"
                }
            },
            "required": ["zone_name"],
            "additionalProperties": False,
        },
        "strict": True,
    }
},

# Add to tool_implementations:
"get_zone_deep_dive": lambda **kwargs: json.dumps(get_zone_deep_dive(kwargs["zone_name"]), default=str),

# Also replace get_executive_overview with enhanced version:
"get_executive_overview": lambda **kwargs: json.dumps(get_executive_overview_enhanced(), default=str),
```

---

## ENHANCEMENT 4: THINKING STATES THAT FEEL EXECUTIVE

Update the thinking state labels in `main.py` to be more polished:

```python
thinking_labels = {
    "get_executive_overview": (
        "Building your executive dashboard",
        "Pulling portfolio performance, financial position, and risk indicators"
    ),
    "get_commercial_leasing_dashboard": (
        "Analyzing commercial portfolio",
        "Occupancy, tenant risk, lease expiry, and zone performance"
    ),
    "get_finance_dashboard": (
        "Loading financial position",
        "Revenue, profitability, cash flow, and receivables"
    ),
    "get_maintenance_dashboard": (
        "Reviewing operations",
        "Work orders, SLA compliance, contractor performance, and satisfaction"
    ),
    "get_asset_attention_index": (
        "Scoring asset priorities",
        "Ranking all assets by vacancy, maintenance, receivables, and risk"
    ),
    "get_collections_priority": (
        "Prioritizing collections",
        "Ranking overdue accounts by amount, age, and tenant risk"
    ),
    "get_zone_deep_dive": (
        "Drilling into zone data",
        f"Loading asset-level detail for the selected zone"
    ),
}
```

---

## ENHANCEMENT 5: SUGGESTED PROMPTS THAT MATCH CEO THINKING

Update `page.tsx` suggested prompts to reflect how a CEO actually thinks:

```tsx
suggestedPrompts={[
  "Good morning — how are we doing?",
  "What needs my attention today?",
  "Show me our commercial leasing performance",
  "How is our cash position and who owes us money?",
  "Are tenants happy? How is maintenance performing?",
  "Compare Porto Arabia vs Medina Centrale",
  "Which assets are struggling the most?",
  "Show me the financial position this month",
]}
```

---

## SUMMARY OF CHANGES

| Change | Why |
|--------|-----|
| Metric registry with define-once-reuse-everywhere | Eliminates duplicate KPI definitions across dashboards |
| Massively upgraded system prompt | Transforms output from data tables into visual executive dashboards with narrative |
| 5-layer response structure | Every response: headline → KPI cards → charts → narrative → drill-downs |
| Enhanced executive overview with trends + alerts | Gives C1 enough context to generate sparklines and flag problems |
| Zone deep-dive tool | Enables the "tell me about Porto Arabia" conversation |
| Executive-grade thinking states | Polished loading messages that feel professional |
| CEO-language suggested prompts | Match how a real estate CEO actually talks |
| Deferred items list | Prevents scope creep into undefined business logic |

The original build guide gives you a working prototype. These enhancements make it a tool the CEO won't want to put down.
