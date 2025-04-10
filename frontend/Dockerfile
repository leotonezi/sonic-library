# Etapa de build
FROM node:20-slim AS builder

ARG NEXT_PUBLIC_BACKEND_URL
ENV NEXT_PUBLIC_BACKEND_URL=$NEXT_PUBLIC_BACKEND_URL

WORKDIR /app

COPY package.json package-lock.json ./

# 👇 First install just base deps
RUN npm install

# 👇 Now copy the rest of the project
COPY . .

# 👇 Reinstall to run postinstall hook and patch lightningcss
RUN npm install --force

# 👇 Run build now that native binaries are available
RUN npm run build

# Etapa de produção
FROM node:20-slim
WORKDIR /app
COPY --from=builder /app ./
EXPOSE 3000
CMD ["npm", "start"]