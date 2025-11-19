# 🔐 Verificación de Autoría - AX-S

## 📋 Resumen

Este documento proporciona las instrucciones para verificar la autoría de las dos versiones del sistema AX-S mediante hashes SHA-256.

---

## 🎯 Versiones del Sistema

### 1. Multi-Tenant (v2.0.0-multitenant)
- **Branch**: `feature/multi-tenant-fixes`
- **Certificado**: `AUTHORSHIP_MULTITENANT.md`
- **Hash SHA-256**: `82f37e96f626993f5ffd698d8ff557293864c237d1abdf368dcf625e6de37b06`

### 2. Single-Tenant (v1.0.0-stable)
- **Branch**: `main`
- **Certificado**: `AUTHORSHIP_SINGLETENANT.md`
- **Hash SHA-256**: `56aff2c031a4825cba1b52542b59e0f846da73bf668e339b2aefb7255607c0e0`

---

## ✅ Verificación de Hashes

### Método 1: Verificación Directa

Para verificar el hash de la versión **Multi-Tenant**:

```bash
echo -n "AX-S v2.0.0-multitenant|B10sp4rt4n|2025-11-19|feature/multi-tenant-fixes|commits:dbb74e2,e3fc415,8c36395,e72f5a0,fa4336c" | sha256sum
```

**Resultado esperado**:
```
82f37e96f626993f5ffd698d8ff557293864c237d1abdf368dcf625e6de37b06
```

Para verificar el hash de la versión **Single-Tenant**:

```bash
echo -n "AX-S v1.0.0-stable|B10sp4rt4n|2025-11-19|main|SQLite+PostgreSQL|Streamlit" | sha256sum
```

**Resultado esperado**:
```
56aff2c031a4825cba1b52542b59e0f846da73bf668e339b2aefb7255607c0e0
```

---

### Método 2: Script de Verificación Python

Guarda este script como `verify_authorship.py`:

```python
#!/usr/bin/env python3
import hashlib

def verify_hash(content, expected_hash, version):
    """Verifica el hash SHA-256 de una versión"""
    calculated_hash = hashlib.sha256(content.encode()).hexdigest()
    
    print(f"\n{'='*70}")
    print(f"Verificando: {version}")
    print(f"{'='*70}")
    print(f"Hash Esperado:  {expected_hash}")
    print(f"Hash Calculado: {calculated_hash}")
    
    if calculated_hash == expected_hash:
        print("✅ VERIFICACIÓN EXITOSA - Hash coincide")
        return True
    else:
        print("❌ VERIFICACIÓN FALLIDA - Hash NO coincide")
        return False

# Multi-Tenant
mt_content = "AX-S v2.0.0-multitenant|B10sp4rt4n|2025-11-19|feature/multi-tenant-fixes|commits:dbb74e2,e3fc415,8c36395,e72f5a0,fa4336c"
mt_hash = "82f37e96f626993f5ffd698d8ff557293864c237d1abdf368dcf625e6de37b06"

# Single-Tenant
st_content = "AX-S v1.0.0-stable|B10sp4rt4n|2025-11-19|main|SQLite+PostgreSQL|Streamlit"
st_hash = "56aff2c031a4825cba1b52542b59e0f846da73bf668e339b2aefb7255607c0e0"

# Verificar ambas versiones
mt_valid = verify_hash(mt_content, mt_hash, "Multi-Tenant v2.0.0")
st_valid = verify_hash(st_content, st_hash, "Single-Tenant v1.0.0")

# Resultado final
print(f"\n{'='*70}")
print("RESULTADO FINAL")
print(f"{'='*70}")
print(f"Multi-Tenant: {'✅ VÁLIDO' if mt_valid else '❌ INVÁLIDO'}")
print(f"Single-Tenant: {'✅ VÁLIDO' if st_valid else '❌ INVÁLIDO'}")
print(f"{'='*70}\n")
```

