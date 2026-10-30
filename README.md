# TaskBoard

A simple task manager. Users sign up, log in, and manage their own to-do list. Everything is saved in a PostgreSQL database through my own REST API.

| | |
|---|---|
| **Live app** | https://taskboard-three-brown.vercel.app |
| **Live API** | https://taskboard-api-anuj.onrender.com |
| **Health check** | https://taskboard-api-anuj.onrender.com/api/health |
| **API docs (Swagger)** | https://taskboard-api-anuj.onrender.com/docs |
| **Repository** | https://github.com/Anujwavekar/taskboard |

## Demo login

```
Email:    demo@taskboard.com
Password: Demo@123
```

The demo account has six sample tasks, including one overdue task and one completed task, so every screen state is visible.

> **Free-tier note: the first load can take up to a minute.**
> The backend (Render) and the database (Neon) both go to sleep when idle. The first request after a quiet period wakes them up. The app shows a "Waking up the server" message while this happens. After that it is fast.

## Features

**Must have**
- Sign up (name, email, password), log in, log out. The session persists until the user logs out
- Each user sees only their own tasks, with Total / Pending / Completed counts
- Add a task: title (required), description, priority (Low / Medium / High, default Medium), due date
- Edit any field; delete asks "Are you sure?"
- Checkbox marks done (strike-through) or pending; counts update immediately
- Filter tabs (All / Pending / Completed), title search and sort by due date or priority, all working together
- Responsive layout (checked at 375px, no sideways scroll), with a floating + button on phones
- Loading, error (with Retry) and empty states

**Extras**
- Overdue tasks shown in red
- Dark mode toggle (remembered, defaults to the system setting)
- Automated API tests (pytest)
- Rate limiting on login and signup

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 19 (Vite), React Router, plain CSS |
| Backend | Python, FastAPI, Uvicorn |
| Validation | Pydantic v2 (server) and matching checks in the forms (client) |
| Database | PostgreSQL on Neon, SQLAlchemy 2.0, Alembic migrations |
| Auth | bcrypt password hashing, JWT (PyJWT) |
| Tests | pytest + FastAPI TestClient |
| Hosting | Vercel (frontend), Render (backend), Neon (database) |

## Architecture

```
Browser  ->  React app (Vercel)  ->  FastAPI (Render)  ->  PostgreSQL (Neon)
                  HTTPS + JWT in the Authorization header     private connection string
```

The browser never talks to the database. Every request to the API goes through authentication, validation and an ownership check.

```
backend/
  app/
    main.py          app setup, CORS, error handlers, rate limiter
    core/            config, security (bcrypt/JWT), error format, limiter
    db/              engine, session, declarative base
    models/          SQLAlchemy tables (users, tasks)
    schemas/         Pydantic request/response shapes and validation
    routers/         URL definitions only
    services/        business logic and database queries
    api/deps.py      get_db and get_current_user
  alembic/           migrations
  scripts/seed.py    demo user and sample tasks
  tests/             pytest tests
frontend/
  src/
    api/             API client (base URL, token, auto-logout on 401)
    context/         AuthContext
    hooks/           useTasks (fetching, filters, mutations)
    pages/           LoginPage, TasksPage
    components/      Header, TaskItem, TaskFormModal, ConfirmDialog, States
    routes/          ProtectedRoute
    utils/           date helpers
```

## API endpoints

