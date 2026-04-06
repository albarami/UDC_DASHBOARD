"""
UDC CEO Dashboard — Governed Tool Definitions

Each tool exposes a deterministic metric or scoring function to C1.
C1 calls these tools via standard OpenAI function calling.
C1 renders the results — it never calculates them.

Every tool returns JSON with data_status: "GOVERNED".
"""

import json
from typing import Any, Callable

from metrics import (
    get_executive_overview,
    get_commercial_leasing,
    get_finance_dashboard,
    get_maintenance_dashboard,
    get_zone_deep_dive,
)
from scoring import (
    calculate_asset_attention_index,
    calculate_collections_priority,
)


def _to_json(data: Any) -> str:
    """Serialize tool output to JSON string for C1 consumption."""
    return json.dumps(data, default=str, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════
# TOOL DEFINITIONS — OpenAI-compatible JSON schemas
# ═══════════════════════════════════════════════════════════════

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_executive_overview",
            "description": (
                "Get the CEO's complete executive overview dashboard: portfolio occupancy, "
                "revenue vs target, cash position, receivables, lease risk, top/bottom assets, "
                "CSAT, revenue trend, cashflow trend, executive alerts, and key risk indicators. "
                "Use this when the CEO asks for a general overview, morning briefing, "
                "'how are we doing', or opens the tool without a specific question."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_commercial_leasing_dashboard",
            "description": (
                "Get detailed commercial leasing performance: occupancy by zone and unit type, "
                "lease expiry profile with revenue at risk, tenant concentration risk, "
                "churn rate, vacancy analysis, and top tenant breakdown. "
                "Use when the CEO asks about commercial properties, retail, office space, "
                "tenants, leasing performance, or vacancy."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_finance_dashboard",
            "description": (
                "Get financial performance: revenue trend (12 months), cost structure breakdown, "
                "receivables aging by bucket, cash flow trend, EBITDA, NOI, staff cost ratios. "
                "Use when the CEO asks about money, revenue, costs, profitability, cash, "
                "budget, receivables, or financial position."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_maintenance_dashboard",
            "description": (
                "Get maintenance operations and tenant satisfaction: work orders (open, closed, "
                "overdue), SLA compliance, first-time-fix rate, contractor performance, "
                "complaint trends, CSAT scores, repeat ticket rate, cost per unit. "
                "Use when the CEO asks about maintenance, repairs, complaints, tenant "
                "satisfaction, service quality, or contractors."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_asset_attention_index",
            "description": (
                "Get the ranked list of assets that need the CEO's attention most, scored by "
                "a composite index: vacancy gap (30%), overdue maintenance (20%), receivables "
                "over 90 days (20%), complaints (15%), lease expiry concentration (15%). "
                "Use when the CEO asks 'what needs my attention', 'which assets are struggling', "
                "'where should I focus', or 'what are the problem areas'."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_collections_priority",
            "description": (
                "Get the prioritized list of tenants with overdue payments, ranked by "
                "collection urgency: amount overdue (40%), days overdue (30%), tenant risk "
                "score (30%). Use when the CEO asks about collections, overdue payments, "
                "'who owes us money', receivables risk, or delinquent tenants."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_zone_deep_dive",
            "description": (
                "Deep dive into a specific Pearl Qatar zone showing all assets in that zone, "
                "occupancy per asset, lease expiry exposure, maintenance burden, and receivables. "
                "Use when the CEO asks about a specific zone like 'tell me about Porto Arabia', "
                "'how is Medina Centrale', 'Viva Bahriya performance', or any zone-specific question. "
                "Available zones: Porto Arabia, Viva Bahriya, Medina Centrale, Qanat Quartier, "
                "Abraj Quartier, The Waterfront, Floresta Gardens, Giardino Village."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "zone_name": {
                        "type": "string",
                        "description": (
                            "The exact zone name. Must be one of: Porto Arabia, Viva Bahriya, "
                            "Medina Centrale, Qanat Quartier, Abraj Quartier, The Waterfront, "
                            "Floresta Gardens, Giardino Village"
                        ),
                    }
                },
                "required": ["zone_name"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
]


# ═══════════════════════════════════════════════════════════════
# TOOL IMPLEMENTATIONS — map tool names to governed functions
# ═══════════════════════════════════════════════════════════════

def _wrap_attention_index() -> dict[str, Any]:
    """Wrap asset attention index with metadata for C1 transparency."""
    results = calculate_asset_attention_index()
    return {
        "assets": results,
        "total_scored": len(results),
        "data_status": "GOVERNED",
        "scoring_version": "v1.0",
        "weights": {
            "vacancy_gap": 0.30,
            "overdue_work_orders": 0.20,
            "receivables_90plus": 0.20,
            "complaint_rate": 0.15,
            "lease_expiry_concentration": 0.15,
        },
    }


def _wrap_collections_priority() -> dict[str, Any]:
    """Wrap collections priority with metadata for C1 transparency."""
    results = calculate_collections_priority()
    return {
        "tenants": results,
        "total_flagged": len(results),
        "data_status": "GOVERNED",
        "scoring_version": "v1.0",
        "weights": {
            "amount_overdue": 0.40,
            "days_overdue": 0.30,
            "tenant_risk_score": 0.30,
        },
    }


TOOL_IMPLEMENTATIONS: dict[str, Callable[..., str]] = {
    "get_executive_overview": lambda **kwargs: _to_json(get_executive_overview()),
    "get_commercial_leasing_dashboard": lambda **kwargs: _to_json(get_commercial_leasing()),
    "get_finance_dashboard": lambda **kwargs: _to_json(get_finance_dashboard()),
    "get_maintenance_dashboard": lambda **kwargs: _to_json(get_maintenance_dashboard()),
    "get_asset_attention_index": lambda **kwargs: _to_json(_wrap_attention_index()),
    "get_collections_priority": lambda **kwargs: _to_json(_wrap_collections_priority()),
    "get_zone_deep_dive": lambda zone_name, **kwargs: _to_json(get_zone_deep_dive(zone_name)),
}
