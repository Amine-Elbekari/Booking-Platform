# Graph Report - .  (2026-07-30)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 223 nodes · 291 edges · 18 communities (15 shown, 3 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 4 edges (avg confidence: 0.68)
- Token cost: 674 input · 41 output

## Graph Freshness
- Built from commit: `0946d45c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- User Authentication and Management
- Frontend Development Tools
- TypeScript App Configuration
- Frontend Services and UI
- compilerOptions
- UUID
- dependencies
- assets.py
- package.json
- API (Backend)
- create_booking
- init.sql
- tsconfig.json
- Frontend Entry Point
- Backend Dev Dependencies

## God Nodes (most connected - your core abstractions)
1. `compilerOptions` - 17 edges
2. `compilerOptions` - 15 edges
3. `User` - 13 edges
4. `get_db()` - 7 edges
5. `login()` - 6 edges
6. `create_user()` - 6 edges
7. `create_asset()` - 5 edges
8. `google_login()` - 5 edges
9. `create_booking()` - 5 edges
10. `complete_profile()` - 5 edges

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

## Communities (18 total, 3 thin omitted)

### Community 0 - "User Authentication and Management"
Cohesion: 0.12
Nodes (27): get_db(), get_current_user(), AsyncSession, Base, User, get_current_user(), google_login(), login() (+19 more)

### Community 1 - "Frontend Development Tools"
Cohesion: 0.06
Nodes (33): autoprefixer, eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, devDependencies, autoprefixer, eslint (+25 more)

### Community 2 - "TypeScript App Configuration"
Cohesion: 0.09
Nodes (22): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection, moduleResolution (+14 more)

### Community 3 - "Frontend Services and UI"
Cohesion: 0.16
Nodes (10): authService, CompleteProfileData, LoginResponse, RegisterData, apiClient, App(), CompleteProfile(), COUNTRIES (+2 more)

### Community 4 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 5 - "UUID"
Cohesion: 0.14
Nodes (11): BookingGuestBase, BookingGuestCreate, BookingGuestResponse, BaseModel, BaseModel, UserBase, UserCreate, UserResponse (+3 more)

### Community 6 - "dependencies"
Cohesion: 0.12
Nodes (17): axios, country-list, dependencies, axios, country-list, react, react-dom, react-hot-toast (+9 more)

### Community 7 - "assets.py"
Cohesion: 0.23
Nodes (11): Asset, Base, create_asset(), get_all_assets(), AsyncSession, get, post, AssetBase (+3 more)

### Community 8 - "package.json"
Cohesion: 0.20
Nodes (9): name, private, scripts, build, dev, lint, preview, type (+1 more)

### Community 9 - "API (Backend)"
Cohesion: 0.22
Nodes (9): Backend Dependencies, API (Backend), Database (PostgreSQL), Frontend, Gatekeeper (Nginx), Redis, Frontend Documentation, React Logo (+1 more)

### Community 10 - "create_booking"
Cohesion: 0.32
Nodes (7): create_booking(), AsyncSession, post, BookingBase, BookingCreate, BookingResponse, BaseModel

### Community 11 - "init.sql"
Cohesion: 0.70
Nodes (4): assets, booking_guests, bookings, users

## Knowledge Gaps
- **78 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+73 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `devDependencies` connect `Frontend Development Tools` to `package.json`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `dependencies` connect `dependencies` to `package.json`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Why does `User` connect `User Authentication and Management` to `create_booking`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _78 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `User Authentication and Management` be split into smaller, more focused modules?**
  _Cohesion score 0.11746031746031746 - nodes in this community are weakly interconnected._
- **Should `Frontend Development Tools` be split into smaller, more focused modules?**
  _Cohesion score 0.06060606060606061 - nodes in this community are weakly interconnected._
- **Should `TypeScript App Configuration` be split into smaller, more focused modules?**
  _Cohesion score 0.08695652173913043 - nodes in this community are weakly interconnected._