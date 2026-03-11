"""
Production-ready Dockerfile examples for common frameworks
"""

EXAMPLES = {
    "python_flask": """
# Flask Web Application (Production)
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y curl \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5000/ || exit 1

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
""",

    "python_fastapi": """
# FastAPI Application (Production)
FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 appuser
USER appuser

HEALTHCHECK --interval=30s CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
""",

    "nodejs_express": """
# Node.js Express App (Multi-stage)
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json .
RUN npm ci

COPY . .
RUN npm run build 2>/dev/null || true

# Production image
FROM node:20-alpine

RUN apk add --no-cache curl

WORKDIR /app

# Copy node_modules from builder
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist 2>/dev/null || true
COPY package.json .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

HEALTHCHECK --interval=30s CMD curl -f http://localhost:3000 || exit 1

EXPOSE 3000
CMD ["node", "dist/server.js"]
""",

    "nodejs_nextjs": """
# Next.js Application (Multi-stage)
FROM node:20-alpine AS deps

WORKDIR /app
COPY package*.json .
RUN npm ci

FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner

WORKDIR /app

RUN apk add --no-cache curl

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY package.json .

RUN useradd -m -u 1000 appuser
USER appuser

HEALTHCHECK --interval=30s CMD curl -f http://localhost:3000 || exit 1

EXPOSE 3000
CMD ["npm", "start"]
""",

    "go_multistage": """
# Go Application (Multi-stage)
FROM golang:1.22-alpine AS builder

WORKDIR /src

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o /app/myapp .

# Final image
FROM alpine:3.20

RUN apk add --no-cache ca-certificates curl

COPY --from=builder /app/myapp /app/myapp

RUN useradd -m -u 1000 appuser
USER appuser

HEALTHCHECK --interval=30s CMD wget --quiet --tries=1 --spider http://localhost:8080/health || exit 1

EXPOSE 8080
CMD ["/app/myapp"]
""",

    "java_springboot": """
# Spring Boot Application (Maven Multi-stage)
FROM eclipse-temurin:21-jdk-alpine AS builder

WORKDIR /build

COPY . .

RUN apt-get update && apt-get install -y maven && \\
    ./mvnw clean package -DskipTests

# Production image
FROM eclipse-temurin:21-jre-alpine

RUN apk add --no-cache curl

COPY --from=builder /build/target/app.jar /app/app.jar

RUN useradd -m -u 1000 appuser
USER appuser

HEALTHCHECK --interval=30s CMD curl -f http://localhost:8080/actuator/health || exit 1

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
""",

    "rust_actix": """
# Rust Actix Web Application (Multi-stage)
FROM rust:latest as builder

WORKDIR /src

COPY . .

RUN cargo build --release

FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y ca-certificates curl && \\
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /src/target/release/myapp /app/myapp

RUN useradd -m -u 1000 appuser
USER appuser

HEALTHCHECK --interval=30s CMD curl -f http://localhost:8080/ || exit 1

EXPOSE 8080
CMD ["/app/myapp"]
""",

    "dotnet_aspnet": """
# ASP.NET Core Application (Multi-stage)
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS builder

WORKDIR /src

COPY . .

RUN dotnet publish -c Release -o /app

# Production image
FROM mcr.microsoft.com/dotnet/aspnet:8.0

WORKDIR /app

COPY --from=builder /app .

RUN useradd -m -u 1000 appuser
USER appuser

HEALTHCHECK --interval=30s CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080
ENTRYPOINT ["dotnet", "MyApp.dll"]
""",

    "php_laravel": """
# PHP Laravel Application (Multi-stage)
FROM php:8.3-fpm-alpine AS provider

RUN apk add --no-cache \\
    build-base \\
    curl \\
    git \\
    oniguruma-dev \\
    zip

RUN docker-php-ext-install bcmath ctype fileinfo json mbstring pdo pdo_mysql tokenizer

COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

WORKDIR /app

COPY . .

RUN composer install --no-interaction --optimize-autoloader

# Production image
FROM php:8.3-fpm-alpine

RUN apk add --no-cache curl nginx

RUN docker-php-ext-install bcmath ctype fileinfo json mbstring pdo pdo_mysql tokenizer

WORKDIR /app

COPY --from=provider /app .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["php-fpm"]
""",

    "ruby_rails": """
# Ruby on Rails Application (Multi-stage)
FROM ruby:3.3-alpine AS dependencies

RUN apk add --no-cache build-base curl postgresql-dev

WORKDIR /app

COPY Gemfile Gemfile.lock ./

RUN bundle install --jobs $(nproc)

# Production image
FROM ruby:3.3-alpine

RUN apk add --no-cache postgresql-client curl

WORKDIR /app

COPY --from=dependencies /usr/local/bundle /usr/local/bundle

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

HEALTHCHECK --interval=30s CMD curl -f http://localhost:3000 || exit 1

EXPOSE 3000
CMD ["bundle", "exec", "rails", "server", "-b", "0.0.0.0"]
""",
}

def get_example(framework: str) -> str:
    """Get Dockerfile example for a framework"""
    key = framework.lower().replace(" ", "_").replace(".net", "dotnet")
    return EXAMPLES.get(key, "No example found for that framework")

def list_examples() -> list:
    """List all available framework examples"""
    return list(EXAMPLES.keys())
