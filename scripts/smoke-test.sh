#!/bin/sh
set -eu
image=${1:?Pass the image to verify}
expected=$(sed -n 's/^ARG CADDY_VERSION=//p' Dockerfile | head -n 1)
version=$(docker run --rm "$image" caddy version)
case "$version" in
  "v$expected "*) ;;
  *) printf 'Unexpected Caddy version: %s\n' "$version" >&2; exit 1 ;;
esac
modules=$(docker run --rm "$image" caddy list-modules)
for module in http.handlers.replace_response http.authentication.providers.authorizer http.handlers.authenticator dns.providers.cloudflare; do
  printf '%s\n' "$modules" | grep -Fx "$module" >/dev/null
done
printf 'Verified Caddy %s and required modules.\n' "$expected"