All task endpoints require the header `Authorization: Bearer <token>`.

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/health` | No | Returns `OK` |
| POST | `/api/auth/signup` | No | Create an account. Body: `name`, `email`, `password` (8-72 chars). `201` with token and user, `409` if the email exists |
| POST | `/api/auth/login` | No | Body: `email`, `password`. `200` with token and user, `401` "Invalid email or password" |
| GET | `/api/auth/me` | Yes | The current user (used to check a stored token) |
| GET | `/api/tasks` | Yes | My tasks plus counts. Query: `status` = all / pending / completed, `search` (title), `sort` = due_date / priority |
| POST | `/api/tasks` | Yes | Create a task. Body: `title` (required), `description`, `priority`, `due_date`. `201` |
| PUT | `/api/tasks/{id}` | Yes | Update any fields (partial update, including `is_completed`). `404` if not found or not mine |
| DELETE | `/api/tasks/{id}` | Yes | Delete a task. `204`, or `404` if not found or not mine |

**List response**
```json
{ "tasks": [ ... ], "counts": { "total": 6, "pending": 5, "completed": 1 } }
```
The counts cover all of the user's tasks and ignore the active filter.

**Error format.** Every error has a `message`. Validation errors (`422`) also have `errors`, one message per field:
```json
{ "message": "Please fix the highlighted fields", "errors": { "title": "Title is required" } }
```

## Run locally

Prerequisites: Python 3.11+, Node 18+, Git, and a PostgreSQL database (a free Neon project works).

```bat
git clone https://github.com/Anujwavekar/taskboard.git
cd taskboard
```

**Backend** (Windows; on Mac/Linux use `source venv/bin/activate` and `cp`)
```bat
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```
Edit `backend\.env` (see the table below), then:
```bat
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload
```
The API runs at http://localhost:8000 (docs at `/docs`).

**Frontend** (in a second terminal)
```bat
cd frontend
npm install
copy .env.example .env
npm run dev
```
The app runs at http://localhost:5173. Log in with the demo account.

## Environment variables

| Variable | Where | Purpose |
|---|---|---|
| `DATABASE_URL` | backend | PostgreSQL URL, in the form `postgresql+psycopg://USER:PASSWORD@HOST/DB?sslmode=require` |
| `JWT_SECRET` | backend | Secret that signs login tokens. Use a long random value |
| `CLIENT_URL` | backend | The frontend's URL, allowed by CORS |
| `JWT_EXPIRE_DAYS` | backend | Token lifetime (default 7) |
| `VITE_API_URL` | frontend | The API's base URL |

Real values live in `.env` files and platform settings. They are never committed (`.env.example` files show the names only).

## Tests

```bat
cd backend
venv\Scripts\activate
pytest -v
```

The tests use an in-memory SQLite database, so they never touch real data. They cover signup and login, hashing, validation, task CRUD, filter / search / sort, counts, rate limiting, and ownership (one user cannot see, edit, complete or delete another user's task).

## Security notes

- Passwords are hashed with bcrypt (salted), and the hash is never returned by the API
- Login uses a signed JWT; the user id always comes from the token, never from the request body
- **Ownership check:** every task query matches on both the task id and the owner. Someone else's task returns `404`, so its existence isn't revealed
- Validation runs in the forms and again on the server (for example an empty title is rejected with `422`)
- Wrong email and wrong password give the same message, with similar response time
- Rate limiting on signup (5/min) and login (10/min) per client IP
- CORS allows only the frontend's URL; secrets live in environment variables
- Queries go through SQLAlchemy (parameterized), which prevents SQL injection

Trade-offs I accepted for this assignment:
- The token is stored in `localStorage` because the frontend and API are on different domains. This keeps it simple, but httpOnly cookies would resist XSS better
- The rate limiter keeps counts in memory (one instance) and trusts the first `X-Forwarded-For` address

## Deployment

| Part | Platform | Notes |
|---|---|---|
| Frontend | Vercel | Root directory `frontend`; `vercel.json` rewrites all paths to the app so refreshing `/tasks` works |
| Backend | Render (free web service) | Root directory `backend`; start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Database | Neon (free PostgreSQL) | Same region as the backend; only the backend knows the connection string |

Database changes are applied with `alembic upgrade head`. To reset the demo account, run `python -m scripts.seed`.

## AI usage

I used Claude (Anthropic) as an assistant to plan the architecture, draft code, and debug errors during setup and deployment. I ran and tested everything myself, I reviewed the code, and I can explain how each part works.