# Ledgerly — Personal Expense & Income Tracker

Ledgerly is a responsive Flask finance tracker for recording income and expenses, setting monthly category budgets, and understanding spending with a private dashboard and reports.

## Features

- Secure registration, login, logout, password hashing, CSRF protection, and user-owned data.
- Unified income/expense transactions with categories, notes, payment methods, dates, search, pagination, editing, and safe delete confirmation.
- Dashboard totals, recent activity, monthly spending, budgets with progress warnings, and a Chart.js category report.
- SQLite locally and PostgreSQL-ready configuration for Render.

## Stack

Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Migrate, SQLite/PostgreSQL, Bootstrap 5, Chart.js, and pytest.

## Run locally on Windows

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

Open `http://127.0.0.1:5000`. Change `SECRET_KEY` in `.env` before using anything beyond local development. The local SQLite database is created in `instance/` on first run.

## Tests

```powershell
pytest
```

## Structure

`app/auth`, `app/transactions`, `app/budgets`, `app/reports`, and `app/profile` are Flask blueprints. `app/models.py` holds SQLAlchemy models and `app/services/` holds shared aggregation logic. Templates and static assets live under `app/templates` and `app/static`.

## Render deployment

1. Push this project to GitHub and create a Render Blueprint deployment from `render.yaml` (or create the web service/database manually with the commands in that file).
2. Render creates `SECRET_KEY`; never commit a real `.env` file.
3. Set `FLASK_CONFIG=production`. Render supplies `DATABASE_URL` from the attached PostgreSQL database.
4. The production command is `gunicorn run:app`.

For an explicit migration workflow after schema changes, run `flask --app run:app db init`, `flask --app run:app db migrate`, and `flask --app run:app db upgrade`. The app also initializes its tables on first launch for a simple first-run experience.
