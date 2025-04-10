# Etapa de build
FROM node:20-slim AS builder

ARG NEXT_PUBLIC_BACKEND_URL
ENV NEXT_PUBLIC_BACKEND_URL=$NEXT_PUBLIC_BACKEND_URL

WORKDIR /app

COPY package.json package-lock.json ./

# 👇 This will run postinstall and patch swc/lightningcss deps
RUN npm install

COPY . .

# 👇 Run build — now lightningcss should be ready
RUN npm run build

# Etapa de produção
FROM node:20-slim

WORKDIR /app
COPY --from=builder /app ./
EXPOSE 3000

CMD ["npm", "start"]