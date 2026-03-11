"""
Generate .env.example files based on Docker templates and compose files.
Helps users set up their environment with proper configuration.
"""

def generate_env_file(framework: str, template_type: str = "compose") -> str:
    """
    Generate a .env.example file for a given framework.
    Includes all necessary environment variables with explanations.
    """
    
    # Base environment variables
    base_env = """# Application Environment
APP_ENV=production
APP_DEBUG=false
LOG_LEVEL=info
"""
    
    # Framework-specific variables
    framework_lower = framework.lower()
    
    if "flask" in framework_lower:
        return base_env + """
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-here-min-32-chars
"""
    
    elif "fastapi" in framework_lower:
        return base_env + """
# FastAPI Configuration
API_TITLE=My API
API_VERSION=1.0.0
API_DESCRIPTION=My awesome API
"""
    
    elif "django" in framework_lower:
        return base_env + """
# Django Configuration
SECRET_KEY=your-django-secret-key-here
DEBUG=false
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
"""
    
    elif "express" in framework_lower or "node" in framework_lower:
        return base_env + """
# Node.js Configuration
NODE_ENV=production
PORT=3000
"""
    
    else:
        return base_env

def generate_database_env(db_type: str) -> str:
    """Generate database-specific environment variables"""
    
    if "postgres" in db_type.lower() or "postgresql" in db_type.lower():
        return """
# PostgreSQL Configuration
DB_ENGINE=django.db.backends.postgresql
# OR for SQLAlchemy:
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname
DB_HOST=postgres
DB_PORT=5432
DB_NAME=appdb
DB_USER=appuser
DB_PASSWORD=change_me_securely
"""
    
    elif "mysql" in db_type.lower():
        return """
# MySQL Configuration
DB_ENGINE=django.db.backends.mysql
# OR for SQLAlchemy:
# DATABASE_URL=mysql+pymysql://user:password@localhost:3306/dbname
DB_HOST=mysql
DB_PORT=3306
DB_NAME=appdb
DB_USER=appuser
DB_PASSWORD=change_me_securely
"""
    
    elif "mongodb" in db_type.lower() or "mongo" in db_type.lower():
        return """
# MongoDB Configuration
MONGODB_URI=mongodb://root:rootpass@mongo:27017/appdb
MONGODB_USER=root
MONGODB_PASSWORD=change_me_securely
"""
    
    elif "sqlite" in db_type.lower():
        return """
# SQLite Configuration
DATABASE_URL=sqlite:///./test.db
"""
    
    return ""

def generate_cache_env(cache_type: str) -> str:
    """Generate cache-specific environment variables"""
    
    if "redis" in cache_type.lower():
        return """
# Redis Configuration
REDIS_URL=redis://redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
CACHE_TTL=3600
"""
    
    elif "memcached" in cache_type.lower():
        return """
# Memcached Configuration
MEMCACHED_HOST=memcached
MEMCACHED_PORT=11211
CACHE_TTL=3600
"""
    
    return ""

def generate_complete_env(framework: str, database: str = None, cache: str = None) -> str:
    """Generate complete .env.example file with all relevant variables"""
    
    env = generate_env_file(framework)
    
    if database:
        env += "\n" + generate_database_env(database)
    
    if cache:
        env += "\n" + generate_cache_env(cache)
    
    # Add security notes
    env += """
# Security Notes:
# - Change all passwords to secure, random values
# - Never commit actual .env file (only .env.example)
# - Use strong SECRET_KEY (min 32 characters, random)
# - Rotate credentials regularly in production
# - Use environment variable management service in production

# Common Ports:
# Flask: 5000
# FastAPI: 8000  
# Django: 8000
# Express/Node: 3000
# PostgreSQL: 5432
# MySQL: 3306
# MongoDB: 27017
# Redis: 6379
"""
    
    return env

# Predefined stacks
ENV_TEMPLATES = {
    "flask postgres": lambda: generate_complete_env("Flask", "PostgreSQL"),
    "flask mysql": lambda: generate_complete_env("Flask", "MySQL"),
    "flask redis": lambda: generate_complete_env("Flask", cache="Redis"),
    "fastapi redis": lambda: generate_complete_env("FastAPI", cache="Redis"),
    "fastapi postgres redis": lambda: generate_complete_env("FastAPI", "PostgreSQL", "Redis"),
    "django postgres": lambda: generate_complete_env("Django", "PostgreSQL"),
    "express mongodb": lambda: generate_complete_env("Express", "MongoDB"),
}

def get_env_file(stack_name: str) -> str:
    """Get .env.example for a specific stack"""
    if stack_name in ENV_TEMPLATES:
        return ENV_TEMPLATES[stack_name]()
    return None
