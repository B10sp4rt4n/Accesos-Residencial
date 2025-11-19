"""
AX-S - API REST Multitenant
FastAPI Application - Sistema de Control de Accesos Residencial
Arquitectura AUP-EXO: Multi-tenant MSP-Ready
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time

from app.database.connection import init_db
from app.routers import msp_router, condominio_router


# ========================================
# LIFECYCLE EVENTS
# ========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eventos de inicio y cierre de la aplicación"""
    # Startup
    print("\n" + "="*60)
    print("🚀 Iniciando AX-S API - Multi-tenant")
    print("="*60)
    
    # Inicializar base de datos
    try:
        init_db()
        print("✅ Base de datos inicializada")
    except Exception as e:
        print(f"⚠️  Error inicializando DB: {e}")
    
    print("✅ API lista para recibir requests")
    print("📖 Documentación: http://localhost:8000/docs")
    print("="*60 + "\n")
    
    yield
    
    # Shutdown
    print("\n" + "="*60)
    print("🛑 Cerrando AX-S API")
    print("="*60 + "\n")


# ========================================
# FASTAPI APP
# ========================================

app = FastAPI(
    title="AX-S Multi-tenant API",
    description="""
    ## 🏢 Sistema de Control de Accesos Residencial
    
    **Arquitectura AUP-EXO Multi-tenant MSP-Ready**
    
    ### Jerarquía:
    - **DS** (Dominio Superior): Super Admin
    - **DD** (Dominio Delegado): MSP (Managed Service Provider)
    - **SE** (Subdominio Específico): Condominio
    - **NO** (Nodo Operativo): Admin Local
    
    ### Características:
    - ✅ Multi-tenant por diseño
    - ✅ Identificadores exógenos (msp_id, condominio_id)
    - ✅ Relaciones basadas en IDs de negocio
    - ✅ Auditoría completa (ledger_exo)
    - ✅ Escalable a miles de condominios
    
    ### Endpoints Disponibles:
    - **MSP**: Gestión de proveedores de servicio
    - **Condominios**: Gestión de condominios bajo MSP
    - *(Próximamente: Residencias, Visitantes, Accesos)*
    """,
    version="1.0.0",
    contact={
        "name": "AX-S Development Team",
        "email": "dev@axs.com"
    },
    license_info={
        "name": "Proprietary"
    },
    lifespan=lifespan
)


# ========================================
# MIDDLEWARE
# ========================================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configurar según necesidades de producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Agregar tiempo de procesamiento en headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# ========================================
# EXCEPTION HANDLERS
# ========================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Manejo global de excepciones"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "error": str(exc),
            "path": str(request.url)
        }
    )


# ========================================
# ROUTERS
# ========================================

app.include_router(msp_router.router)
app.include_router(condominio_router.router)


# ========================================
# ROOT ENDPOINTS
# ========================================

@app.get(
    "/",
    tags=["Root"],
    summary="API Status"
)
def root():
    """Endpoint raíz - Status de la API"""
    return {
        "status": "online",
        "service": "AX-S Multi-tenant API",
        "version": "1.0.0",
        "architecture": "AUP-EXO",
        "documentation": "/docs",
        "endpoints": {
            "msp": "/msp",
            "condominios": "/condominio"
        }
    }


@app.get(
    "/health",
    tags=["Root"],
    summary="Health Check"
)
def health_check():
    """Health check para monitoreo"""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


@app.get(
    "/info",
    tags=["Root"],
    summary="API Information"
)
def api_info():
    """Información detallada de la API"""
    return {
        "name": "AX-S Multi-tenant API",
        "version": "1.0.0",
        "architecture": {
            "type": "AUP-EXO",
            "description": "Multi-tenant MSP-Ready",
            "hierarchy": [
                {"level": 1, "name": "DS", "description": "Dominio Superior - Super Admin"},
                {"level": 2, "name": "DD", "description": "Dominio Delegado - MSP"},
                {"level": 3, "name": "SE", "description": "Subdominio Específico - Condominio"},
                {"level": 4, "name": "NO", "description": "Nodo Operativo - Admin Local"}
            ]
        },
        "database": {
            "type": "PostgreSQL",
            "schema": "schema_exo.sql",
            "tables": 11,
            "models": "SQLAlchemy ORM"
        },
        "features": [
            "Multi-tenant por diseño",
            "Identificadores exógenos",
            "Auditoría completa",
            "Escalabilidad horizontal",
            "API RESTful",
            "Documentación OpenAPI/Swagger"
        ]
    }


# ========================================
# STARTUP MESSAGE
# ========================================

if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║           AX-S Multi-tenant API - AUP-EXO                  ║
    ╚════════════════════════════════════════════════════════════╝
    
    📖 Ejecutar:
        uvicorn app.main:app --reload
        
    🌐 URLs:
        - API: http://localhost:8000
        - Docs: http://localhost:8000/docs
        - ReDoc: http://localhost:8000/redoc
    
    🔧 Configuración:
        - DATABASE_URL en .env o variables de entorno
        - Ver app/database/connection.py para detalles
    """)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
