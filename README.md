# Caddy V2 with https://github.com/greenpau/caddy-auth-jwt installed for my server

Build Process:
docker images
docker build -t 192.168.1.3:5000/caddy-custom:latest .
docker login 192.168.1.3:5000
docker push 192.168.1.3:5000/caddy-custom:latest
