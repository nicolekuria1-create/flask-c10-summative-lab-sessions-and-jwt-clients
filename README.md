# Full Auth Flask Backend - Notes API

## Project Description
This project is a secure Flask REST API for a productivity Notes app. It implements session-based authentication, user-owned notes, and protected CRUD endpoints with pagination so each user can only access their own records.

## Features
- Session auth: signup, login, logout, check session
- Secure password hashing with Flask-Bcrypt
- User-owned `Note` resource with full CRUD
- Authorization checks on all resource routes
- Pagination on notes index route
- Seed script to generate sample users and notes
- Flask-Migrate configuration for database migrations

## Tech Stack
- Flask
- Flask-RESTful
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Bcrypt
- Marshmallow
- SQLite (default)

## Installation
1. Clone the repo and open it in VS Code.
2. Install dependencies:

```bash
pipenv install
```

3. Activate shell:

```bash
pipenv shell
```

## Database Setup
1. Initialize migrations (first time only):

```bash
flask db init
```

2. Create migration:

```bash
flask db migrate -m "initial migration"
```

3. Apply migration:

```bash
flask db upgrade
```

4. Seed the database:

```bash
python seed.py
```

## Run Instructions
Run the API server:

```bash
flask run
```

Or:

```bash
python app.py
```

Base URL:

```text
http://127.0.0.1:5555
```

## API Endpoints

### Auth Endpoints
- `POST /signup`
  - Creates a user and starts a session.
  - Body: `{ "username": "string", "password": "string" }`
  - Returns: user object (`201`) or error (`400`, `409`)

- `POST /login`
  - Logs in an existing user.
  - Body: `{ "username": "string", "password": "string" }`
  - Returns: user object (`200`) or error (`400`, `401`)

- `DELETE /logout`
  - Logs out current user.
  - Returns: empty body (`204`) or error (`401`)

- `GET /check_session`
  - Returns currently logged-in user if session is valid.
  - Returns: user object (`200`) or error (`401`)

### Notes Endpoints (Protected)
- `GET /notes?page=1&per_page=10`
  - Returns paginated notes owned by current user.
  - Returns: pagination object with `items`, `page`, `per_page`, `total`, `pages` (`200`)

- `GET /notes/<id>`
  - Returns one note owned by current user.
  - Returns: note object (`200`) or error (`401`, `404`)

- `POST /notes`
  - Creates a note for current user.
  - Body: `{ "title": "string", "content": "string", "mood": "optional string" }`
  - Returns: created note (`201`) or error (`400`, `401`)

- `PATCH /notes/<id>`
  - Updates note fields for a note owned by current user.
  - Body: any of `{ "title", "content", "mood" }`
  - Returns: updated note (`200`) or error (`400`, `401`, `404`)

- `DELETE /notes/<id>`
  - Deletes a note owned by current user.
  - Returns: empty body (`204`) or error (`401`, `404`)

## Project Structure
```text
.
├── app.py
├── config.py
├── extensions.py
├── models.py
├── schemas.py
├── seed.py
├── Pipfile
├── README.md
├── instance/
├── migrations/
└── tests/
```

## Security Notes
- Passwords are hashed with bcrypt before storage.
- Usernames are unique.
- All notes routes require authentication.
- Note queries are scoped by `user_id`, preventing cross-user access.

## Suggested Test Flow (Postman)
1. `POST /signup`
2. `GET /check_session`
3. `POST /notes`
4. `GET /notes?page=1&per_page=5`
5. `PATCH /notes/<id>`
6. `DELETE /notes/<id>`
7. `DELETE /logout`
8. `GET /check_session` (should return `401`)
