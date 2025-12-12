# Configuración de Supabase (Dual Mode)

PDF Cortex ahora soporta tener **ambas** configuraciones (VPS y Cloud) guardadas en tu `.env` y cambiar entre ellas simplemente modificando una variable (`SUPABASE_TARGET`).

## 1. Crear Base de Datos (SQL)
No importa si usas VPS o Cloud, necesitas ejecutar el script de inicialización en tu base de datos.
1. Abre el **SQL Editor** de tu instancia (Supabase Dashboard o Dokploy UI).
2. Ejecuta el contenido de `supabase_schema.sql`.

## 2. Configurar el `.env`
Copia el contenido de `.env.example` a `.env` y rellena las secciones:

### Variable Maestra
Define cuál entorno usar:
```ini
SUPABASE_TARGET="VPS"  # Usa esto para producción ilimitada
# SUPABASE_TARGET="CLOUD" # Usa esto para pruebas rápidas
```

### Sección VPS (Dokploy / Docker)
*Recomendado para producción.*
```ini
VPS_SUPABASE_URL=http://<IP_TU_VPS>:8000
VPS_SUPABASE_KEY=<TU_SERVICE_ROLE_KEY>
VPS_SUPABASE_DB_URL=postgresql://postgres:password@<IP_TU_VPS>:5432/postgres
```

### Sección Cloud (Supabase.com)
*Opcional, si tienes un proyecto de respaldo.*
```ini
CLOUD_SUPABASE_URL=https://<proyecto>.supabase.co
CLOUD_SUPABASE_KEY=<TU_ANON_KEY>
CLOUD_SUPABASE_DB_URL=postgresql://postgres.usuario:pass@aws-0-....supa...
```

## 3. Reiniciar
Al reiniciar PDF Cortex (`Ctrl+C` -> `uvicorn...`), el sistema leerá `SUPABASE_TARGET` y cargará automáticamente las credenciales correspondientes.
