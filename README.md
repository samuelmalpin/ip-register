# DevOps IP Address Management System (IPAM)

Plateforme IPAM sécurisée, multi-site et prête pour la production.

## Stack

- Backend: FastAPI, SQLAlchemy 2.0 async, PostgreSQL, Alembic, Pydantic v2, python-jose, passlib+bcrypt, loguru
- Frontend: React + Vite + TypeScript + TailwindCSS + Axios
- Infra: Docker multi-stage, Docker Compose, Nginx reverse proxy, healthchecks, volumes persistants

## Fonctionnalités

- Authentification JWT en cookies httpOnly (`access_token` + `refresh_token`) avec rotation refresh token
- Première connexion admin: changement obligatoire email + mot de passe avant accès au panel
- Protection CSRF (double-submit cookie), CORS strict, rate limiting middleware
- RBAC (`ADMIN`, `VIEWER`)
- Gestion multi-site: Sites, Subnets, IPs
- Suggestion d'IP libre intelligente via `ipaddress`
- Scan réseau optionnel via `nmap` (détection conflits)
- Import CSV sécurisé (schéma strict, taille max, rollback atomique)
- Export CSV contrôlé par RBAC
- Journal d’audit (qui modifie quoi)
- Dashboard (IPs par site/subnet, % libres) + mode sombre frontend

## Arborescence

```text
/backend
  /app
    /api
    /models
    /schemas
    /core
    /services
    /utils
  /alembic
  Dockerfile

/frontend
  /src
  Dockerfile

/docker
  nginx.conf

docker-compose.yml
.env.example
README.md
```

## Variables d’environnement

1. Copier `.env.example` vers `.env`
2. Remplir en priorité:
   - `JWT_SECRET_KEY` (>= 32 chars)
   - `POSTGRES_PASSWORD`
   - `ADMIN_PASSWORD`
  - `CORS_ORIGINS` (origines strictes, sans slash final, séparées par virgule)

## Lancement (Docker)

```bash
cp .env.example .env
docker compose up --build -d
```

Accès:
- App: `http://localhost`
- API docs: `http://localhost/docs`
- Health API: `http://localhost/health`

## Commandes utiles

```bash
make up
make down
make logs
make backend-lint
make backend-test
```

## Backend local (hors Docker)

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Frontend local (hors Docker)

```bash
cd frontend
npm install
npm run dev
```

## Sécurité appliquée

- Hash mots de passe: bcrypt (`passlib`)
- JWT access/refresh + rotation
- Cookies httpOnly pour JWT
- CSRF middleware pour requêtes mutables
- Validation stricte Pydantic v2
- SQLAlchemy ORM (protection SQL injection)
- Sanitization des champs utilisateur
- CORS strict configurable
- Rate limiting global par IP
- Rate limiting Redis-ready (`REDIS_URL`) avec fallback mémoire
- Logs structurés (`loguru`) + audit logs
- Aucune clé hardcodée, secrets uniquement via `.env`

## Rôles

### Admin
- CRUD IP
- CRUD Site/Subnet
- Scan réseau
- Import CSV
- Gestion utilisateurs

### Viewer
- Lecture (dashboard, sites, subnets, IPs)
- Export CSV

## Endpoints principaux

- Auth: `/api/v1/auth/register`, `/login`, `/refresh`, `/logout`, `/me`, `/first-login-setup`, `/change-password`
- Sites: `/api/v1/sites`
- Subnets: `/api/v1/subnets`
- IPs: `/api/v1/ips`, `/ips/suggest/{subnet_id}`, `/ips/import`, `/ips/export`
- Scan: `/api/v1/scan/{subnet_id}`
- Dashboard: `/api/v1/dashboard/stats`

## Tests

- `backend/tests/test_health.py`
- `backend/tests/test_scan_service.py`

## Notes production

- Activer HTTPS en frontal (obligatoire si `COOKIE_SECURE=true`)
- Restreindre `CORS_ORIGINS` aux domaines autorisés
- Utiliser le format strict d'origine: `https://domaine.tld` (pas de path, pas de slash final)
- Ne jamais utiliser les credentials par défaut en production
- Ajouter un scanner SAST/DAST dans le pipeline CI/CD

## Accès WAN + TLS (Let's Encrypt)

1. Configurer DNS: `A` record de ton domaine vers ton IP publique.
2. Ouvrir/NAT routeur: `80` et `443` vers la machine Docker.
3. Mettre dans `.env`:
  - `DOMAIN_NAME=ton-domaine.com`
  - `LETSENCRYPT_EMAIL=toi@ton-domaine.com`
  - `FRONTEND_URL=https://ton-domaine.com`
  - `CORS_ORIGINS=https://ton-domaine.com`
  - `COOKIE_SECURE=true`
4. Démarrer la stack: `docker compose up --build -d`.
5. Générer le certificat: `make tls-init`.
6. Redémarrer nginx pour activer HTTPS: `docker compose restart nginx`.

Renouvellement:
- Service `certbot` présent dans `docker-compose.yml` (boucle de renouvellement automatique).
- Vérification manuelle possible: `make tls-renew`.
