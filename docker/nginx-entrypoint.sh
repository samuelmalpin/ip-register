#!/bin/sh
set -e

DOMAIN="${DOMAIN_NAME}"
CERT_PATH="/etc/letsencrypt/live/${DOMAIN}/fullchain.pem"
KEY_PATH="/etc/letsencrypt/live/${DOMAIN}/privkey.pem"

if [ -n "$DOMAIN" ] && [ -f "$CERT_PATH" ] && [ -f "$KEY_PATH" ]; then
  envsubst '${DOMAIN_NAME}' < /etc/nginx/templates/nginx.tls.conf.template > /etc/nginx/conf.d/default.conf
  echo "TLS enabled for domain: $DOMAIN"
else
  envsubst '${DOMAIN_NAME}' < /etc/nginx/templates/nginx.http.conf.template > /etc/nginx/conf.d/default.conf
  echo "TLS certificate not found yet. Running HTTP mode."
fi

nginx -g 'daemon off;'