Ejecuta el script:

```bash
python3 verify_authorship.py
```

**Salida esperada**:
```
======================================================================
Verificando: Multi-Tenant v2.0.0
======================================================================
Hash Esperado:  82f37e96f626993f5ffd698d8ff557293864c237d1abdf368dcf625e6de37b06
Hash Calculado: 82f37e96f626993f5ffd698d8ff557293864c237d1abdf368dcf625e6de37b06
✅ VERIFICACIÓN EXITOSA - Hash coincide

======================================================================
Verificando: Single-Tenant v1.0.0
======================================================================
Hash Esperado:  56aff2c031a4825cba1b52542b59e0f846da73bf668e339b2aefb7255607c0e0
Hash Calculado: 56aff2c031a4825cba1b52542b59e0f846da73bf668e339b2aefb7255607c0e0
✅ VERIFICACIÓN EXITOSA - Hash coincide

======================================================================
RESULTADO FINAL
======================================================================
Multi-Tenant: ✅ VÁLIDO
Single-Tenant: ✅ VÁLIDO
======================================================================
```

---

## 🔍 Verificación en el Repositorio Git

### Verificar Commits de Multi-Tenant

```bash
# Checkout a la branch multi-tenant
git checkout feature/multi-tenant-fixes

# Verificar commits específicos
git log --oneline | grep -E "(dbb74e2|e3fc415|8c36395|e72f5a0|fa4336c)"

# Ver detalles de un commit
git show dbb74e2
```

**Commits esperados**:
```
12d563d - docs: Agregar certificados de autoría con hash SHA-256
dbb74e2 - docs: Agregar documentación completa de implementación multi-tenant
e3fc415 - feat: Implementar filtrado por contexto en Gestión de Condominios
8c36395 - ✨ Confirmación visual del contexto en sidebar
e72f5a0 - ✨ Mostrar contexto activo en todos los módulos
fa4336c - fix: Resolver errores de JSON parsing y manejo de NULL
```

### Verificar Autor de los Commits

```bash
# Verificar que todos los commits son de B10sp4rt4n
git log --author="B10sp4rt4n" --oneline feature/multi-tenant-fixes | head -10
```

---

## 📊 Verificación de Archivos

### Multi-Tenant: Archivos Principales

```bash
# Verificar existencia de archivos clave
ls -la index.py
ls -la modulos/entidades.py
ls -la modulos/entidades_ui.py
ls -la modulos/vigilancia.py
ls -la core/db.py

# Verificar certificado de autoría
cat AUTHORSHIP_MULTITENANT.md | grep -A2 "Hash de Autoría"
```

### Single-Tenant: Estructura Base

```bash
# Verificar módulos core
ls -la modulos/*.py
ls -la core/*.py

# Verificar certificado de autoría
cat AUTHORSHIP_SINGLETENANT.md | grep -A2 "Hash de Autoría"
```

---

## 🎓 Verificación de Autoría en GitHub

### 1. Verificar Repositorio

- **URL**: https://github.com/B10sp4rt4n/Accesos-Residencial
- **Owner**: B10sp4rt4n
- **Branches**: `main`, `feature/multi-tenant-fixes`

### 2. Verificar Commits en GitHub

Navega a:
```
https://github.com/B10sp4rt4n/Accesos-Residencial/commits/feature/multi-tenant-fixes
```

Verifica que los commits listados coincidan con los del certificado.

### 3. Verificar Archivos en GitHub

```
https://github.com/B10sp4rt4n/Accesos-Residencial/blob/feature/multi-tenant-fixes/AUTHORSHIP_MULTITENANT.md
https://github.com/B10sp4rt4n/Accesos-Residencial/blob/main/AUTHORSHIP_SINGLETENANT.md
```

---

## 🔐 Firma Digital de los Certificados

### Multi-Tenant

