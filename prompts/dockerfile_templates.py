"""
Production-ready Dockerfile templates for common frameworks.
Instant generation (0.5s) vs LLM generation (45s).
"""

def get_flask_template(app_name: str = "app") -> str:
    return f"""FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl && \\
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY .dockerignore .
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5000/ || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "{app_name}:app"]
"""

def get_flask_redis_template(app_name: str = "app") -> str:
    """Flask with Redis caching integration"""
    return f"""FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (curl for health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl && \\
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY .dockerignore .
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# Health check (Flask endpoint)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5000/ || exit 1

# Run Flask with gunicorn
# Note: Requires environment variable REDIS_URL (e.g., redis://redis:6379)
# For local development with Docker Compose: redis service name is 'redis'
ENV REDIS_URL=redis://redis:6379/0

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "{app_name}:app"]
"""

def get_fastapi_template(app_name: str = "main") -> str:
    return f"""FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl && \\
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY .dockerignore .
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "{app_name}:app", "--host", "0.0.0.0", "--port", "8000"]
"""

def get_django_template(project_name: str = "myproject") -> str:
    return f"""FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl && \\
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY .dockerignore .
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/ || exit 1

CMD ["gunicorn", "{project_name}.wsgi:application", "--bind", "0.0.0.0:8000"]
"""

def get_node_express_template(app_name: str = "server") -> str:
    return f"""FROM node:20-alpine

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache curl

# Copy package files
COPY package*.json .
RUN npm ci --omit=dev

# Copy application
COPY .dockerignore .
COPY . .

# Create non-root user
RUN addgroup -S appuser && adduser -S appuser -G appuser && \\
    chown -R appuser:appuser /app
USER appuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["node", "{app_name}.js"]
"""

def get_node_nextjs_template() -> str:
    return """FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine

WORKDIR /app
RUN apk add --no-cache curl
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

RUN addgroup -S appuser && adduser -S appuser -G appuser && \\
    chown -R appuser:appuser /app
USER appuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["npm", "start"]
"""

def get_python_selenium_template() -> str:
    return """FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (includes Chromium for Selenium)
RUN apt-get update && apt-get install -y --no-install-recommends \\
    chromium-browser \\
    chromium-chromedriver \\
    curl && \\
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY .dockerignore .
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["python", "app.py"]
"""

def get_go_template(binary_name: str = "app") -> str:
    return f"""FROM golang:1.22-alpine AS builder

WORKDIR /src
RUN apk add --no-cache git

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/{binary_name} .

FROM alpine:3.20

RUN apk add --no-cache ca-certificates curl

COPY --from=builder /app/{binary_name} /app/{binary_name}

RUN addgroup -S appuser && adduser -S appuser -G appuser
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD wget --quiet --tries=1 --spider http://localhost:8080/health || exit 1

CMD ["/app/{binary_name}"]
"""

def get_java_spring_template() -> str:
    return """FROM eclipse-temurin:21-jdk-alpine AS builder

WORKDIR /build
COPY . .
RUN apk add --no-cache maven && \\
    ./mvnw clean package -DskipTests

FROM eclipse-temurin:21-jre-alpine

RUN apk add --no-cache curl

COPY --from=builder /build/target/*.jar /app/app.jar

RUN addgroup -S appuser && adduser -S appuser -G appuser && \\
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD wget --quiet --tries=1 --spider http://localhost:8080/actuator/health || exit 1

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
"""

def get_fastapi_redis_template(app_name: str = "main") -> str:
    """FastAPI with Redis caching integration"""
    return f"""FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl && \\
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY .dockerignore .
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Redis URL environment variable
# For Docker Compose: redis service name is 'redis'
ENV REDIS_URL=redis://redis:6379/0

CMD ["uvicorn", "{app_name}:app", "--host", "0.0.0.0", "--port", "8000"]
"""

def get_fastapi_postgres_template(app_name: str = "main") -> str:
    """FastAPI with PostgreSQL database"""
    return f"""FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl \\
    postgresql-client && \\
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY .dockerignore .
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# PostgreSQL connection string
# For Docker Compose: DATABASE_URL=postgresql://user:password@postgres:5432/dbname
ENV DATABASE_URL=postgresql://user:password@postgres:5432/appdb

CMD ["uvicorn", "{app_name}:app", "--host", "0.0.0.0", "--port", "8000"]
"""

def get_flask_postgres_template(app_name: str = "app") -> str:
    """Flask with PostgreSQL database"""
    return f"""FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl \\
    postgresql-client && \\
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY .dockerignore .
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5000/ || exit 1

# PostgreSQL connection string
# For Docker Compose: DATABASE_URL=postgresql://user:password@postgres:5432/dbname
ENV DATABASE_URL=postgresql://user:password@postgres:5432/appdb

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "{app_name}:app"]
"""

def get_flask_mysql_template(app_name: str = "app") -> str:
    """Flask with MySQL database"""
    return f"""FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl \\
    default-mysql-client && \\
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY .dockerignore .
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5000/ || exit 1

# MySQL connection string
# For Docker Compose: DATABASE_URL=mysql+pymysql://user:password@mysql:3306/dbname
ENV DATABASE_URL=mysql+pymysql://user:password@mysql:3306/appdb

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "{app_name}:app"]
"""

