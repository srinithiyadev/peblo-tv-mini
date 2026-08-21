# Peblo TV Mini

## What I built
This is a small TV content platform with an Admin React UI, FastAPI/PostgreSQL backend, Viewer React UI, Docker Compose and GitHub Actions. The main flow is Admin → API/database → publish → catalogue → Viewer.

## How to run
From the project root:
`docker compose up --build`

Backend: http://localhost:8000  
Admin: http://localhost:5173  
Viewer: http://localhost:5174

Backend tests:
`cd backend && source venv/bin/activate && PYTHONPATH=. pytest -q`

## Main decisions

### Publishing
The viewer reads a published catalogue instead of querying the editing database directly. This gives the viewer a stable snapshot and separates editing from what users see.

If the process stops during publishing, the previous usable catalogue should remain available. For a production system I would make the temporary-file/atomic-rename and rollback behaviour more explicit.

### Storage
Storage is kept simple/local for this assignment. I would keep access behind a storage layer so local storage could later be replaced by Cloudflare R2 without changing the rest of the application.

### Search
Search and filters are handled by the backend and are enough for the supplied dataset. I would not keep a simple catalogue scan for a very large dataset. I would move the search to indexed PostgreSQL queries or a search service.

### Why a published catalogue
A pre-published catalogue keeps viewer reads simple and predictable. The trade-off is that edited content is not visible until another publish happens, and the catalogue has to be regenerated.

## What I completed
- FastAPI backend
- PostgreSQL through Docker Compose
- Admin UI
- Viewer UI
- Catalogue API and search
- Validation report
- Publish history
- Docker Compose
- GitHub Actions
- Backend API tests
- Environment example
- Seeded catalogue data

## What I left out / limitations
This is not presented as production-ready. Authentication/role enforcement, full artwork-upload management and some editorial CRUD flows are simplified or incomplete.

The supplied seed data is intentionally imperfect. The validation report exposes issues such as missing artwork and missing sections instead of hiding them.

## AI usage
I used AI mainly for debugging, explaining errors and checking implementation approaches. I checked generated changes against the actual errors and tests instead of blindly keeping them.

## Approximate time
Backend/API 35% · Admin 20% · Viewer 20% · Docker/CI 15% · Testing/documentation 10%.

## Final note
This is a take-home implementation, not a claim that the system is production-ready. I focused on getting the main CMS → publish → catalogue → viewer flow working and being honest about the remaining limitations.
