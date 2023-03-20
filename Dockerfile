FROM caddy:builder AS builder
RUN xcaddy build \
    --with github.com/caddyserver/replace-response \
    --with github.com/greenpau/caddy-security
    FROM caddy:latest
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
VOLUME [ "/etc/caddy/" ]
