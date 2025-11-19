-- ========================================
-- FIX: Crear vista eventos para compatibilidad
-- ========================================
-- Este script crea una vista "eventos" que mapea ledger_exo
-- a la estructura esperada por los módulos legacy.
-- 
-- EJECUTAR EN: PostgreSQL (Base de datos externa)
-- CUÁNDO: Después de crear schema_exo.sql
-- POR QUÉ: El código legacy consulta tabla "eventos" que no existe
--          en schema_exo.sql (solo existe ledger_exo)
-- ========================================

-- Crear vista de compatibilidad
CREATE OR REPLACE VIEW eventos AS
SELECT 
    l.ledger_id AS evento_id,
    l.msp_id,
    l.condominio_id,
    l.entidad_id,
    l.accion AS tipo_evento,
    l.detalle AS metadata,
    NULL::VARCHAR(100) AS evidencia_id,
    ''::VARCHAR(100) AS hash_actual,
    l.timestamp AS timestamp_servidor,
    l.timestamp AS timestamp_cliente,
    l.usuario_id AS actor,
    l.ip_origen AS dispositivo,
    l.ip_origen AS origen,
    l.user_agent AS contexto,
    NULL::VARCHAR(200) AS recibo_recordia
FROM ledger_exo l;

-- Comentario explicativo
COMMENT ON VIEW eventos IS 'Vista de compatibilidad: mapea ledger_exo a estructura legacy de eventos';

-- Verificar que la vista se creó correctamente
SELECT 'Vista eventos creada correctamente' AS status;
SELECT COUNT(*) AS total_eventos FROM eventos;

-- ========================================
-- FIN DEL SCRIPT
-- ========================================
