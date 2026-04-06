"""Test all metric and scoring functions return valid, non-empty data."""
import json
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


def test_executive_overview():
    data = get_executive_overview()
    assert data["data_status"] == "GOVERNED"
    assert data["portfolio"]["total_units"] > 0
    assert data["portfolio"]["leased_units"] > 0
    assert data["portfolio"]["occupancy_rate_pct"] > 0
    assert data["revenue"]["current_month_qar"] > 0
    assert data["profitability"]["ebitda_qar"] is not None
    assert data["cash_position"]["cash_balance_qar"] != 0
    assert data["receivables"]["total_outstanding_qar"] > 0
    assert len(data["vacancy_by_zone"]) >= 6
    assert len(data["worst_performing_assets"]) == 5
    assert len(data["best_performing_assets"]) == 5
    assert len(data["revenue_trend"]) >= 6
    assert len(data["cashflow_trend"]) >= 6
    assert "executive_alerts" in data
    assert data["validation"]["occupancy_check"] == True
    # EBITDA margin should be between 0 and 100
    margin = data["profitability"]["ebitda_margin_pct"]
    assert -50 < margin < 80, f"EBITDA margin {margin}% looks unrealistic"
    print("  get_executive_overview: PASSED")


def test_commercial_leasing():
    data = get_commercial_leasing()
    assert data["data_status"] == "GOVERNED"
    assert data["summary"]["total_units"] > 0
    assert data["summary"]["occupancy_rate_pct"] > 0
    assert len(data["occupancy_by_zone"]) > 0
    assert len(data["occupancy_by_unit_type"]) > 0
    assert data["lease_expiry_profile"]["next_3_months"] >= 0
    assert len(data["top_tenants"]) > 0
    assert data["tenant_concentration"]["top_5_pct_of_revenue"] > 0
    print("  get_commercial_leasing: PASSED")


def test_finance():
    data = get_finance_dashboard()
    assert data["data_status"] == "GOVERNED"
    assert len(data["monthly_trend"]) >= 6
    assert len(data["receivables_aging"]) > 0
    assert data["cost_structure"]["staff_cost_qar"] > 0
    assert data["cost_structure"]["staff_pct_of_revenue"] > 0
    # Verify aging buckets exist
    buckets = {r["aging_bucket"] for r in data["receivables_aging"]}
    assert "90+" in buckets or len(buckets) >= 2
    print("  get_finance_dashboard: PASSED")


def test_maintenance():
    data = get_maintenance_dashboard()
    assert data["data_status"] == "GOVERNED"
    assert data["work_orders"]["total"] > 0
    assert data["work_orders"]["open"] > 0
    assert 0 < data["work_orders"]["first_time_fix_rate_pct"] < 100
    assert 0 < data["work_orders"]["repeat_rate_pct"] < 50
    assert len(data["worst_assets"]) > 0
    assert len(data["by_category"]) > 0
    assert len(data["contractor_performance"]) > 0
    assert data["tenant_satisfaction"]["avg_csat"] is not None
    print("  get_maintenance_dashboard: PASSED")


def test_zone_deep_dive():
    data = get_zone_deep_dive("Porto Arabia")
    assert data["data_status"] == "GOVERNED"
    assert data["zone_name"] == "Porto Arabia"
    assert data["summary"]["total_units"] > 0
    assert len(data["assets"]) > 0
    print("  get_zone_deep_dive('Porto Arabia'): PASSED")


def test_asset_attention():
    data = calculate_asset_attention_index()
    assert len(data) > 0
    first = data[0]
    assert "attention_index" in first
    assert 0 <= first["attention_index"] <= 100
    assert first["priority"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    # Verify sorted descending
    scores = [d["attention_index"] for d in data]
    assert scores == sorted(scores, reverse=True), "Not sorted descending"
    print("  calculate_asset_attention_index: PASSED")


def test_collections():
    data = calculate_collections_priority()
    assert len(data) > 0
    first = data[0]
    assert "collection_priority_score" in first
    assert first["total_overdue"] > 0
    assert first["priority_level"] in ["CRITICAL", "HIGH", "MEDIUM"]
    print("  calculate_collections_priority: PASSED")


if __name__ == "__main__":
    print("\n=== TESTING ALL METRIC AND SCORING FUNCTIONS ===\n")
    test_executive_overview()
    test_commercial_leasing()
    test_finance()
    test_maintenance()
    test_zone_deep_dive()
    test_asset_attention()
    test_collections()
    print("\nALL 7 FUNCTIONS PASSED\n")
