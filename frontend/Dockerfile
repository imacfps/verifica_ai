FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# Vite embute variáveis VITE_* no bundle em build-time (client-side, portanto
# precisa ser uma URL alcançável pelo navegador do usuário, não pelo container).
ARG VITE_API_URL=http://localhost:8000/v1
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM nginx:1.27-alpine AS runtime
RUN adduser -D -H -u 1001 webapp
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN chown -R webapp:webapp /usr/share/nginx/html /var/cache/nginx /var/run /var/log/nginx \
    && touch /var/run/nginx.pid \
    && chown webapp:webapp /var/run/nginx.pid
USER webapp
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
