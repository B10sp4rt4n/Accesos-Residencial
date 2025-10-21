# Accesos-Residencial

Proyecto demo de consola de caseta (Streamlit).

Cómo desplegar en Streamlit Cloud

1. Ir a https://streamlit.io/cloud e iniciar sesión con GitHub.
2. Crear una nueva app y conectar este repositorio.
3. Como `Main file` usar: `app.py` (en la raíz del repo).
4. Streamlit Cloud instalará las dependencias desde `requirements.txt` automáticamente.
5. Opcional: en la sección "Secrets" de tu app en Streamlit Cloud añade variables sensibles (ej.: `SUPABASE_URL`, `SUPABASE_KEY`) si vas a conectar a Supabase.

Nota sobre reproducibilidad

Se han fijado versiones básicas en `requirements.txt` para evitar sorpresas en Cloud. Si quieres actualizar a versiones más recientes, edita `requirements.txt` y crea un nuevo commit.

Ejecución local

1. Crear un entorno virtual e instalar dependencias:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Ejecutar la app localmente:

```bash
streamlit run app.py
```

Notas

- Si planeas usar Supabase, añade las variables de entorno en la sección "Secrets" de Streamlit Cloud (`SUPABASE_URL`, `SUPABASE_KEY`).
- El archivo `app_accesos_residencial` contiene la app principal; se exporta vía `app.py` para facilitar el despliegue.
Software Acceso a Resdencial
