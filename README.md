# Caddy V2 with https://github.com/greenpau/caddy-auth-jwt installed for my server


Build Process: 
docker images
docker build -t caddy-custom .
docker login 192.168.1.3:5000
docker tag caddy-custom:latest 192.168.1.3:5000/caddy-custom
docker tag caddy-custom:latest 192.168.1.3:5000/caddy-custom:latest
docker push 192.168.1.3:5000/caddy-custom
