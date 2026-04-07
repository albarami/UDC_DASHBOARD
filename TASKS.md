# UDC CEO Dashboard — Implementation Plan

## Status Legend
- [ ] Not started
- [x] Complete
- [🔄] In progress

## Phase 1 Build Steps

### Step 1: Environment Setup
- [x] Create project structure (backend/, frontend/, docs/)
- [x] Create backend/requirements.txt
- [x] Install backend dependencies
- [x] Create .gitignore
- [x] Verify .env and API keys

### Step 2: Synthetic Data Generation
- [x] Create backend/seed_data.py with 13 tables
- [x] Generate realistic Pearl Qatar data (assets, units, tenants, leases, receivables, work orders, complaints, finance, employees, contracts, subsidiaries, community fees, leads)
- [x] Run seed_data.py and verify database created
- [x] Test: verify row counts per table
- [x] Test: verify data integrity (foreign keys, realistic value ranges)
- [x] Test: run 3 sample queries to confirm data quality

### Step 3: Metric Registry
- [x] Create backend/metric_registry.py with all Phase 1 metric definitions
- [x] Define once, reuse everywhere — no duplicate metric definitions

### Step 4: Deterministic Metrics Engine
- [x] Create backend/metrics.py with 4 dashboard functions:
  - [x] get_executive_overview() — with enhanced version (trends, alerts, narrative context)
  - [x] get_commercial_leasing()
  - [x] get_finance_dashboard()
  - [x] get_maintenance_dashboard()
- [x] Create backend/scoring.py with 2 scoring functions:
  - [x] calculate_asset_attention_index()
  - [x] calculate_collections_priority()
- [x] Create get_zone_deep_dive(zone_name) for drill-downs
- [x] Test: each function returns valid JSON with correct structure
- [x] Test: all numbers trace to SQL queries (no hardcoded values)
- [x] Test: validation checks pass (occupancy numerator <= denominator, aging buckets sum to total AR)

### Step 5: Tool Definitions
- [x] Create backend/tools.py with 7 tool definitions + implementations
- [x] Each tool has OpenAI-compatible JSON schema
- [x] Each tool maps to a governed metrics/scoring function
- [x] Test: each tool_implementation returns valid JSON

### Step 6: System Prompt
- [x] Create backend/system_prompt.py with the enhanced 5-layer prompt
- [x] Verify prompt includes: visual-first rules, color language, priority badges, drill-down patterns, CEO question mapping

### Step 7: FastAPI Backend
- [x] Create backend/main.py with:
  - [x] C1 API client setup
  - [x] Tool calling loop (call → execute → return → repeat until done)
  - [x] Streaming response with thesys_genui_sdk
  - [x] Thinking states for each tool call
  - [x] In-memory message store
  - [x] CORS middleware
- [x] Test: POST /api/chat with a test prompt returns streaming C1 response
- [x] Test: tool calls execute correctly and return governed data
- [x] Test: thinking states appear in response stream

### Step 8: Next.js Frontend
- [x] Create frontend with C1Chat component
- [x] Configure: full-page layout, custom UDC dark theme, UDC branding
- [x] Add conversation starters matching CEO workflows (6 options)
- [x] Set up API proxy to FastAPI backend (streaming SSE)
- [x] Test: open http://localhost:3000 — C1Chat renders with dark theme
- [x] Test: type "How are we doing?" — full executive dashboard appears with KPIs, charts, tables
- [x] Test: drill-down buttons appear at bottom of response
- [x] Test: thinking states visible during loading ("Preparing your dashboard...")

### Step 9: Integration Testing
- [ ] Test all 7 tools through the full stack (frontend → backend → C1 → tool → render)
- [ ] Test conversational flow (overview → drill into zone → drill into asset)
- [ ] Verify no numbers are LLM-invented (all trace to database)
- [ ] Verify data_status = "GOVERNED" appears on all dashboards
- [ ] Verify QAR formatting is correct throughout

### Step 10: Git Commit
- [ ] Clean up any test files
- [ ] Final commit and push to GitHub
