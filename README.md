# FastAPI TODO App

A web-based TODO application built with FastAPI, SQLAlchemy, Jinja2 templates, SQLite, and Bootstrap. Users can register, log in, manage their own TODO items, update account details, and use JWT-based authentication.

## Features

- User registration and login
- JWT authentication
- Create, read, update, and delete TODO items
- User-specific TODO lists
- Admin endpoints for managing TODO records
- Password and phone number update endpoints
- Server-rendered HTML pages with Jinja2
- SQLite database for local development
- Alembic database migrations
- Automated tests with pytest

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- Alembic
- SQLite
- Pydantic
- Jinja2
- Bootstrap
- Pytest

## Project Structure

```text
TODOapp/
  alembic/       Database migration files
  routers/       API and page route modules
  static/        CSS and JavaScript assets
  templates/     Jinja2 HTML templates
  test/          Pytest test suite
  database.py    Database engine and session setup
  main.py        FastAPI application entry point
  models.py      SQLAlchemy database models
```

## Setup

Create and activate a virtual environment:

```bash
python -m venv fastapienv
fastapienv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local `.env` file using the variables shown in `.env.example`:

```env
TODOAPP_SECRET_KEY=replace-with-a-long-random-secret
TODOAPP_DATABASE_URL=sqlite:///./todosapp.db
```

For local development, SQLite is used by default.

## Running The App

Start the development server:

```bash
uvicorn TODOapp.main:app --reload
```

Open the app in your browser:

```text
http://127.0.0.1:8000
```

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Database Migrations

Run Alembic migrations:

```bash
alembic -c TODOapp/alembic.ini upgrade head
```

The app also creates SQLite tables locally when it starts, but migrations are included so the database schema can be recreated cleanly.

## Running Tests

```bash
pytest TODOapp/test
```

Current test coverage includes authentication, user routes, TODO routes, admin routes, and the health check endpoint.

## Security Notes

- The real JWT secret should be stored in `TODOAPP_SECRET_KEY`, not hardcoded in source code.
- Local `.env` files and SQLite database files are ignored by Git.
- New registered users are assigned the `user` role by default.
- User API responses do not expose password hashes.

## Status

This project is a learning-focused FastAPI application prepared for public GitHub sharing. It is suitable as a portfolio project and local demo, but production deployment would require additional hardening such as HTTPS-only cookies, CSRF protection for browser-based form flows, stronger password policies, and production database configuration.
