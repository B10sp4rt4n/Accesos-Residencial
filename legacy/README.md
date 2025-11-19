# Carpeta Legacy

Esta carpeta contiene archivos obsoletos del sistema anterior.

## ⚠️ IMPORTANTE

**Estos archivos NO deben usarse en producción.**

Están preservados únicamente como referencia histórica durante la migración a arquitectura AUP-EXO.

## 📁 Archivos Migrados

| Archivo | Sustituido por | Fecha |
|---------|----------------|-------|
| `personas_old.py` | `modulos/entidades_ui.py` | 15-Nov-2025 |
| `vehiculos_old.py` | `modulos/entidades_ui.py` | 15-Nov-2025 |
| `dashboard_old.py` | Módulo en desarrollo | 15-Nov-2025 |
| `eventos_old.py` | Módulo en desarrollo | 15-Nov-2025 |
| `politicas_old.py` | Módulo en desarrollo | 15-Nov-2025 |
| `vigilancia_OLD.py` | `modulos/vigilancia.py` | 15-Nov-2025 |
| `entidades_OLD.py` | `modulos/entidades.py` | 15-Nov-2025 |
| `index_old.py` | `index.py` | 15-Nov-2025 |

## 🔄 Migración AUP-EXO

El sistema ha migrado de:

**ANTES:**
```
personas.py       → DB directa
vehiculos.py      → DB directa
visitas.py        → DB directa
proveedores.py    → DB directa
vigilante.py      → DB directa
```

**AHORA:**
```
modulos/entidades_ui.py   → ENTIDAD
modulos/vigilancia.py     → ORQUESTADOR → EVENTO
```

## 🗑️ Eliminación Futura

Estos archivos serán eliminados permanentemente en:
- **Fase D** (post testing completo)
- Después de 3 meses sin incidencias
- Una vez validada la estabilidad del sistema AUP-EXO

## 📋 Notas

Si necesitas consultar alguna función específica de los módulos antiguos, usa `git log` para ver el historial completo antes de la migración.

```bash
# Ver última versión funcional de personas.py
git show HEAD~10:personas.py

# Ver cambios en la migración
git diff main..feature/aup-exo-roadmap
```

---

**No modificar archivos de esta carpeta.**  
**Solo lectura para referencia histórica.**
