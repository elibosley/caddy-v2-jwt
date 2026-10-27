ARG CADDY_VERSION=2.11.7
FROM --platform=$BUILDPLATFORM caddy:${CADDY_VERSION}-builder AS builder
ARG CADDY_VERSION
ARG TARGETOS
ARG TARGETARCH
RUN GOOS=${TARGETOS} GOARCH=${TARGETARCH} xcaddy build v${CADDY_VERSION} \
    --with github.com/caddyserver/replace-response@v0.0.0-20250618171559-80962887e4c6 \
    --with github.com/greenpau/caddy-security@v1.5.0 \
    --with github.com/caddy-dns/cloudflare@v0.2.4

FROM caddy:${CADDY_VERSION}
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
