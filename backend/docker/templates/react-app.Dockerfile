# Stage 1 — build
FROM node:20-alpine AS builder
WORKDIR /app
COPY site/package.json site/package-lock.json* ./
RUN npm ci --prefer-offline
COPY site/ .
RUN npm run build

# Stage 2 — serve
FROM nginx:1.25-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
RUN echo 'server { listen 80; location / { try_files $uri /index.html; } }' \
    > /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
