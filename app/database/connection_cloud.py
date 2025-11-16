"""
Conexión a base de datos con soporte PostgreSQL para producción
y SQLite para desarrollo local.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_database_url():
    """
    Obtiene la URL de la base de datos según el entorno.
    
    Prioridad:
    1. DATABASE_URL (env var) - PostgreSQL en producción
    2. SQLite local (desarrollo)
    """
    db_url = os.getenv('DATABASE_URL')
    
    if db_url:
        # Streamlit Cloud puede dar postgres:// en vez de postgresql://
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        return db_url
    
    # SQLite por defecto (desarrollo)
    return 'sqlite:///axs_v2.db'

# Engine global
DATABASE_URL = get_database_url()
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith('sqlite') else {},
    pool_pre_ping=True,  # Verificar conexión antes de usar
    pool_size=5,
    max_overflow=10
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Genera una sesión de base de datos.
    
    Uso:
        with get_db() as db:
            # operaciones
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Para uso directo sin context manager
def get_connection():
    """
    Retorna conexión directa (compatible con código existente).
    """
    if DATABASE_URL.startswith('sqlite'):
        import sqlite3
        return sqlite3.connect('axs_v2.db')
    else:
        import psycopg2
        return psycopg2.connect(DATABASE_URL)
