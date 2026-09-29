# Graph Report - .  (2026-08-30)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 345 nodes · 500 edges · 29 communities (25 shown, 4 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 5 edges (avg confidence: 0.64)
- Token cost: 1,046 input · 64 output

## Graph Freshness
- Built from commit: `1d6e53cb`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Backend Auth and Database
- Frontend Dev Dependencies
- TypeScript App Config
- Frontend Auth and Layout
- compilerOptions
- booking_guest.py
- Frontend Production Dependencies
- assets.py
- Document RAG Management
- API (Backend)
- orchestrator.py
- init.sql
- tsconfig.json
- Frontend Entry Point
- Backend Dev Dependencies
- ft_rental_architecture (Booking Platform)
- rag_lifecycle_test.py
- concurrency_test.py
- rag_security_test.py
- rag_debug.py
- rag_e2e_test.py
- rag_scope_test.py
- test_full_user_and_booking_lifecycle

## God Nodes (most connected - your core abstractions)
1. `User` - 20 edges
2. `compilerOptions` - 17 edges
3. `compilerOptions` - 15 edges
4. `run_agent_loop()` - 13 edges
5. `upload_document()` - 9 edges
6. `get_db()` - 8 edges
7. `check_asset_availability()` - 7 edges
8. `process_document()` - 7 edges
9. `ingest_document_chunks()` - 7 edges
10. `query_documents()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `API (Backend)` --references--> `Backend Dependencies`  [INFERRED]
  docker-compose.yml → backend/requirements.txt
- `Frontend` --references--> `Frontend Documentation`  [INFERRED]
  docker-compose.yml → frontend/README.md
- `Frontend Entry Point` --references--> `Hero Image`  [INFERRED]
  frontend/index.html → frontend/src/assets/hero.png
- `Frontend Documentation` --references--> `React Logo`  [EXTRACTED]
  frontend/README.md → frontend/src/assets/react.svg
- `Frontend Documentation` --references--> `Vite Logo`  [EXTRACTED]
  frontend/README.md → frontend/src/assets/vite.svg

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Rental Application Infrastructure** — docker_compose_gatekeeper, docker_compose_api, docker_compose_frontend, docker_compose_db, docker_compose_redis [EXTRACTED 1.00]

## Communities (29 total, 4 thin omitted)

### Community 0 - "Backend Auth and Database"
Cohesion: 0.08
Nodes (41): get_db(), get_redis(), get_current_user(), AsyncSession, Base, User, get_current_user(), google_login() (+33 more)

### Community 1 - "Frontend Dev Dependencies"
Cohesion: 0.06
Nodes (33): autoprefixer, eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, devDependencies, autoprefixer, eslint (+25 more)

### Community 2 - "TypeScript App Config"
Cohesion: 0.09
Nodes (22): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection, moduleResolution (+14 more)

### Community 3 - "Frontend Auth and Layout"
Cohesion: 0.09
Nodes (22): authService, CompleteProfileData, LoginResponse, RegisterData, apiClient, App(), Navbar(), navItems (+14 more)

### Community 4 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 5 - "booking_guest.py"
Cohesion: 0.60
Nodes (4): BookingGuestBase, BookingGuestCreate, BookingGuestResponse, BaseModel

### Community 6 - "Frontend Production Dependencies"
Cohesion: 0.07
Nodes (28): axios, country-list, dependencies, axios, country-list, lucide-react, react, react-dom (+20 more)

### Community 7 - "assets.py"
Cohesion: 0.19
Nodes (16): Asset, Base, check_asset_availability(), create_asset(), get_all_assets(), AsyncSession, get, post (+8 more)

### Community 8 - "Document RAG Management"
Cohesion: 0.10
Nodes (31): Document, Base, delete_document(), list_documents(), process_document_background(), AsyncSession, get, post (+23 more)

### Community 9 - "API (Backend)"
Cohesion: 0.22
Nodes (9): Backend Dependencies, API (Backend), Database (PostgreSQL), Frontend, Gatekeeper (Nginx), Redis, Frontend Documentation, React Logo (+1 more)

### Community 10 - "orchestrator.py"
Cohesion: 0.19
Nodes (17): AsyncSession, run_agent_loop(), AgentDecision, BaseModel, AsyncSession, tool_get_booking(), tool_get_property(), tool_get_user_bookings() (+9 more)

### Community 11 - "init.sql"
Cohesion: 0.60
Nodes (5): assets, booking_guests, bookings, documents, users

### Community 18 - "ft_rental_architecture (Booking Platform)"
Cohesion: 0.20
Nodes (9): 🏗️ Architecture Overview, Environment Variables, ft_rental_architecture (Booking Platform), 🚀 Getting Started, ✨ Key Features & Defense Mechanisms, Make Commands Reference, Prerequisites, Running the Project (+1 more)

### Community 19 - "rag_lifecycle_test.py"
Cohesion: 0.47
Nodes (4): main(), End-to-End RAG Lifecycle Test. Verifies source attribution accuracy, document…, sep(), wait_for_ready()

### Community 20 - "concurrency_test.py"
Cohesion: 0.70
Nodes (4): create_asset(), create_user_and_login(), main(), make_booking_request()

### Community 21 - "rag_security_test.py"
Cohesion: 0.50
Nodes (3): main(), Security End-to-End RAG Test. Verifies file validation, prompt injection…, sep()

### Community 22 - "rag_debug.py"
Cohesion: 0.67
Nodes (3): divider(), main(), RAG Pipeline Diagnostic Script Traces a complete query from embedding →…

### Community 23 - "rag_e2e_test.py"
Cohesion: 0.67
Nodes (3): main(), End-to-end RAG pipeline test. Creates a user, uploads a test PDF document,…, sep()

### Community 24 - "rag_scope_test.py"
Cohesion: 0.83
Nodes (3): get_auth_token(), main(), run_test()

## Knowledge Gaps
- **94 isolated node(s):** `Config`, `name`, `private`, `version`, `type` (+89 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `Backend Auth and Database` to `Document RAG Management`, `orchestrator.py`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Why does `devDependencies` connect `Frontend Dev Dependencies` to `Frontend Production Dependencies`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **What connects `Config`, `name`, `private` to the rest of the system?**
  _94 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Backend Auth and Database` be split into smaller, more focused modules?**
  _Cohesion score 0.07692307692307693 - nodes in this community are weakly interconnected._
- **Should `Frontend Dev Dependencies` be split into smaller, more focused modules?**
  _Cohesion score 0.06060606060606061 - nodes in this community are weakly interconnected._
- **Should `TypeScript App Config` be split into smaller, more focused modules?**
  _Cohesion score 0.08695652173913043 - nodes in this community are weakly interconnected._
- **Should `Frontend Auth and Layout` be split into smaller, more focused modules?**
  _Cohesion score 0.08739495798319327 - nodes in this community are weakly interconnected._