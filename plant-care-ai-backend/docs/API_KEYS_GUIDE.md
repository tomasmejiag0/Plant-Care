# Lista de APIs Gratuitas

## APIs Necesarias (100% Gratis)

### 1. Google Gemini API 🤖

**Propósito**: LLM para visión de imágenes y generación de recomendaciones

**Tier Gratuito**:
- 15 requests/minuto
- 1,500 requests/día
- Ilimitado para desarrollo

**Cómo obtener**:
1. Ve a [https://ai.google.dev/](https://ai.google.dev/)
2. Click "Get started" → "Get API key in Google AI Studio"
3. Inicia sesión con Google
4. Click "Create API key" → "Create API key in new project"
5. Copia el key (empieza con `AIza...`)
6. Importante: Click "Enable" en Gemini API si aparece mensaje

**Documentación**: [https://ai.google.dev/docs](https://ai.google.dev/docs)

**Nota**: La API es gratuita durante el periodo de preview. Google ha indicado que mantendrá un tier gratuito generoso incluso después.

---

### 2. Plant.id API 🌿

**Propósito**: Identificación de especies de plantas por imagen

**Tier Gratuito**:
- 100 requests/mes
- Suficiente para desarrollo y demos
- Precisión ~85%

**Cómo obtener**:
1. Ve a [https://plant.id/api](https://plant.id/api)
2. Click "Sign Up"
3. Completa registro con email
4. Confirma email
5. Login → Dashboard → API keys
6. Copia tu API key

**Upgrade (Opcional)**:
- Starter: $15/mes - 1,000 requests
- Amateur: $30/mes - 3,000 requests

**Documentación**: [https://github.com/flowerchecker/Plant-id-API/wiki](https://github.com/flowerchecker/Plant-id-API/wiki)

**Alternativas gratuitas**:
- PlantNet API: [https://plantnet.org/](https://plantnet.org/) (requiere autorización)
- Perenual API: [https://perenual.com/docs/api](https://perenual.com/docs/api) (100 req/día gratis)

---

### 3. Supabase 💾

**Propósito**: Base de datos PostgreSQL con pgvector para búsqueda vectorial

**Tier Gratuito**:
- 500 MB de almacenamiento de base de datos
- 2 GB de ancho de banda/mes
- Proyectos ilimitados
- 50,000 usuarios activos mensuales
- pgvector incluido sin costo extra

**Cómo obtener**:
1. Ve a [https://supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign up con GitHub, Google o email
4. Click "New project"
5. Nombra tu proyecto: `plantcare-ai`
6. Crea contraseña de BD (guárdala)
7. Selecciona región (recomendado: más cercana a ti)
8. Click "Create new project" (toma ~2 min)

**Obtener credenciales**:
- Proyecto creado → Settings → API
- Copia **URL** y **anon public key**

**Upgrade (Opcional)**:
- Pro: $25/mes - 8 GB BD, 50 GB bandwidth
- Free tier es suficiente para este proyecto

**Documentación**: [https://supabase.com/docs](https://supabase.com/docs)

---

## Modelos Open Source (Sin API Key)

### sentence-transformers 📊

**Propósito**: Generación de embeddings vectoriales

**Modelo usado**: `all-MiniLM-L6-v2`
- Dimensiones: 384
- Tamaño: ~80 MB
- Velocidad: ~200 embeddings/seg en CPU
- Calidad: Excelente para búsqueda semántica

**Instalación**:
```bash
pip install sentence-transformers
```

La primera vez que ejecutes el código, descargará el modelo automáticamente. Luego se cachea localmente.

**Alternativas**:
- `all-mpnet-base-v2`: Mayor calidad pero más lento (768 dims)
- `paraphrase-multilingual-MiniLM-L12-v2`: Multilenguaje

**Hugging Face**: [https://huggingface.co/sentence-transformers](https://huggingface.co/sentence-transformers)

---

## Comparación de Costos

| API | Gratis | Límite | Suficiente para proyecto |
|-----|--------|--------|--------------------------|
| **Gemini** | ✅ Sí | 15 req/min | ✅ Sobra |
| **Plant.id** | ✅ Sí | 100 req/mes | ✅ Para demos |
| **Supabase** | ✅ Sí | 500 MB | ✅ Perfecto |
| **sentence-transformers** | ✅ Sí | Ilimitado (local) | ✅ Ilimitado |

**Total mensual**: $0 USD 💰

---

## APIs de Pago (Alternativas - NO Necesarias)

### OpenAI API (Alternativa a Gemini)

Si decides usar OpenAI en lugar de Gemini:

**Modelos**:
- GPT-4o mini (visión): $0.15/1M tokens input
- GPT-3.5 turbo: $0.50/1M tokens
- text-embedding-3-small: $0.02/1M tokens

**Costo estimado**: ~$2-5/mes para desarrollo moderado

**Cómo obtener**:
1. [https://platform.openai.com/signup](https://platform.openai.com/signup)
2. Settings → Billing → Add payment method
3. Settings → API keys → Create new key

**Ventajas**:
- Sin rate limits estrictos
- Embeddings nativos mejores
- GPT-4o excelente en visión

**Desventajas**:
- Requiere tarjeta de crédito
- No hay tier totalmente gratuito

---

### Google Cloud Vision API (Alternativa a Gemini Vision)

**Pricing**:
- 1,000 requests/mes gratis
- Luego $1.50/1,000 imágenes

**No recomendado**: Gemini Vision es gratis y mejor

---

## Configuración Final

Una vez que tengas todas las API keys, crea el archivo `.env`:

```env
# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Google Gemini (Gratis)
GEMINI_API_KEY=AIzaSy...

# Plant.id (Gratis - 100 req/mes)
PLANT_ID_API_KEY=xxxxx

# Server Config
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

---

## Rate Limits y Best Practices

### Gemini API
- **Límite**: 15 req/min
- **Tip**: Implementa retry con backoff exponencial
- **Cachea** resultados cuando sea posible

### Plant.id
- **Límite**: 100 req/mes
- **Tip**: Guarda identificaciones en BD para no repetir
- **Fallback**: Si se acaba, usa solo Gemini Vision

### sentence-transformers
- **Sin límites**
- **Tip**: Cachea embeddings de documentos (no regenerar)
- **Performance**: Usa GPU si disponible (opcional)

---

## Verificación

Para verificar que tus API keys funcionan:

```bash
# Desde el directorio del backend
python

>>> import os
>>> from dotenv import load_dotenv
>>> load_dotenv()
>>> print(os.getenv("GEMINI_API_KEY")[:10])  # Debe mostrar AIzaSy...
>>> print(os.getenv("SUPABASE_URL"))  # Debe mostrar https://...
```

---

## ¿Preguntas?

- **Gemini**: [Google AI Studio](https://ai.google.dev/)
- **Plant.id**: [Support](mailto:support@kindwise.com)
- **Supabase**: [Discord](https://discord.supabase.com/)

## Recursos Adicionales

- [Gemini API Cookbook](https://github.com/google-gemini/cookbook)
- [Supabase Vector Guide](https://supabase.com/docs/guides/ai)
- [sentence-transformers Docs](https://www.sbert.net/)

---

**Última actualización**: Noviembre 2025  
**Todas las APIs verificadas como gratuitas al momento de creación**
