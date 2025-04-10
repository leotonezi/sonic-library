FROM node:20-slim AS builder

WORKDIR /app

# Set the backend URL if needed
ARG NEXT_PUBLIC_BACKEND_URL
ENV NEXT_PUBLIC_BACKEND_URL=$NEXT_PUBLIC_BACKEND_URL

# Copy only deps first
COPY package.json package-lock.json ./

# Install deps (will also run postinstall)
RUN npm install

# Copy rest of project
COPY . .

# Patch swc and lightningcss deps again
RUN npm install --force

# Now that all deps and native binaries are available
RUN npm run build

# Production
FROM node:20-slim
WORKDIR /app
COPY --from=builder /app ./
EXPOSE 3000
CMD ["npm", "start"]