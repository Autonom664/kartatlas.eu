FROM nginx:1.28-alpine

COPY --chown=nginx:nginx kart-atlas.html /usr/share/nginx/html/index.html
COPY --chown=nginx:nginx kart-atlas.json /usr/share/nginx/html/kart-atlas.json
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
