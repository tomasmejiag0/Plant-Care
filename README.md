# 🌱 PlantCare AI - Asistente Inteligente de Cuidado de Plantas

**Proyecto Final - Introducción a la Inteligencia Artificial**

> Una aplicación móvil multiplataforma que utiliza arquitectura multi-agente para identificar plantas, evaluar su salud y proporcionar recomendaciones personalizadas.

[![React Native](https://img.shields.io/badge/React_Native-20232A?logo=react&logoColor=61DAFB)](https://reactnative.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://python.org/)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com/)

---

## 📱 Demo Rápido

1. **Toma una foto** de tu planta
2. **Describe** qué has hecho con ella (ej: "La riego cada día")
3. **Recibe** en segundos:
   - 🔍 Identificación de especie
   - 💚 Evaluación de salud (1-10)
   - 🩺 Diagnóstico completo
   - 💡 Recomendaciones personalizadas

## ✨ Características

- ✅ **100% Gratis**: Usa APIs gratuitas (Gemini, Plant.id, Supabase)
- ✅ **Multiplataforma**: iOS y Android con React Native
- ✅ **Arquitectura Multi-Agente**: 4 agentes especializados con LangChain
- ✅ **Base de Datos Vectorial**: Búsqueda semántica con Supabase pgvector
- ✅ **Open Source**: Código completo disponible

## 🚀 Inicio Rápido

### Opción 1: Guía Rápida (15 minutos)
Lee [`QUICK_START.md`](QUICK_START.md) para tener todo funcionando en 15 minutos

### Opción 2: Documentación Completa
Lee [`plant-care-ai-backend/README.md`](plant-care-ai-backend/README.md) para instrucciones detalladas

## 📂 Estructura del Proyecto

```
ia/
├── plant-care-ai-backend/          # Backend FastAPI + Agentes
│   ├── src/
│   │   ├── agentes/                # 4 agentes LangChain
│   │   ├── extraccion.py           # Extracción de datos
│   │   ├── chunking.py             # Segmentación de textos
│   │   ├── embeddings.py           # Vectorización
│   │   ├── similitud.py            # Búsqueda por similitud
│   │   └── vector_db.py            # Supabase pgvector
│   ├── data/plantas/               # Base de conocimiento
│   ├── docs/                       # Documentación técnica
│   │   ├── Documento_Tecnico.md    # Entregable del curso
│   │   ├── SUPABASE_SETUP.md       # Configuración BD
│   │   ├── API_KEYS_GUIDE.md       # Guía de APIs
│   │   └── EJEMPLOS_USO.md         # Casos de uso
│   └── main.py                     # API REST
│
├── plant-care-mobile/              # App React Native
│   ├── src/
│   │   ├── screens/                # Pantallas
│   │   └── services/               # Cliente API
│   └── App.js
│
├── QUICK_START.md                  # Guía de inicio rápido
└── LICENSE                         # MIT License
```

## 🎓 Requisitos del Curso Cumplidos

| Componente | Implementación | ✅ |
|------------|----------------|-----|
| **Extracción** | `src/extraccion.py` | ✅ |
| **Chunking** | `src/chunking.py` (400 chars, overlap 50) | ✅ |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) | ✅ |
| **Similitud** | Similitud del coseno | ✅ |
| **Vector DB** | Supabase + pgvector | ✅ |
| **Multi-Agente** | 4 agentes con LangChain | ✅ |
| **Interfaz** | React Native móvil | ✅ |
| **Documentación** | README + Doc Técnico | ✅ |

## 🤖 Arquitectura Multi-Agente

1. **Agente de Visión**: Gemini Vision + Plant.id → Identifica especie y salud visual
2. **Agente de Conocimiento**: Supabase pgvector → Búsqueda semántica
3. **Agente de Análisis**: Diagnóstico basado en reglas
4. **Agente de Respuesta**: Orquestador LangChain + generación con Gemini

## 📖 Documentación

- **[README Principal](plant-care-ai-backend/README.md)**: Instalación completa y arquitectura
- **[Documento Técnico](plant-care-ai-backend/docs/Documento_Tecnico.md)**: Entregable académico
- **[Inicio Rápido](QUICK_START.md)**: 15 minutos de setup
- **[Guía de APIs](plant-care-ai-backend/docs/API_KEYS_GUIDE.md)**: Cómo obtener API keys gratis
- **[Setup Supabase](plant-care-ai-backend/docs/SUPABASE_SETUP.md)**: Configuración de BD vectorial
- **[Ejemplos de Uso](plant-care-ai-backend/docs/EJEMPLOS_USO.md)**: Casos de uso reales

## 🛠️ Tecnologías

**Backend**:
- FastAPI, LangChain, Google Gemini API, Plant.id API
- Supabase (PostgreSQL + pgvector), sentence-transformers

**Frontend**:
- React Native, Expo, React Navigation
- Axios, Expo Image Picker, Linear Gradient

## 🌟 Próximos Pasos

1. **Instalar**: Sigue [`QUICK_START.md`](QUICK_START.md)
2. **Configurar APIs**: Lee [`API_KEYS_GUIDE.md`](plant-care-ai-backend/docs/API_KEYS_GUIDE.md)
3. **Ejecutar Backend**: `python main.py`
4. **Ejecutar App**: `npm start`
5. **Probar**: Toma foto de una planta! 🌱

## 👨‍💻 Equipo

- [Tu Nombre] - Desarrollo Full Stack

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE)

## 🙏 Agradecimientos

- Curso de Introducción a IA
- Google Gemini API (tier gratuito)
- Plant.id API
- Supabase & pgvector

---

**⭐ Si te gusta el proyecto, compártelo!**

Para más información, consulta la [documentación completa](plant-care-ai-backend/README.md).