```
-----BEGIN AUTHORSHIP CERTIFICATE-----
Proyecto: AX-S Sistema de Control de Accesos Residencial
Versión: 2.0.0-multitenant
Autor: B10sp4rt4n
Fecha: 2025-11-19
Branch: feature/multi-tenant-fixes
Hash: 82f37e96f626993f5ffd698d8ff557293864c237d1abdf368dcf625e6de37b06
Commits: dbb74e2, e3fc415, 8c36395, e72f5a0, fa4336c
Repository: github.com/B10sp4rt4n/Accesos-Residencial
-----END AUTHORSHIP CERTIFICATE-----
```

### Single-Tenant

```
-----BEGIN AUTHORSHIP CERTIFICATE-----
Proyecto: AX-S Sistema de Control de Accesos Residencial
Versión: 1.0.0-stable
Autor: B10sp4rt4n
Fecha: 2025-11-19
Branch: main
Hash: 56aff2c031a4825cba1b52542b59e0f846da73bf668e339b2aefb7255607c0e0
Tecnologías: Python, Streamlit, SQLite, PostgreSQL
Repository: github.com/B10sp4rt4n/Accesos-Residencial
-----END AUTHORSHIP CERTIFICATE-----
```

---

## 📞 Contacto para Verificación

Si necesitas verificar la autenticidad de cualquier versión:

- **GitHub**: [@B10sp4rt4n](https://github.com/B10sp4rt4n)
- **Repositorio**: [Accesos-Residencial](https://github.com/B10sp4rt4n/Accesos-Residencial)

---

## ⚠️ Qué Hacer si la Verificación Falla

Si los hashes **NO coinciden**, podría indicar:

1. ❌ **Modificación no autorizada** del código
2. ❌ **Copia sin atribución** de otra fuente
3. ❌ **Alteración** de los certificados de autoría
4. ❌ **Fork sin referencia** al repositorio original

### Acciones Recomendadas

- ✅ Verificar que estás usando la versión oficial del repositorio
- ✅ Revisar el historial de commits en GitHub
- ✅ Contactar al autor original para confirmar autenticidad
- ✅ No usar código con hash inválido en producción

---

## 📜 Declaración Legal

Los hashes SHA-256 proporcionados sirven como:

1. **Prueba de Autoría**: Demuestran que B10sp4rt4n es el autor original
2. **Integridad del Código**: Cualquier modificación alterará el hash
3. **Timestamping**: Los commits de Git proporcionan marca temporal
4. **Trazabilidad**: Cada cambio está registrado en el historial de Git

**Nota Legal**: Estos certificados tienen validez como prueba de autoría intelectual. El uso no autorizado del código está prohibido según las leyes de derechos de autor.

---

## ✅ Checklist de Verificación

Usa esta lista para verificar la autenticidad completa:

### Multi-Tenant (v2.0.0)
- [ ] Hash SHA-256 coincide: `82f37e96...`
- [ ] Branch `feature/multi-tenant-fixes` existe
- [ ] Commits dbb74e2, e3fc415, 8c36395, e72f5a0, fa4336c presentes
- [ ] Archivo `AUTHORSHIP_MULTITENANT.md` existe
- [ ] Autor de commits es B10sp4rt4n
- [ ] Repositorio es github.com/B10sp4rt4n/Accesos-Residencial

### Single-Tenant (v1.0.0)
- [ ] Hash SHA-256 coincide: `56aff2c0...`
- [ ] Branch `main` existe
- [ ] Archivo `AUTHORSHIP_SINGLETENANT.md` existe
- [ ] Módulos core presentes (entidades.py, vigilancia.py, etc.)
- [ ] Autor de commits es B10sp4rt4n
- [ ] Repositorio es github.com/B10sp4rt4n/Accesos-Residencial

---

**Documento generado**: 19/11/2025  
**Versión**: 1.0  
**Autor**: B10sp4rt4n

*Este documento es parte del sistema de protección de autoría del proyecto AX-S*
