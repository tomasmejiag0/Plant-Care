# 🚀 Guía de Inicio Rápido - PlantCare AI

Esta guía te ayudará a tener PlantCare AI funcionando en menos de 15 minutos.

## ⚡ Pre-requisitos Rápidos

Antes de comenzar, asegúrate de tener:
- [ ] Python 3.9+ instalado
- [ ] Node.js 16+ instalado  
- [ ] Cuenta de Supabase (gratis en supabase.com)
- [ ] API key de Google Gemini (gratis en ai.google.dev)
- [ ] API key de Plant.id (gratis en plant.id/api)

## 📋 Paso 1: Obtener API Keys (5 min)

### Google Gemini API
1. Ve a [ai.google.dev](https://ai.google.dev/)
2. Click "Get API key in Google AI Studio"
3. Click "Create API key"
4. Copia el key (empieza con `AIza...`)

### Plant.id API
1. Ve a [plant.id/api](https://plant.id/api)
2. Sign up gratis
3. Confirma email
4. Ve a Dashboard → API keys
5. Copia tu API key

### Supabase
1. Ve a [supabase.com](https://supabase.com)
2. Create account
3. New Project → Nombra "plantcare-ai"
4. Espera ~2 min mientras se crea
5. Settings → API → Copia URL y anon key

## 🔧 Paso 2: Configurar Backend (5 min)

```bash
# Clonar (o navegar a tu carpeta)
cd c:/Users/Tomaas/OneDrive/Escritorio/ia/plant-care-ai-backend

# Crear entorno virtual
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Configurar .env

```bash
# Copiar template
copy .env.example .env

# Editar .env con tus keys
notepad .env
```

Pega tus claves:
```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=eyJhbGc...
GEMINI_API_KEY=AIza...
PLANT_ID_API_KEY=tu_plant_id_key
```

### Configurar Supabase (3 min)

Abre el archivo `docs/SUPABASE_SETUP.md` y sigue los pasos 2-4 (copiar y ejecutar SQL).

O rápidamente:
1. Supabase → SQL Editor
2. Ejecuta estos 4 comandos (uno por uno):

```sql
create extension if not exists vector;
```

```sql
create table if not exists plant_documents (
  id bigserial primary key,
  chunk_id text unique not null,
  source_file text not null,
  chunk_index int not null,
  text text not null,
  embedding vector(384),
  created_at timestamptz default now()
);
create index on plant_documents using ivfflat (embedding vector_cosine_ops);
```

```sql
create or replace function match_plant_documents (
  query_embedding vector(384),
  match_threshold float,
  match_count int
)
returns table (
  id bigint,
  chunk_id text,
  source_file text,
  text text,
  similarity float
)
language sql stable
as $$
  select id, chunk_id, source_file, text,
    1 - (embedding <=> query_embedding) as similarity
  from plant_documents
  where 1 - (embedding <=> query_embedding) > match_threshold
  order by embedding <=> query_embedding
  limit match_count;
$$;
```

### Procesar Documentos

```bash
python process_documents.py
```

Deberías ver: ✅ Indexación completada (23 chunks)

### Iniciar Backend

```bash
python main.py
```

✅ Si ves "Backend listo para recibir peticiones" → ¡Éxito!

Prueba: Abre http://localhost:8000/docs

## 📱 Paso 3: Configurar App Móvil (3 min)

```bash
cd ../plant-care-mobile

npm install

# Instalar Expo CLI (si no lo tienes)
npm install -g expo-cli
```

### Configurar IP del Backend

1. Busca tu IP local:
   - Windows: `ipconfig` → busca IPv4 Address (ej: 192.168.1.10)
   - Mac/Linux: `ifconfig` → busca inet (ej: 192.168.1.10)

2. Edita `src/services/api.js`:

```javascript
const API_BASE_URL = 'http://TU_IP_AQUI:8000'; // Ejemplo: http://192.168.1.10:8000
```

### Iniciar App

```bash
npm start
```

Escanea el QR con Expo Go (descarga de App Store/Play Store)

## ✅ Paso 4: ¡Probar! (2 min)

1. Abre la app en tu teléfono
2. Toma una foto de una planta (o usa una de Google Images)
3. Describe: "La riego cada día"
4. Presiona "Analizar Planta"
5. Espera 5-10 segundos
6. ¡Disfruta los resultados! 🌱

## 🐛 Troubleshooting Rápido

### Backend no inicia
- ✅ Verifica que el .env tiene API keys correctas
- ✅ Activa el entorno virtual: `venv\Scripts\activate`

### App no conecta al backend
- ✅ Verifica que usaste tu IP local (no localhost)
- ✅ Backend y móvil deben estar en la misma red WiFi
- ✅ Firewall de Windows puede bloquear puerto 8000

### Error en Supabase
- ✅ Verifica que ejecutaste los 3 scripts SQL
- ✅ Ejecuta `python process_documents.py` de nuevo

### Plant.id/Gemini error
- ✅ Verifica las API keys en .env
- ✅ Gemini: Asegúrate de habilitar "Gemini API" en Google AI Studio
- ✅ Plant.id: Confirma tu email

## 📖 Próximos Pasos

- Lee el README.md completo
- Revisa Documento_Tecnico.md
- Agrega más documentos de plantas en `data/plantas/`
- Personaliza la UI de la app móvil

## 🆘 ¿Necesitas Ayuda?

1. Revisa los logs del backend (terminal donde corre `python main.py`)
2. Revisa la consola de Expo
3. Abre un issue en GitHub

---

**¡Felicidades!** 🎉 Tienes un sistema de IA completamente funcional. 

**Tiempo estimado**: ~15 minutos  
**Próximo objetivo**: Tomar foto de 10 plantas diferentes
