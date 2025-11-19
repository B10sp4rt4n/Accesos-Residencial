"""
Database connection manager para FastAPI
Configuración de SQLAlchemy engine y sessions
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import toml

# Importar Base de los modelos existentes
from core.db_exo import Base

# Función para obtener DATABASE_URL
def get_database_url():
    """Obtiene DATABASE_URL desde .streamlit/secrets.toml o variables de entorno"""
    
    # Intentar cargar desde .streamlit/secrets.toml primero
    secrets_path = ".streamlit/secrets.toml"
    if os.path.exists(secrets_path):
        try:
            secrets = toml.load(secrets_path)
            if "DATABASE_URL" in secrets:
                return secrets["DATABASE_URL"]
        except:
            pass
    
    # Fallback a variable de entorno
    return os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/axs_exo"
    )

# Configuración de PostgreSQL
DATABASE_URL = get_database_url()

# Crear engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # True para debug SQL
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    pool_size=5,
    max_overflow=10
)

# Crear SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Inicializar base de datos (crear tablas si no existen)"""
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas inicializadas en PostgreSQL")


def get_db():
    """
    Dependency para FastAPI
    Proporciona una sesión de base de datos y la cierra automáticamente
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Context manager para uso fuera de FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
