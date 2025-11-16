"""
database/pg_connection.py
=========================
Módulo de conexión nativa a PostgreSQL (Supabase/directo)
Sin ORM, usando psycopg2 + RealDictCursor para resultados dict
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from contextlib import contextmanager

# Cargar variables de entorno
load_dotenv()

def get_pg_config():
    """
    Obtiene configuración de PostgreSQL desde variables de entorno.
    
    Returns:
        dict: Diccionario con parámetros de conexión
    """
    return {
        'host': os.getenv('PG_HOST', 'localhost'),
        'database': os.getenv('PG_DATABASE', 'postgres'),
        'user': os.getenv('PG_USER', 'postgres'),
        'password': os.getenv('PG_PASSWORD', ''),
        'port': int(os.getenv('PG_PORT', 5432))
    }

def get_pg():
    """
    Crea una conexión directa a PostgreSQL.
    
    Returns:
        psycopg2.connection: Conexión activa a PostgreSQL
        
    Raises:
        psycopg2.Error: Si no se puede conectar
        
    Example:
        >>> conn = get_pg()
        >>> cursor = conn.cursor()
        >>> cursor.execute("SELECT * FROM eventos LIMIT 10")
        >>> rows = cursor.fetchall()
        >>> conn.close()
    """
    config = get_pg_config()
    return psycopg2.connect(**config)

@contextmanager
def get_pg_context():
    """
    Context manager para conexión PostgreSQL con auto-close.
    
    Yields:
        psycopg2.connection: Conexión activa
        
    Example:
        >>> with get_pg_context() as conn:
        ...     cursor = conn.cursor()
        ...     cursor.execute("SELECT COUNT(*) FROM eventos")
        ...     count = cursor.fetchone()[0]
    """
    conn = get_pg()
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def get_pg_cursor(dict_cursor=True):
    """
    Context manager para cursor PostgreSQL con auto-commit/close.
    
    Args:
        dict_cursor (bool): Si True, usa RealDictCursor (resultados como dict)
                           Si False, usa cursor normal (resultados como tuplas)
    
    Yields:
        psycopg2.cursor: Cursor activo
        
    Example:
        >>> with get_pg_cursor() as cur:
        ...     cur.execute("SELECT id, nombre FROM residentes WHERE id = %s", (100,))
        ...     residente = cur.fetchone()
        ...     print(residente['nombre'])  # dict access
    """
    conn = get_pg()
    cursor = conn.cursor(cursor_factory=RealDictCursor) if dict_cursor else conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def execute_query(query, params=None, fetch_one=False, fetch_all=True):
    """
    Ejecuta una query SELECT y retorna resultados como dict.
    
    Args:
        query (str): Query SQL (usar %s para parámetros)
        params (tuple): Parámetros para la query
        fetch_one (bool): Si True, retorna solo un registro (dict)
        fetch_all (bool): Si True, retorna todos los registros (list[dict])
    
    Returns:
        dict | list[dict] | None: Resultados de la query
        
    Example:
        >>> evento = execute_query(
        ...     "SELECT * FROM eventos WHERE id = %s",
        ...     (123,),
        ...     fetch_one=True
        ... )
        >>> eventos = execute_query(
        ...     "SELECT * FROM eventos WHERE tipo = %s ORDER BY timestamp DESC LIMIT 10",
        ...     ('ingreso',)
        ... )
    """
    with get_pg_cursor() as cur:
        cur.execute(query, params)
        
        if fetch_one:
            return cur.fetchone()
        elif fetch_all:
            return cur.fetchall()
        else:
            return None

def execute_insert(query, params=None, return_id=True):
    """
    Ejecuta INSERT y retorna el ID del registro creado.
    
    Args:
        query (str): Query INSERT (usar %s para parámetros)
        params (tuple): Parámetros para la query
        return_id (bool): Si True, retorna el ID generado (SERIAL)
    
    Returns:
        int | None: ID del registro insertado
        
    Example:
        >>> evento_id = execute_insert(
        ...     "INSERT INTO eventos (tipo, rol, detalle) VALUES (%s, %s, %s) RETURNING id",
        ...     ('ingreso', 'vigilante', 'Acceso concedido')
        ... )
    """
    with get_pg_cursor(dict_cursor=False) as cur:
        cur.execute(query, params)
        
        if return_id:
            # PostgreSQL retorna ID con RETURNING id
            if 'RETURNING' in query.upper():
                result = cur.fetchone()
                return result[0] if result else None
            else:
                # Alternativa: usar lastrowid (no recomendado)
                return cur.lastrowid
        return None

def execute_update(query, params=None):
    """
    Ejecuta UPDATE/DELETE y retorna cantidad de filas afectadas.
    
    Args:
        query (str): Query UPDATE/DELETE (usar %s para parámetros)
        params (tuple): Parámetros para la query
    
    Returns:
        int: Cantidad de filas afectadas
        
    Example:
        >>> rows_updated = execute_update(
        ...     "UPDATE entidades SET score = score + %s WHERE id = %s",
        ...     (10, 100)
        ... )
    """
    with get_pg_cursor(dict_cursor=False) as cur:
        cur.execute(query, params)
        return cur.rowcount

def init_pg_schema():
    """
    Inicializa el schema de PostgreSQL ejecutando database/schema.sql.
    
    Returns:
        bool: True si se ejecutó correctamente
        
    Raises:
        FileNotFoundError: Si no existe schema.sql
        psycopg2.Error: Si hay errores en el SQL
    """
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"No se encontró {schema_path}")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    with get_pg_cursor(dict_cursor=False) as cur:
        cur.execute(schema_sql)
    
    print("✅ Schema PostgreSQL inicializado correctamente")
    return True

def test_connection():
    """
    Prueba la conexión a PostgreSQL y retorna info de la BD.
    
    Returns:
        dict: Información de la conexión
    """
    try:
        with get_pg_cursor() as cur:
            cur.execute("SELECT version()")
            version = cur.fetchone()['version']
            
            cur.execute("SELECT current_database()")
            database = cur.fetchone()['current_database']
            
            cur.execute("SELECT current_user")
            user = cur.fetchone()['current_user']
            
            return {
                'status': 'connected',
                'version': version,
                'database': database,
                'user': user
            }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

if __name__ == '__main__':
    # Test de conexión
    print("🔍 Probando conexión PostgreSQL...")
    result = test_connection()
    
    if result['status'] == 'connected':
        print(f"✅ Conectado a: {result['database']}")
        print(f"👤 Usuario: {result['user']}")
        print(f"📦 Versión: {result['version']}")
    else:
        print(f"❌ Error: {result['error']}")
