# Etapa de build
FROM node:20-slim AS builder

# Variável de ambiente para build (precisa ser passada no docker-compose)
ARG NEXT_PUBLIC_BACKEND_URL
ENV NEXT_PUBLIC_BACKEND_URL=$NEXT_PUBLIC_BACKEND_URL

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

# Garante que as variáveis de ambiente públicas estejam disponíveis em tempo de build
RUN npm run build

# Etapa de produção
FROM node:20-slim

WORKDIR /app

COPY --from=builder /app ./

EXPOSE 3000

CMD ["npm", "start"]