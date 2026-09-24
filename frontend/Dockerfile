FROM node:24.15.0-alpine@sha256:d1b3b4da11eefd5941e7f0b9cf17783fc99d9c6fc34884a665f40a06dbdfc94f AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts
COPY . .
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.30.5-alpine@sha256:4714e0b1b2577eaa1a6131d07c958b67f0eb68e6d0521e90c6e5287db8cf0bc5 AS runtime
USER root
# Apply vendor security fixes released after the pinned base was built.
RUN apk upgrade --no-cache
COPY --chown=101:101 nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=builder --chown=101:101 /app/dist /usr/share/nginx/html
USER 101:101
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/ || exit 1
CMD ["nginx", "-g", "daemon off;"]
