"""
Gestor de conexión de base de datos.
Usa PostgreSQL en producción (Streamlit Cloud) y SQLite en desarrollo local.
"""
import os
import sqlite3
import streamlit as st

def get_db_connection():
    """
    Retorna una conexión a la base de datos.
    - PostgreSQL si DATABASE_URL está en secrets (producción)
    - SQLite si no hay DATABASE_URL (desarrollo local)
    """
    # Intentar obtener DATABASE_URL de secrets
    try:
        if hasattr(st, 'secrets') and 'DATABASE_URL' in st.secrets:
            # Producción: PostgreSQL
            import psycopg2
            return psycopg2.connect(st.secrets['DATABASE_URL'])
    except Exception as e:
        pass
    
    # Desarrollo: SQLite
    return sqlite3.connect('axs_v2.db', check_same_thread=False)

def execute_query(query, params=None, fetch=True):
    """
    Ejecuta query de forma compatible con SQLite y PostgreSQL.
    
    Args:
        query: SQL query (usar %s para params en ambos)
        params: Tupla de parámetros
        fetch: Si True, retorna resultados. Si False, solo commit.
    
    Returns:
        Lista de tuplas si fetch=True, None si fetch=False
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Convertir ? a %s si es PostgreSQL
    if 'postgresql' in str(type(conn)):
        query = query.replace('?', '%s')
    
    try:
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        
        if fetch:
            results = cur.fetchall()
            conn.close()
            return results
        else:
            conn.commit()
            conn.close()
            return None
    except Exception as e:
        conn.close()
        raise e

def get_db_type():
    """Retorna 'postgresql' o 'sqlite' según la BD activa."""
    try:
        if hasattr(st, 'secrets') and 'DATABASE_URL' in st.secrets:
            return 'postgresql'
    except:
        pass
    return 'sqlite'
