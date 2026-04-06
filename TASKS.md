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
- [ ] Create backend/metric_registry.py with all Phase 1 metric definitions
- [ ] Define once, reuse everywhere — no duplicate metric definitions

### Step 4: Deterministic Metrics Engine
- [ ] Create backend/metrics.py with 4 dashboard functions:
  - [ ] get_executive_overview() — with enhanced version (trends, alerts, narrative context)
  - [ ] get_commercial_leasing()
  - [ ] get_finance_dashboard()
  - [ ] get_maintenance_dashboard()
- [ ] Create backend/scoring.py with 2 scoring functions:
  - [ ] calculate_asset_attention_index()
  - [ ] calculate_collections_priority()
- [ ] Create get_zone_deep_dive(zone_name) for drill-downs
- [ ] Test: each function returns valid JSON with correct structure
- [ ] Test: all numbers trace to SQL queries (no hardcoded values)
- [ ] Test: validation checks pass (occupancy numerator <= denominator, aging buckets sum to total AR)

### Step 5: Tool Definitions
- [ ] Create backend/tools.py with 7 tool definitions + implementations
- [ ] Each tool has OpenAI-compatible JSON schema
- [ ] Each tool maps to a governed metrics/scoring function
- [ ] Test: each tool_implementation returns valid JSON

### Step 6: System Prompt
- [ ] Create backend/system_prompt.py with the enhanced 5-layer prompt
- [ ] Verify prompt includes: visual-first rules, color language, priority badges, drill-down patterns, CEO question mapping

### Step 7: FastAPI Backend
- [ ] Create backend/main.py with:
  - [ ] C1 API client setup
  - [ ] Tool calling loop (call → execute → return → repeat until done)
  - [ ] Streaming response with thesys_genui_sdk
  - [ ] Thinking states for each tool call
  - [ ] In-memory message store
  - [ ] CORS middleware
- [ ] Test: POST /api/chat with a test prompt returns streaming C1 response
- [ ] Test: tool calls execute correctly and return governed data
- [ ] Test: thinking states appear in response stream

### Step 8: Next.js Frontend
- [ ] Create frontend with C1Chat component
- [ ] Configure: full-page layout, carbon dark theme, UDC branding
- [ ] Add suggested prompts matching CEO workflows
- [ ] Set up API proxy to FastAPI backend
- [ ] Test: open http://localhost:3000 — C1Chat renders
- [ ] Test: type "How are we doing?" — full executive dashboard appears
- [ ] Test: drill-down buttons work — clicking triggers new tool calls
- [ ] Test: thinking states visible during loading

### Step 9: Integration Testing
- [ ] Test all 7 tools through the full stack (frontend → backend → C1 → tool → render)
- [ ] Test conversational flow (overview → drill into zone → drill into asset)
- [ ] Verify no numbers are LLM-invented (all trace to database)
- [ ] Verify data_status = "GOVERNED" appears on all dashboards
- [ ] Verify QAR formatting is correct throughout

### Step 10: Git Commit
- [ ] Clean up any test files
- [ ] Final commit and push to GitHub
