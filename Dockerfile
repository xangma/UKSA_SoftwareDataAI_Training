FROM node:22-alpine AS builder

WORKDIR /build

COPY package.json package-lock.json ./
RUN apk add --no-cache python3
RUN npm ci

COPY . .

ENV BASE_URL=/jupyterbook
RUN npm run build:docs

FROM nginxinc/nginx-unprivileged:stable-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /build/_build/html /usr/share/nginx/html/jupyterbook

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
