FROM caddy:2.3.0-builder AS builder
RUN xcaddy build \
    --with github.com/greenpau/caddy-auth-jwt \
    --with github.com/greenpau/caddy-trace

FROM caddy:2.3.0
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
VOLUME [ "/etc/caddy/" ]
