.PHONY: up down logs backend-lint backend-test frontend-lint tls-init tls-renew

ifneq (,$(wildcard .env))
include .env
export DOMAIN_NAME
export LETSENCRYPT_EMAIL
endif

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

backend-lint:
	docker compose run --rm backend sh -c "ruff check . && mypy app"

backend-test:
	docker compose run --rm backend pytest -q

frontend-lint:
	docker compose run --rm frontend sh -c "npm run lint"

tls-init:
	@test -n "$$DOMAIN_NAME" || (echo "DOMAIN_NAME is empty. Set it in .env" && exit 1)
	@test -n "$$LETSENCRYPT_EMAIL" || (echo "LETSENCRYPT_EMAIL is empty. Set it in .env" && exit 1)
	docker compose run --rm --entrypoint certbot certbot certonly --webroot -w /var/www/certbot -d $$DOMAIN_NAME --email $$LETSENCRYPT_EMAIL --agree-tos --no-eff-email

tls-renew:
	docker compose run --rm --entrypoint certbot certbot renew --webroot -w /var/www/certbot
