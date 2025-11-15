# 🚀 Guía de Inicio Rápido

## Para empezar en 10 minutos

### 1️⃣ Compra la Tablet (Día 1)

**Opción Económica:**
- Samsung Galaxy Tab A8 10.5" - [$200 en Amazon](https://amazon.com)
- Funda con soporte - $25
- **Total: $225**

**Dónde comprar:**
- Amazon México
- Best Buy
- Liverpool
- Mercado Libre

---

### 2️⃣ Crea Cuenta en Supabase (5 minutos)

1. Ve a [supabase.com](https://supabase.com)
2. Click en "Start your project"
3. Login con GitHub
4. Create New Project:
   - Name: `accesos-residencial`
   - Database Password: (guarda esta contraseña)
   - Region: South America (São Paulo)
5. Espera 2 minutos a que inicie

**Obtén tus credenciales:**
```
Settings → API →
- Project URL: https://xxx.supabase.co
- anon/public key: eyJhbGc...
```

📝 Guarda estas credenciales, las necesitarás después.

---

### 3️⃣ Despliega en Streamlit Cloud (5 minutos)

1. Ve a [streamlit.io/cloud](https://streamlit.io/cloud)
2. Sign in with GitHub
3. Click "New app"
4. Configuración:
   ```
   Repository: B10sp4rt4n/Accesos-Residencial
   Branch: main
   Main file path: vigilante.py
   ```
5. Click "Deploy!"

**Agrega Secrets (IMPORTANTE):**
```
Settings → Secrets → Edit

Pega esto:
[supabase]
url = "https://xxx.supabase.co"  # Tu URL de Supabase
key = "eyJhbGc..."                # Tu anon key
```

6. Save → La app se reiniciará
7. ¡Tu URL estará lista! `https://tu-app.streamlit.app`

---

### 4️⃣ Crea las Tablas en Supabase (10 minutos)

1. En Supabase, ve a **SQL Editor**
2. Click "New query"
3. Pega este código:

```sql
-- Tabla de personas
CREATE TABLE personas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre VARCHAR(255) NOT NULL,
  tipo VARCHAR(50) NOT NULL,
  curp VARCHAR(18),
  doc_tipo VARCHAR(50),
  casa VARCHAR(50),
  telefono VARCHAR(20),
  status VARCHAR(50) DEFAULT 'activo',
  foto_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de vehículos
CREATE TABLE vehiculos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  persona_id UUID REFERENCES personas(id) ON DELETE CASCADE,
  placa VARCHAR(20) NOT NULL,
  estado_mex VARCHAR(10),
  marca VARCHAR(100),
  modelo VARCHAR(100),
  color VARCHAR(50),
  foto_url TEXT,
  en_lista_negra BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(placa, estado_mex)
);

-- Tabla de eventos
CREATE TABLE eventos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  tipo VARCHAR(20) NOT NULL,
  persona_id UUID REFERENCES personas(id),
  vehiculo_id UUID REFERENCES vehiculos(id),
  placa VARCHAR(20),
  gate_id VARCHAR(50) NOT NULL,
  guardia_id UUID,
  foto_evento_url TEXT,
  placa_confianza DECIMAL(3,2),
  verificacion_manual BOOLEAN DEFAULT false,
  notas TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de políticas
CREATE TABLE politicas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre VARCHAR(255) NOT NULL,
  descripcion TEXT,
  tipo VARCHAR(50),
  prioridad VARCHAR(50),
  aplicable_a VARCHAR(100),
  activa BOOLEAN DEFAULT true,
  config JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_eventos_timestamp ON eventos(timestamp DESC);
CREATE INDEX idx_eventos_placa ON eventos(placa);
CREATE INDEX idx_vehiculos_placa ON vehiculos(placa);
CREATE INDEX idx_personas_tipo ON personas(tipo);

-- Datos de ejemplo (opcional)
INSERT INTO personas (nombre, tipo, curp, casa, telefono) VALUES
  ('Juan Pérez', 'residente', 'CURP001', '15', '5512345678'),
  ('María López', 'residente', 'CURP002', '22', '5587654321');

INSERT INTO vehiculos (persona_id, placa, estado_mex, marca, modelo, color) 
SELECT id, 'ABC-1234', 'CDMX', 'Toyota', 'Corolla', 'Gris' 
FROM personas WHERE nombre = 'Juan Pérez';

INSERT INTO vehiculos (persona_id, placa, estado_mex, marca, modelo, color) 
SELECT id, 'XYZ-7890', 'CDMX', 'Honda', 'Civic', 'Blanco' 
FROM personas WHERE nombre = 'María López';
```

4. Click "Run" (botón abajo)
5. ✅ Deberías ver "Success. No rows returned"

---

### 5️⃣ Configura la Tablet (Día que llegue)

#### A. Configuración inicial Android/iPad

1. **Enciende la tablet**
2. **Conecta a WiFi** de la caseta
3. **Abre Chrome** (o Safari en iPad)
4. **Ve a tu URL**: `https://tu-app.streamlit.app`
5. **Agregar a pantalla de inicio:**
   - Android: Menú (⋮) → "Agregar a pantalla de inicio"
   - iPad: Compartir → "Agregar a inicio"
6. **Resultado:** Ícono como app nativa

#### B. Configuración de seguridad

**Android:**
1. Settings → Display → Screen timeout → 5 minutes
2. Settings → Security → Screen lock → PIN (crea uno simple)
3. Instala "Fully Kiosk Browser" (opcional, para modo kiosco)

**iPad:**
1. Ajustes → Pantalla → Auto-Lock → 5 minutos
2. Ajustes → Face ID → Activar
3. Ajustes → Accesibilidad → Acceso Guiado (modo kiosco)

#### C. Soporte físico

Opciones de montaje:
- **Soporte de escritorio ajustable**: $20-30 (Amazon)
- **Brazo articulado con clamp**: $40-60 (ideal para espacios pequeños)
- **Soporte de pared**: $25-35 (permanente)

---

### 6️⃣ Entrena al Vigilante (30 minutos)

#### Práctica 1: Residente conocido
```
1. "Toma foto de la placa" o "Escribe: ABC-1234"
2. Presiona BUSCAR
3. Ve la info del residente
4. Presiona ✅ PERMITIR ACCESO
5. ¡Listo! Evento registrado
```

#### Práctica 2: Visitante nuevo
```
1. Escribe placa: "DEF-5678"
2. Sistema dice "NO REGISTRADO"
3. Completa formulario:
   - Tipo: Visitante
   - Nombre: Carlos Ruiz
   - Casa: 8
4. Presiona ✅ REGISTRAR Y PERMITIR
5. ¡Listo! Visitante en sistema
```

#### Práctica 3: Lista negra
```
1. Crea un vehículo de prueba en Supabase:
   UPDATE vehiculos SET en_lista_negra = true WHERE placa = 'XXX-9999'
2. Busca esa placa
3. Sistema muestra ALERTA ROJA
4. Acceso denegado automáticamente
```

---

## ✅ Checklist Final

Antes de poner en producción:

- [ ] Tablet comprada y configurada
- [ ] Cuenta Supabase creada
- [ ] Tablas en base de datos creadas
- [ ] App desplegada en Streamlit Cloud
- [ ] Secrets configurados
- [ ] Al menos 10 residentes en BD
- [ ] Al menos 10 vehículos en BD
- [ ] Vigilante entrenado (30 min)
- [ ] WiFi estable en caseta
- [ ] Soporte físico instalado
- [ ] Cable de carga conectado
- [ ] Probado con 5 vehículos reales

---

## 🆘 Solución de Problemas

### "No se conecta a Supabase"
```
1. Verifica Secrets en Streamlit Cloud
2. Confirma que URL tiene https://
3. Confirma que key comienza con "eyJ"
4. Reinicia la app
```

### "La tablet se apaga"
```
1. Conecta cable USB-C permanentemente
2. Settings → Battery → No optimizar
3. Usa cargador de 2A mínimo
```

### "Muy lento"
```
1. Cierra otras apps en tablet
2. Borra caché del navegador
3. Reinicia tablet
4. Verifica señal WiFi (mínimo 3 barras)
```

### "No aparecen los datos"
```
1. Verifica que corriste el SQL en Supabase
2. Table Editor → personas → debe tener filas
3. Refresca la app (F5)
```

---

## 📞 Siguiente Pasos

Una vez funcionando:

1. **Semana 1**: Agregar todos los residentes
2. **Semana 2**: Agregar todos los vehículos
3. **Mes 1**: Evaluar OCR automático
4. **Mes 3**: Considerar segunda tablet/caseta
5. **Mes 6**: Evaluar cámara LPR profesional

---

## 💰 Resumen de Costos

```
INVERSIÓN INICIAL
──────────────────────────────────
Tablet Samsung Tab A8:     $200
Funda + cable:             $25
Soporte:                   $30
──────────────────────────────────
TOTAL INICIAL:             $255


MENSUAL
──────────────────────────────────
Streamlit Cloud:           $0
Supabase:                  $0
Internet (ya existe):      $0
──────────────────────────────────
TOTAL MENSUAL:             $0

COSTO PRIMER AÑO:          $255
```

---

¿Dudas? Revisa `README.md` o `ARQUITECTURA.md` para más detalles.
