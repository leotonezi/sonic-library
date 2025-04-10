# Etapa de build
FROM node:20-slim AS builder

# Variável de ambiente para build (precisa ser passada no docker-compose)
ARG NEXT_PUBLIC_BACKEND_URL
ENV NEXT_PUBLIC_BACKEND_URL=$NEXT_PUBLIC_BACKEND_URL

WORKDIR /app

# 1. Instala dependências base (cache de node_modules)
COPY package.json package-lock.json ./
RUN npm install

# 2. Copia o restante do código
COPY . .

# 3. Instala novamente para baixar dependências nativas do Next.js e Tailwind (como lightningcss)
RUN npm install --force

# 4. Executa o build
RUN npm run build

# Etapa de produção
FROM node:20-slim

WORKDIR /app

COPY --from=builder /app ./

EXPOSE 3000

CMD ["npm", "start"]