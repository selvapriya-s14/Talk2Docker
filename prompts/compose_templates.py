"""
Production-ready Docker Compose templates for multi-service stacks.
Pairs with Dockerfile templates for complete application setup.
"""

def get_flask_postgres_compose() -> str:
    """Flask + PostgreSQL with proper networking and volumes"""
    return """version: '3.8'

services:
  app:
    build: .
    container_name: flask_app
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://appuser:apppass@postgres:5432/appdb
      - FLASK_ENV=production
    depends_on:
      - postgres
    volumes:
      - ./logs:/app/logs
    networks:
      - app_network

  postgres:
    image: postgres:15-alpine
    container_name: postgres_db
    environment:
      - POSTGRES_USER=appuser
      - POSTGRES_PASSWORD=apppass
      - POSTGRES_DB=appdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:

networks:
  app_network:
    driver: bridge
"""

def get_fastapi_redis_compose() -> str:
    """FastAPI + Redis for caching"""
    return """version: '3.8'

services:
  app:
    build: .
    container_name: fastapi_app
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    volumes:
      - ./logs:/app/logs
    networks:
      - app_network

  redis:
    image: redis:7-alpine
    container_name: redis_cache
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - app_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  redis_data:

networks:
  app_network:
    driver: bridge
"""

def get_fastapi_postgres_redis_compose() -> str:
    """FastAPI + PostgreSQL + Redis full stack"""
    return """version: '3.8'

services:
  app:
    build: .
    container_name: fastapi_app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://appuser:apppass@postgres:5432/appdb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs:/app/logs
    networks:
      - app_network

  postgres:
    image: postgres:15-alpine
    container_name: postgres_db
    environment:
      - POSTGRES_USER=appuser
      - POSTGRES_PASSWORD=apppass
      - POSTGRES_DB=appdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: redis_cache
    volumes:
      - redis_data:/data
    networks:
      - app_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:

networks:
  app_network:
    driver: bridge
"""

def get_django_postgres_compose() -> str:
    """Django + PostgreSQL with migrations"""
    return """version: '3.8'

services:
  app:
    build: .
    container_name: django_app
    command: >
      sh -c "python manage.py migrate &&
             gunicorn myproject.wsgi:application --bind 0.0.0.0:8000"
    ports:
      - "8000:8000"
    environment:
      - DB_ENGINE=django.db.backends.postgresql
      - DB_NAME=djangodb
      - DB_USER=djangouser
      - DB_PASSWORD=djangopass
      - DB_HOST=postgres
      - DB_PORT=5432
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
      - static_volume:/app/staticfiles
    networks:
      - app_network

  postgres:
    image: postgres:15-alpine
    container_name: postgres_db
    environment:
      - POSTGRES_USER=djangouser
      - POSTGRES_PASSWORD=djangopass
      - POSTGRES_DB=djangodb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U djangouser"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  static_volume:

networks:
  app_network:
    driver: bridge
"""

def get_express_mongodb_compose() -> str:
    """Express + MongoDB for document-based apps"""
    return """version: '3.8'

services:
  app:
    build: .
    container_name: express_app
    ports:
      - "3000:3000"
    environment:
      - MONGODB_URI=mongodb://mongo:27017/appdb
      - NODE_ENV=production
    depends_on:
      - mongo
    volumes:
      - ./logs:/app/logs
    networks:
      - app_network

  mongo:
    image: mongo:7-alpine
    container_name: mongodb
    ports:
      - "27017:27017"
    environment:
      - MONGO_INITDB_ROOT_USERNAME=root
      - MONGO_INITDB_ROOT_PASSWORD=rootpass
    volumes:
      - mongo_data:/data/db
    networks:
      - app_network
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  mongo_data:

networks:
  app_network:
    driver: bridge
"""

# Compose template registry
COMPOSE_TEMPLATES = {
    "flask postgres": ("Flask + PostgreSQL", get_flask_postgres_compose),
    "flask postgresql": ("Flask + PostgreSQL", get_flask_postgres_compose),
    "fastapi redis": ("FastAPI + Redis", get_fastapi_redis_compose),
    "fastapi postgres": ("FastAPI + PostgreSQL + Redis", get_fastapi_postgres_redis_compose),
    "fastapi postgresql": ("FastAPI + PostgreSQL + Redis", get_fastapi_postgres_redis_compose),
    "django postgres": ("Django + PostgreSQL", get_django_postgres_compose),
    "django postgresql": ("Django + PostgreSQL", get_django_postgres_compose),
    "express mongodb": ("Express + MongoDB", get_express_mongodb_compose),
}

def detect_compose_template(user_input: str) -> tuple[str, callable] | None:
    """Detect if input matches a compose template combination"""
    user_lower = user_input.lower()
    user_words = set(user_lower.replace("+", " ").replace("and", " ").replace("with", " ").split())
    
    matches = []
    for key, (label, func) in COMPOSE_TEMPLATES.items():
        key_words = set(key.split())
        label_lower_words = set(label.lower().replace("+", " ").split())
        
        if key_words.issubset(user_words) or label_lower_words.issubset(user_words):
            matches.append((len(key), key, func))
    
    if not matches:
        return None
    
    matches.sort(reverse=True)
    _, best_key, best_func = matches[0]
    return (best_key, best_func)

def get_compose_template(key: str) -> str:
    """Get compose template by key"""
    if key not in COMPOSE_TEMPLATES:
        return None
    
    _, template_func = COMPOSE_TEMPLATES[key]
    return template_func()
