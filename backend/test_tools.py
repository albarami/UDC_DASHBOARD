"""Test that all 7 tools return valid JSON with governed data."""
import json
from tools import TOOL_DEFINITIONS, TOOL_IMPLEMENTATIONS


def test_all_tools():
    print("\n=== TESTING ALL 7 GOVERNED TOOLS ===\n")

    # Verify definitions and implementations match
    defined_names = {t["function"]["name"] for t in TOOL_DEFINITIONS}
    implemented_names = set(TOOL_IMPLEMENTATIONS.keys())
    assert defined_names == implemented_names, (
        f"Mismatch: defined={defined_names - implemented_names}, "
        f"implemented={implemented_names - defined_names}"
    )
    print(f"  Tool count: {len(defined_names)} defined, {len(implemented_names)} implemented — MATCH")

    # Test each tool returns valid JSON
    for tool_def in TOOL_DEFINITIONS:
        name = tool_def["function"]["name"]
        params = tool_def["function"]["parameters"]
        required = params.get("required", [])

        # Build test args
        test_args = {}
        if "zone_name" in required:
            test_args["zone_name"] = "Porto Arabia"

        # Call the tool
        result_str = TOOL_IMPLEMENTATIONS[name](**test_args)

        # Verify it's valid JSON
        result = json.loads(result_str)
        assert isinstance(result, (dict, list)), f"{name} returned {type(result)}, expected dict or list"

        # Verify governed status where applicable
        if isinstance(result, dict) and "data_status" in result:
            assert result["data_status"] == "GOVERNED", f"{name} data_status is not GOVERNED"

        print(f"  {name}: valid JSON, {len(result_str)} bytes — PASSED")

    print("\n  ALL 7 TOOLS PASSED\n")


if __name__ == "__main__":
    test_all_tools()
