# DevOps IP Address Management System (IPAM)

A secure, multi-site, production-ready IPAM platform built with FastAPI, React, PostgreSQL and Docker

## Features

- JWT auth in `httpOnly` cookies (`access_token` + `refresh_token`) with refresh rotation
- Mandatory first admin login setup (must change admin email and password before panel access)
- CSRF protection (double-submit cookie), strict CORS, and rate limiting
- Role-based access control (`ADMIN`, `VIEWER`)
- Multi-site IP management: Sites, Subnets, IP Addresses
- Smart free IP suggestion
- Network scan support (`nmap`/ARP) with conflict detection and IP persistence
- CSV import/export with validation and rollback safety
- Audit logs for sensitive operations
- Dashboard with usage metrics and dark mode

## Tech Stack

- Backend: FastAPI, SQLAlchemy 2 async, PostgreSQL, Alembic, Pydantic v2
- Security: python-jose (JWT), passlib + bcrypt, CSRF middleware
- Frontend: React, Vite, TypeScript, TailwindCSS, Axios
- Infra: Docker multi-stage, Docker Compose, Nginx reverse proxy, Certbot

## Project Structure

```text
backend/
  app/
  alembic/
frontend/
  src/
docker/
docker-compose.yml
.env.example
README.md
```

## Prerequisites

- Docker Engine
- Optional for local (non-Docker) run:
  - Python 3.12+
  - Node.js 20+

## Quick Start (Docker)

### 1) Create your environment file

Linux/macOS:

```bash
cp .env.example .env
```

PowerShell:

```powershell
Copy-Item .env.example .env
```

### 2) Update critical variables in `.env`

At minimum, set:

- `JWT_SECRET_KEY` (long random value, at least 32 chars)
- `POSTGRES_PASSWORD`
- `ADMIN_PASSWORD`
- `FRONTEND_URL`
- `CORS_ORIGINS` (strict origin format, comma-separated, no trailing slash, no path)

Example:

```env
FRONTEND_URL=http://localhost
CORS_ORIGINS=http://localhost
COOKIE_SECURE=false
```

### 3) Start the full stack

```bash
docker compose up --build -d
```

### 4) Open the app

- App: `http://localhost`
- API docs: `http://localhost/docs`
- Health: `http://localhost/health`

### 5) First admin login requirement

On first login with default admin credentials, the app forces you to change:

- Admin email
- Admin password

You cannot access the rest of the panel until this setup is completed.

## Default Credentials (for first run only)

- Email: value of `ADMIN_EMAIL` (default: `admin@ipam.local`)
- Password: value of `ADMIN_PASSWORD`

Change both immediately through the first-login setup screen.

## Useful Commands

```bash
make up
make down
make logs
make backend-lint
make backend-test
make frontend-lint
```

## Local Development (without Docker)

### Backend

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Main API Endpoints

- Auth: `/api/v1/auth/register`, `/login`, `/refresh`, `/logout`, `/me`, `/first-login-setup`, `/change-password`
- Users: `/api/v1/users`
- Sites: `/api/v1/sites`
- Subnets: `/api/v1/subnets`
- IPs: `/api/v1/ips`, `/ips/suggest/{subnet_id}`, `/ips/import`, `/ips/export`
- Scan: `/api/v1/scan/{subnet_id}`
- Dashboard: `/api/v1/dashboard/stats`

## Security Notes

- Keep `COOKIE_SECURE=true` in production (HTTPS required)
- Restrict `CORS_ORIGINS` to trusted domains only
- Never commit `.env` files or real secrets
- Consider adding SAST/DAST checks in CI/CD
- Optional distributed rate limiting is available with `REDIS_URL`

## WAN + HTTPS (Let's Encrypt)

1. Point your domain `A` record to your public IP
2. Forward ports `80` and `443` to your Docker host
3. Set in `.env`:
   - `DOMAIN_NAME=your-domain.com`
   - `LETSENCRYPT_EMAIL=you@your-domain.com`
   - `FRONTEND_URL=https://your-domain.com`
   - `CORS_ORIGINS=https://your-domain.com`
   - `COOKIE_SECURE=true`
4. Start stack:

```bash
docker compose up --build -d
```

5. Create certificate:

```bash
make tls-init
```

6. Reload Nginx:

```bash
docker compose restart nginx
```

Certificate renewal is handled by the `certbot` service. You can also run manual renewal:

```bash
make tls-renew
```

## Tests

- `backend/tests/test_health.py`
- `backend/tests/test_scan_service.py`
- `backend/tests/test_config.py`