def get_django_postgres_template(project_name: str = "myproject") -> str:
    """Django with PostgreSQL database"""
    return f"""FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl \\
    postgresql-client && \\
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY .dockerignore .
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/ || exit 1

# PostgreSQL connection via environment variables
# For Docker Compose: Use DB_ENGINE=django.db.backends.postgresql, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
ENV DB_ENGINE=django.db.backends.postgresql \\
    DB_NAME=appdb \\
    DB_USER=user \\
    DB_PASSWORD=password \\
    DB_HOST=postgres \\
    DB_PORT=5432

CMD ["gunicorn", "{project_name}.wsgi:application", "--bind", "0.0.0.0:8000"]
"""

def get_express_redis_template(app_name: str = "server") -> str:
    """Express with Redis caching"""
    return f"""FROM node:20-alpine

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache curl

# Copy package files
COPY package*.json .
RUN npm ci --omit=dev

# Copy application
COPY .dockerignore .
COPY . .

# Create non-root user
RUN addgroup -S appuser && adduser -S appuser -G appuser && \\
    chown -R appuser:appuser /app
USER appuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

# Redis URL environment variable
# For Docker Compose: redis service name is 'redis'
ENV REDIS_URL=redis://redis:6379

CMD ["node", "{app_name}.js"]
"""

def get_express_postgres_template(app_name: str = "server") -> str:
    """Express with PostgreSQL database"""
    return f"""FROM node:20-alpine

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache curl postgresql-client

# Copy package files
COPY package*.json .
RUN npm ci --omit=dev

# Copy application
COPY .dockerignore .
COPY . .

# Create non-root user
RUN addgroup -S appuser && adduser -S appuser -G appuser && \\
    chown -R appuser:appuser /app
USER appuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

# PostgreSQL connection string
# For Docker Compose: DATABASE_URL=postgresql://user:password@postgres:5432/dbname
ENV DATABASE_URL=postgresql://user:password@postgres:5432/appdb

CMD ["node", "{app_name}.js"]
"""

def get_express_mongodb_template(app_name: str = "server") -> str:
    """Express with MongoDB database"""
    return f"""FROM node:20-alpine

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache curl

# Copy package files
COPY package*.json .
RUN npm ci --omit=dev

# Copy application
COPY .dockerignore .
COPY . .

# Create non-root user
RUN addgroup -S appuser && adduser -S appuser -G appuser && \\
    chown -R appuser:appuser /app
USER appuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

# MongoDB connection string
# For Docker Compose: MONGODB_URI=mongodb://mongo:27017/appdb
ENV MONGODB_URI=mongodb://mongo:27017/appdb

CMD ["node", "{app_name}.js"]
"""

# Template registry
TEMPLATES = {
    "flask": ("Flask Web App", get_flask_template),
    "flask redis": ("Flask + Redis", get_flask_redis_template),
    "flask postgres": ("Flask + PostgreSQL", get_flask_postgres_template),
    "flask postgresql": ("Flask + PostgreSQL", get_flask_postgres_template),
    "flask mysql": ("Flask + MySQL", get_flask_mysql_template),
    "fastapi": ("FastAPI App", get_fastapi_template),
    "fastapi redis": ("FastAPI + Redis", get_fastapi_redis_template),
    "fastapi postgres": ("FastAPI + PostgreSQL", get_fastapi_postgres_template),
    "fastapi postgresql": ("FastAPI + PostgreSQL", get_fastapi_postgres_template),
    "django": ("Django App", get_django_template),
    "django postgres": ("Django + PostgreSQL", get_django_postgres_template),
    "django postgresql": ("Django + PostgreSQL", get_django_postgres_template),
    "express": ("Node Express App", get_node_express_template),
    "express redis": ("Express + Redis", get_express_redis_template),
    "express postgres": ("Express + PostgreSQL", get_express_postgres_template),
    "express postgresql": ("Express + PostgreSQL", get_express_postgres_template),
    "express mongodb": ("Express + MongoDB", get_express_mongodb_template),
    "nextjs": ("Next.js App", get_node_nextjs_template),
    "selenium": ("Python Selenium", get_python_selenium_template),
    "go": ("Go Microservice", get_go_template),
    "spring": ("Spring Boot App", get_java_spring_template),
}

def detect_template(user_input: str) -> tuple[str, callable] | None:
    """
    Detect if input matches a template framework.
    Returns (template_key, template_function) or None.
    
    Smart matching:
    - "Flask with PostgreSQL" matches "flask postgres" (all words present)
    - "fastapi and redis" matches "fastapi redis" (all words present)
    - Prioritizes longer matches (more specific combinations)
    """
    user_lower = user_input.lower()
    user_words = set(user_lower.replace("+", " ").replace("and", " ").replace("with", " ").split())
    
    # Find matching keys where all words in the key are in the input
    matches = []
    for key, (label, func) in TEMPLATES.items():
        key_words = set(key.split())
        label_lower_words = set(label.lower().replace("+", " ").replace("and", " ").split())
        
        # Check if all words in key are present in user input
        if key_words.issubset(user_words) or label_lower_words.issubset(user_words):
            matches.append((len(key), key, func))
    
    if not matches:
        return None
    
    # Sort by key length (descending) to prefer specific combinations
    # e.g., "flask postgres" (14 chars) before "flask" (5 chars)
    matches.sort(reverse=True)
    
    _, best_key, best_func = matches[0]
    return (best_key, best_func)

def get_template(key: str, **kwargs) -> str:
    """Get template by key, with optional kwargs for customization"""
    if key not in TEMPLATES:
        return None
    
    _, template_func = TEMPLATES[key]
    return template_func(**kwargs)
