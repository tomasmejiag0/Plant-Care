# Documento Técnico – Proyecto Final Introducción a IA

**Proyecto**: PlantCare AI - Asistente Inteligente de Cuidado de Plantas  
**Equipo**: Tomas Mejia - Johan Gomez  
**Fecha**: Noviembre 2025  
**Curso**: Introducción a la Inteligencia Artificial

---

## 1. Introducción

### 1.1 Contexto y Problema

En un mundo donde cada vez más personas cultivan plantas en sus hogares y espacios de trabajo, existe una necesidad creciente de herramientas que ayuden a mantenerlas saludables. Muchas personas, especialmente principiantes, enfrentan dificultades para:

- **Identificar especies**: No saben qué tipo de planta tienen
- **Detectar problemas**: No reconocen síntomas de enfermedades o mal cuidado
- **Aplicar cuidados adecuados**: Información genérica que no considera el contexto específico
- **Obtener respuestas rápidas**: Necesitan ayuda inmediata sin buscar en múltiples fuentes

### 1.2 Solución Propuesta

**PlantCare AI** es un sistema inteligente de cuidado de plantas que combina:

- **Análisis de imágenes** mediante visión por computadora
- **Búsqueda semántica** en base de conocimiento vectorial
- **Generación de respuestas naturales** usando LLMs
- **Arquitectura multiagente** para razonamiento robusto

El sistema permite a los usuarios:
1. Subir una imagen de su planta y recibir identificación y análisis de salud
2. Hacer preguntas abiertas sobre cuidado de plantas sin necesidad de imagen
3. Obtener recomendaciones personalizadas basadas en su situación específica

### 1.3 Objetivo General

Desarrollar una aplicación web que demuestre la aplicación práctica de conceptos fundamentales de IA moderna:

1. **Manejo de datos**: Extracción y procesamiento de documentos
2. **Segmentación (chunks)**: División de texto en fragmentos manejables
3. **Embeddings y similitud**: Conversión de texto a vectores y búsqueda semántica
4. **Base de datos vectorial**: Almacenamiento y consulta eficiente de embeddings
5. **Extracción de datos**: Uso de APIs (OCR, Vision) para análisis de imágenes
6. **Arquitectura multiagente en LangChain**: Coordinación de agentes especializados

---

## 2. Metodología

### 2.1 Fuente de Datos

**Módulo**: `src/extraccion.py`

Se recopilaron y procesaron **20+ documentos** de conocimiento especializado sobre cuidado de plantas:

- Suculentas (cuidado general, propagación, problemas comunes)
- Cactus (especies específicas, riego, iluminación)
- Plantas de interior comunes (Pothos, Monstera, Sansevieria, etc.)
- Problemas comunes y soluciones (hojas amarillas, plagas, enfermedades)
- Guías de riego, luz, suelo y fertilización

**Formato de documentos**:
- Archivos Markdown (.md)
- Archivos de texto plano (.txt)
- Encoding UTF-8

**Proceso de extracción**:
1. Lectura de archivos desde directorio `data/plantas/`
2. Validación de encoding UTF-8
3. Extracción completa del contenido textual
4. Metadata: nombre de archivo, ruta, longitud de caracteres

### 2.2 Segmentación (Chunking)

**Módulo**: `src/chunking.py`

**Estrategia de segmentación**:
- **Tamaño de chunk**: 400 caracteres
- **Overlap**: 50 caracteres (12.5%)
- **Respeto de límites**: Mantiene coherencia contextual entre chunks

**Justificación de parámetros**:
- 400 caracteres: Balance entre contexto suficiente y eficiencia de búsqueda
- Overlap del 12.5%: Evita pérdida de información en límites de chunks
- Límites de oraciones: Mantiene coherencia semántica

**Estructura de cada chunk**:
```python
{
    'chunk_id': 'doc1_chunk_0',
    'source_file': 'suculentas.md',
    'chunk_index': 0,
    'text': 'Las suculentas son plantas que almacenan agua...'
}
```

**Ejemplo de chunking**:
```
Documento original:
"Las suculentas son plantas que almacenan agua en sus hojas y tallos. 
Requieren poco riego, aproximadamente cada 10-14 días. Prefieren luz 
indirecta brillante. El exceso de riego puede causar pudrición de raíces."

Chunk 1 (0-400):
"Las suculentas son plantas que almacenan agua en sus hojas y tallos. 
Requieren poco riego, aproximadamente cada 10-14 días. Prefieren luz 
indirecta brillante. El exceso de riego..."

Chunk 2 (350-750):
"...poco riego, aproximadamente cada 10-14 días. Prefieren luz 
indirecta brillante. El exceso de riego puede causar pudrición de raíces."
```

**Resultado**: 20+ documentos → ~200+ chunks indexados

### 2.3 Embeddings y Similitud

**Módulo**: `src/embeddings.py`, `src/similitud.py`

#### Modelo de Embeddings

**Modelo seleccionado**: `sentence-transformers/all-MiniLM-L6-v2`

**Características**:
- **Dimensiones**: 384
- **Velocidad**: ~200 vectorizaciones/segundo en CPU
- **Tamaño**: 80 MB (descarga única)
- **Licencia**: Open source (Apache 2.0)
- **Optimización**: Específicamente entrenado para búsqueda semántica

**Ventajas del modelo elegido**:
- ✅ No requiere GPU (funciona en CPU)
- ✅ Rápido y eficiente
- ✅ Buen balance precisión/velocidad
- ✅ Optimizado para tareas de similitud semántica
- ✅ Multilingüe (incluye español)

#### Proceso de Generación de Embeddings

```python
from sentence_transformers import SentenceTransformer

# 1. Cargar modelo
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Generar embedding para un texto
text = "¿Cómo cuido una suculenta?"
embedding = model.encode(text, normalize_embeddings=True)

# Resultado: array numpy de 384 números
# Ejemplo: [0.23, -0.45, 0.12, 0.89, ...]
```

**Normalización L2**: 
- Importante para calcular similitud del coseno eficientemente
- Permite usar producto punto en lugar de cálculo completo de coseno
- Fórmula: `similitud = dot(emb1, emb2)` cuando ambos están normalizados

#### Similitud del Coseno

**Módulo**: `src/similitud.py`

**Algoritmo**:
```python
# Para embeddings normalizados:
similarity = np.dot(embedding1, embedding2)

# Para embeddings no normalizados:
similarity = np.dot(embedding1, embedding2) / (
    np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
)
```

**Rango de valores**: -1 a 1
- **1.0**: Textos idénticos o muy similares
- **0.0**: Textos no relacionados
- **-1.0**: Textos opuestos (raro en práctica)

**Umbral de relevancia**: 0.25 (25% de similitud mínima)
- Documentos con similitud < 0.25 se consideran no relevantes
- Ajustado empíricamente para balancear precisión y recall

### 2.4 Base de Datos Vectorial

**Tecnología**: Supabase (PostgreSQL) + extensión pgvector

**Módulo**: `src/vector_db.py`

#### Configuración de la Base de Datos

**Tabla `plant_documents`**:
```sql
CREATE TABLE plant_documents (
    id BIGSERIAL PRIMARY KEY,
    chunk_id TEXT UNIQUE NOT NULL,
    source_file TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    embedding VECTOR(384),  -- Vector de 384 dimensiones
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Índice para búsqueda eficiente**:
```sql
CREATE INDEX ON plant_documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

**Función de búsqueda vectorial**:
```sql
CREATE OR REPLACE FUNCTION match_plant_documents (
    query_embedding VECTOR(384),
    match_threshold FLOAT,
    match_count INT
)
RETURNS TABLE (
    id BIGINT,
    chunk_id TEXT,
    source_file TEXT,
    text TEXT,
    similarity FLOAT
)
LANGUAGE SQL STABLE
AS $$
    SELECT
        id,
        chunk_id,
        source_file,
        text,
        1 - (embedding <=> query_embedding) AS similarity
    FROM plant_documents
    WHERE 1 - (embedding <=> query_embedding) > match_threshold
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$;
```

**Operador `<=>`**: Calcula distancia coseno entre vectores
- `embedding <=> query_embedding`: Distancia (0 = idénticos, 2 = opuestos)
- `1 - distancia = similitud`: Convierte distancia a similitud

#### Ventajas de Supabase + pgvector

- ✅ **Tier gratuito**: 500 MB de datos, suficiente para el proyecto
- ✅ **pgvector nativo**: Extensión oficial de PostgreSQL
- ✅ **API REST automática**: Acceso fácil desde Python
- ✅ **Escalable**: Soporta millones de vectores
- ✅ **Índices optimizados**: IVFFlat para búsqueda rápida

#### Proceso de Indexación

1. **Generar embeddings** para todos los chunks
2. **Insertar en Supabase** con embeddings vectoriales
3. **Crear índice IVFFlat** para búsqueda eficiente
4. **Verificar**: Consulta de prueba para validar funcionamiento

**Código de indexación**:
```python
# 1. Generar embeddings para todos los chunks
embeddings = embedding_generator.generate_embeddings_batch(chunk_texts)

# 2. Insertar en Supabase
vector_db.insert_chunks(chunks, embeddings)

# 3. Búsqueda de prueba
results = vector_db.search_similar(query_embedding, top_k=5, threshold=0.25)
```

### 2.5 Extracción de Datos con APIs

#### 2.5.1 Plant.id API

**Propósito**: Identificación de especies de plantas

**Endpoint**: `https://api.plant.id/v2/identify`

**Proceso**:
1. Codificar imagen en base64
2. Enviar POST request con imagen
3. Recibir sugerencias con especies y probabilidades
4. Seleccionar mejor coincidencia

**Ejemplo de respuesta**:
```json
{
    "suggestions": [
        {
            "plant_name": "Echeveria elegans",
            "probability": 0.85,
            "plant_details": {
                "common_names": ["Mexican snowball", "Mexican gem"]
            }
        }
    ]
}
```

**Ventajas**:
- ✅ Especializado en identificación de plantas
- ✅ Alta precisión para especies comunes
- ✅ Incluye nombres comunes y taxonomía

#### 2.5.2 Google Gemini Vision API

**Propósito**: Análisis visual de salud de plantas (fallback para identificación)

**Modelo**: `gemini-pro` (multimodal)

**Capacidades**:
- Análisis de imágenes para detectar problemas visuales
- Identificación de síntomas (hojas amarillas, manchas, plagas)
- Evaluación general del estado de salud

**Prompt estructurado**:
```
Analiza esta imagen de planta y proporciona:
1. Estado general de salud (1-10)
2. Problemas visuales detectados
3. Síntomas observables
4. Recomendaciones visuales básicas
```

**Ventajas**:
- ✅ Multimodal (texto + imagen)
- ✅ Análisis contextual avanzado
- ✅ Fallback cuando Plant.id no está disponible

### 2.6 Arquitectura Multi-Agente con LangChain

**Framework**: LangChain (versión 0.1.4+)

**Módulo principal**: `src/agentes/agente_respuesta_langchain.py`

#### 2.6.1 ¿Qué es LangChain?

LangChain es un framework de código abierto diseñado para construir aplicaciones con LLMs. Proporciona:

- **AgentExecutor**: Orquestador para ejecutar múltiples agentes
- **Tools**: Herramientas especializadas que los agentes pueden usar
- **Chains**: Secuencias de operaciones con LLMs
- **Memory**: Gestión de contexto conversacional
- **Prompts**: Templates estructurados para LLMs

#### 2.6.2 Componentes LangChain Utilizados

**1. AgentExecutor**:
```python
from langchain.agents import AgentExecutor, create_structured_chat_agent

executor = AgentExecutor(
    agent=create_structured_chat_agent(llm, tools, prompt),
    tools=tools,
    memory=ConversationBufferMemory(),
    verbose=True,
    max_iterations=5
)
```

**2. Tools (Herramientas)**:
```python
from langchain.tools import Tool

tools = [
    Tool(
        name="vision_analysis",
        func=vision_agent.execute,
        description="Analiza imágenes de plantas para identificar especie y estado de salud"
    ),
    Tool(
        name="knowledge_search",
        func=knowledge_agent.search_knowledge,
        description="Busca información relevante en la base de conocimiento vectorial"
    ),
    Tool(
        name="plant_analysis",
        func=analysis_agent.execute,
        description="Realiza análisis y diagnóstico completo de la planta"
    )
]
```

**3. ChatPromptTemplate**:
```python
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", """Eres un asistente experto en cuidado de plantas...
    Tienes acceso a las siguientes herramientas: {tools}
    {agent_scratchpad}"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])
```

**4. ConversationBufferMemory**:
```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)
```

**5. ChatGoogleGenerativeAI**:
```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    google_api_key=GEMINI_API_KEY
)
```

#### 2.6.3 Flujo de Orquestación

```
1. Usuario envía input (imagen + pregunta o solo pregunta)
   ↓
2. AgentExecutor recibe input
   ↓
3. LLM decide qué Tool usar primero (vision_analysis)
   ↓
4. Vision Agent ejecuta → identifica especie y problemas visuales
   ↓
5. LLM decide usar knowledge_search
   ↓
6. Knowledge Agent ejecuta → busca documentos relevantes en Supabase
   ↓
7. LLM decide usar plant_analysis
   ↓
8. Analysis Agent ejecuta → genera diagnóstico completo
   ↓
9. LLM genera recomendaciones finales usando todo el contexto
   ↓
10. Response estructurado → JSON final
```

### 2.7 Agentes Especializados

#### Agente 1: Vision Agent

**Archivo**: `src/agentes/agente_vision.py`

**Responsabilidades**:
1. Identificar especie de planta (Plant.id API)
2. Analizar estado de salud visual (Gemini Vision)
3. Detectar problemas visuales (manchas, color, plagas)

**Flujo de ejecución**:
```python
def execute(self, image_path: str, user_actions: str = "") -> Dict:
    # 1. Identificar especie
    species_info = self.identify_plant_species(image_path)
    # Resultado: {'species': 'Echeveria', 'probability': 0.85}
    
    # 2. Analizar salud visual
    health_info = self.analyze_plant_health(image_path, user_actions)
    # Resultado: {'health_score': 6, 'visual_problems': ['hojas amarillas']}
    
    # 3. Combinar resultados
    return {
        'species': species_info['species'],
        'health_score': health_info['health_score'],
        'visual_problems': health_info['visual_problems']
    }
```

**Output ejemplo**:
```json
{
    "agent": "VisionAgent",
    "species": "Echeveria elegans",
    "species_probability": 0.85,
    "common_names": ["Mexican snowball"],
    "health_score": 6,
    "health_status": "Regular - Requiere atención",
    "visual_problems": ["hojas amarillas", "manchas marrones"]
}
```

#### Agente 2: Knowledge Agent

**Archivo**: `src/agentes/agente_conocimiento.py`

**Responsabilidades**:
1. Construir consulta mejorada (especie + problemas + acciones usuario)
2. Generar embedding de la consulta
3. Buscar documentos relevantes en Supabase
4. Retornar top 5 documentos más relevantes

**Flujo de ejecución**:
```python
def search_knowledge(self, query: str, species: str, problems: List[str]) -> List[Dict]:
    # 1. Construir consulta mejorada
    enhanced_query = f"{species} {query} problemas: {', '.join(problems)}"
    # Ejemplo: "Echeveria elegans ¿Cómo la cuido? problemas: hojas amarillas"
    
    # 2. Generar embedding
    query_embedding = self.embedding_generator.generate_embedding(enhanced_query)
    
    # 3. Buscar en Supabase
    results = self.vector_db.search_similar(
        query_embedding, 
        top_k=5, 
        threshold=0.25
    )
    
    # 4. Formatear resultados
    return [
        {
            'text': doc['text'],
            'source': doc['source_file'],
            'relevance_score': score
        }
        for doc, score in results
    ]
```

**Output ejemplo**:
```json
{
    "documents": [
        {
            "text": "Las suculentas requieren riego moderado...",
            "source": "suculentas.md",
            "relevance_score": 0.87
        },
        {
            "text": "Hojas amarillas pueden indicar exceso de riego...",
            "source": "problemas_comunes.md",
            "relevance_score": 0.82
        }
    ]
}
```

#### Agente 3: Analysis Agent

**Archivo**: `src/agentes/agente_analisis.py`

**Responsabilidades**:
1. Analizar riego (exceso/falta basado en acciones del usuario)
2. Analizar iluminación (basado en problemas visuales)
3. Calcular puntuación final de salud
4. Generar diagnóstico completo

**Algoritmo de análisis**:
```python
def calculate_health_score(self, visual_score: int, problems_count: int, severity: int) -> int:
    # Score inicial del análisis visual
    score = visual_score
    
    # Penalizar por número de problemas
    score -= problems_count * 0.5
    
    # Penalizar por severidad
    score -= severity * 0.3
    
    # Mantener en rango 1-10
    return max(1, min(10, int(score)))
```

**Reglas de diagnóstico**:
- **Exceso de riego**: Detectado si usuario dice "riego cada día" + hojas amarillas
- **Falta de luz**: Detectado si hay problemas visuales de coloración + ubicación sombría
- **Plagas**: Detectado si hay manchas o síntomas específicos en análisis visual

**Output ejemplo**:
```json
{
    "agent": "AnalysisAgent",
    "health_score": 4,
    "overall_status": "Regular - Requiere atención",
    "diagnosis": "La Echeveria presenta exceso de riego detectado",
    "identified_issues": [
        {
            "type": "exceso_de_riego",
            "severity": 9,
            "description": "Riego excesivo detectado por frecuencia y síntomas visuales"
        }
    ]
}
```

#### Agente 4: Response Agent (Orquestador)

**Archivo**: `src/agentes/agente_respuesta_langchain.py`

**Responsabilidades**:
1. Orquestar ejecución de todos los agentes usando LangChain
2. Coordinar Tools especializados
3. Generar recomendaciones finales con LLM
4. Mantener contexto conversacional

**Implementación con LangChain**:
```python
class ResponseAgentLangChain:
    def __init__(self):
        # Inicializar agentes especializados
        self.vision_agent = VisionAgent()
        self.knowledge_agent = KnowledgeAgent()
        self.analysis_agent = AnalysisAgent()
        
        # Configurar LLM
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        
        # Crear Tools
        self.tools = self._create_tools()
        
        # Crear AgentExecutor
        self.agent_executor = self._create_agent_executor()
    
    def execute(self, image_path: str, user_question: str) -> Dict:
        # AgentExecutor coordina automáticamente la ejecución
        result = self.agent_executor.invoke({
            "input": f"Analiza esta planta: {user_question}",
            "image_path": image_path
        })
        return result
```

**Output final**:
```json
{
    "success": true,
    "plant_info": {
        "species": "Echeveria elegans",
        "common_names": ["Mexican snowball"],
        "confidence": 0.85
    },
    "health_assessment": {
        "score": 4,
        "status": "Regular - Requiere atención",
        "visual_problems": ["hojas amarillas", "manchas marrones"]
    },
    "diagnosis": "La Echeveria presenta exceso de riego detectado",
    "recommendations": [
        "Reduce el riego a cada 10-14 días",
        "Verifica que la maceta tenga buen drenaje",
        "Permite que la tierra se seque completamente entre riegos",
        "Considera trasplantar si las raíces están podridas"
    ]
}
```

### 2.8 LLM y Generación de Respuestas

#### 2.8.1 Google Gemini

**Modelo principal**: `gemini-2.5-flash`

**Uso**:
- Generación de recomendaciones personalizadas
- Análisis de contexto conversacional
- Orquestación inteligente de agentes

**Configuración**:
```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,  # Balance creatividad/consistencia
    google_api_key=GEMINI_API_KEY
)
```

**Prompt para recomendaciones**:
```
Eres un experto en cuidado de plantas. Basándote en:
- Especie: {species}
- Diagnóstico: {diagnosis}
- Conocimiento relevante: {context}
- Pregunta del usuario: {user_question}

Genera 3-5 recomendaciones específicas y accionables.
Si el usuario menciona una preocupación específica (como "arranqué una hoja"),
aborda esa preocupación directamente.
```

#### 2.8.2 Ollama (LLM Local)

**Propósito**: Fallback cuando Gemini no está disponible

**Modelo**: `llama3.2` (1B, 3B, o 7B parámetros)

**Módulo**: `src/local_llm.py`

**Ventajas**:
- ✅ Funciona sin conexión a internet
- ✅ No consume cuota de APIs externas
- ✅ Privacidad total (datos no salen del servidor)
- ✅ Gratuito y open source

**Configuración**:
```python
from src.local_llm import get_local_llm

# Detectar Ollama disponible
local_llm = get_local_llm()  # Retorna None si no está disponible

# Usar si Gemini falla
if not gemini_available and local_llm:
    response = local_llm.generate(prompt)
```

**Cadena de fallback**:
```
1. Intentar Gemini → Si falla o sin cuota
2. Intentar Ollama local → Si no disponible
3. Usar solo documentos (DocumentProcessor) → Si no hay documentos relevantes
4. Modo demo (respuestas predefinidas)
```

### 2.9 Interfaz Web

**Tecnologías**: HTML5, CSS3, JavaScript (Vanilla)

**Archivos**:
- `plant-care-web/index.html`: Estructura
- `plant-care-web/styles.css`: Estilos (glassmorphism, animaciones)
- `plant-care-web/script.js`: Lógica de frontend

**Características**:
- Diseño moderno con efecto glass-panel
- Animaciones CSS (flotación, respiración)
- Drag & drop para imágenes
- Chat interactivo con historial
- Visualización de resultados formateados

**Flujo de usuario**:
```
1. Usuario abre index.html en navegador
2. Opción A: Sube imagen + pregunta
   Opción B: Solo pregunta (sin imagen)
3. Frontend envía request a FastAPI backend
4. Backend procesa con agentes
5. Frontend recibe y muestra resultados
6. Usuario puede continuar conversación
```

---

## 3. Arquitectura del Sistema

### 3.1 Diagrama de Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                    USUARIO (Navegador Web)                  │
│                    plant-care-web/index.html                 │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP POST /api/analyze-plant
                           │ HTTP POST /api/chat
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (main.py)                      │
│              Puerto: 8000                                   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │     Response Agent (Orquestador LangChain)            │  │
│  │     agente_respuesta_langchain.py                     │  │
│  │                                                        │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │  AgentExecutor (LangChain)                      │ │  │
│  │  │  - Coordina ejecución de Tools                  │ │  │
│  │  │  - Mantiene memoria conversacional              │ │  │
│  │  └──────────────┬───────────────────────────────────┘ │  │
│  │                 │                                      │  │
│  │  ┌──────────────┼──────────────┬──────────────┐       │  │
│  │  │              │              │              │       │  │
│  │  ▼              ▼              ▼              ▼       │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────┐ │  │
│  │  │ Vision   │  │Knowledge │  │ Analysis │  │ LLM  │ │  │
│  │  │ Agent    │  │ Agent    │  │ Agent    │  │Gemini│ │  │
│  │  │          │  │          │  │          │  │Ollama│ │  │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┘ │  │
│  │       │             │             │                  │  │
│  │       ▼             ▼             ▼                  │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │  │
│  │  │ Plant.id │  │ Supabase │  │ Reglas   │           │  │
│  │  │ API      │  │ pgvector │  │ Lógica   │           │  │
│  │  │ Gemini   │  │ Embeddings│  │          │           │  │
│  │  │ Vision   │  │ Búsqueda │  │          │           │  │
│  │  └──────────┘  └──────────┘  └──────────┘           │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │ JSON Response
                           ▼
                    ┌─────────────┐
                    │   Usuario   │
                    │  Ve Resultados│
                    └─────────────┘
```

### 3.2 Flujo de Datos Detallado

#### Flujo 1: Análisis de Imagen

```
Usuario sube imagen + pregunta
    ↓
FastAPI recibe POST /api/analyze-plant
    ↓
Response Agent (LangChain) inicia
    ↓
AgentExecutor decide usar vision_analysis Tool
    ↓
Vision Agent ejecuta:
  ├─ Plant.id API → identifica especie
  └─ Gemini Vision → analiza salud visual
    ↓
AgentExecutor decide usar knowledge_search Tool
    ↓
Knowledge Agent ejecuta:
  ├─ Construye consulta mejorada
  ├─ Genera embedding
  └─ Busca en Supabase → documentos relevantes
    ↓
AgentExecutor decide usar plant_analysis Tool
    ↓
Analysis Agent ejecuta:
  ├─ Analiza riego/luz
  ├─ Calcula score final
  └─ Genera diagnóstico
    ↓
LLM (Gemini/Ollama) genera recomendaciones
    ↓
Response estructurado → JSON
    ↓
Frontend muestra resultados
```

#### Flujo 2: Chat sin Imagen

```
Usuario escribe pregunta (ej: "¿Cómo cuido una suculenta?")
    ↓
FastAPI recibe POST /api/chat
    ↓
Knowledge Agent busca documentos relevantes
    ↓
Si documentos encontrados:
  ├─ LLM genera respuesta basada en documentos
  └─ Retorna respuesta natural
    ↓
Si no hay documentos relevantes:
  ├─ Detecta si pregunta es sobre plantas
  └─ Sugiere reformular o usar modo demo
    ↓
Frontend muestra respuesta
```

### 3.3 Comunicación Entre Agentes

**Patrón**: Pipeline secuencial con acumulación de contexto

Cada agente:
1. **Recibe** output del agente anterior (o input inicial)
2. **Procesa** información con su especialización
3. **Añade** información nueva al contexto
4. **Pasa** contexto enriquecido al siguiente agente

**Ventajas del diseño**:
- ✅ Separación clara de responsabilidades
- ✅ Fácil de testear módulo por módulo
- ✅ Escalable (agregar nuevos agentes sin modificar existentes)
- ✅ Mantenible (modificar un agente no afecta otros)

**Ejemplo de acumulación de contexto**:
```python
# Input inicial
input = {"image": "plant.jpg", "question": "¿Cómo la cuido?"}

# Después de Vision Agent
context = {
    "species": "Echeveria",
    "health_score": 6,
    "visual_problems": ["hojas amarillas"]
}

# Después de Knowledge Agent
context = {
    ...context anterior...,
    "documents": [...],
    "knowledge_context": "Las suculentas requieren..."
}

# Después de Analysis Agent
context = {
    ...context anterior...,
    "diagnosis": "Exceso de riego",
    "identified_issues": [...]
}

# Después de Response Agent (LLM)
final_response = {
    ...context anterior...,
    "recommendations": ["Reduce riego...", ...]
}
```

---

## 4. Resultados y Evaluación

### 4.1 Métricas del Sistema

**Rendimiento**:
- Tiempo promedio de análisis: 5-8 segundos
- Precisión identificación especies: ~85% (Plant.id API)
- Documentos indexados: 20+ archivos → ~200+ chunks
- Dimensionalidad embeddings: 384
- Tamaño modelo embeddings: 80 MB

**Capacidad**:
- Chunks indexados en Supabase: ~200+
- Búsqueda vectorial: < 100ms promedio
- Soporte de consultas simultáneas: Múltiples (limitado por APIs externas)

### 4.2 Casos de Prueba

#### Caso 1: Suculenta con Exceso de Riego

**Input**:
- Imagen: Suculenta con hojas amarillas
- Acciones usuario: "Riego cada día"

**Output**:
```json
{
    "species": "Echeveria elegans",
    "health_score": 4,
    "diagnosis": "Exceso de riego detectado",
    "recommendations": [
        "Reduce el riego a cada 10-14 días",
        "Verifica drenaje de maceta",
        "Permite que tierra se seque completamente"
    ]
}
```

**Tiempo**: 6.2 segundos  
**Precisión**: ✅ Diagnóstico correcto

#### Caso 2: Cactus Saludable

**Input**:
- Imagen: Cactus verde saludable
- Acciones usuario: "Riego cada 2 semanas"

**Output**:
```json
{
    "species": "Mammillaria",
    "health_score": 9,
    "diagnosis": "Estado excelente",
    "recommendations": [
        "Mantén el mismo régimen de riego",
        "Asegura buena iluminación",
        "Continúa con cuidados actuales"
    ]
}
```

**Tiempo**: 5.8 segundos  
**Precisión**: ✅ Evaluación correcta

#### Caso 3: Pregunta sin Imagen

**Input**:
- Pregunta: "¿Cómo cuido una suculenta?"

**Output**:
```
Las suculentas son plantas que almacenan agua en sus hojas y tallos.
Requieren poco riego, aproximadamente cada 10-14 días. Prefieren luz
indirecta brillante. El exceso de riego puede causar pudrición de raíces.
```

**Tiempo**: 2.1 segundos  
**Precisión**: ✅ Respuesta relevante y completa

### 4.3 Cumplimiento de Requisitos

✅ **Todos los componentes mínimos implementados**:

1. ✅ **Fuente de datos**: 20+ documentos sobre cuidado de plantas
2. ✅ **Extracción**: Módulo `src/extraccion.py` para leer documentos
3. ✅ **Segmentación (chunks)**: Módulo `src/chunking.py` (400 chars, overlap 50)
4. ✅ **Embeddings**: Módulo `src/embeddings.py` usando sentence-transformers
5. ✅ **Similitud**: Módulo `src/similitud.py` con similitud del coseno
6. ✅ **Base de datos vectorial**: Supabase + pgvector (`src/vector_db.py`)
7. ✅ **Arquitectura multiagente en LangChain**: 4 agentes coordinados
8. ✅ **Interfaz**: Frontend web interactivo (HTML/CSS/JS)
9. ✅ **Repositorio GitHub**: Código organizado y documentado

**Verificación detallada**: `docs/CUMPLIMIENTO_REQUISITOS.md`

### 4.4 Aprendizajes del Equipo

#### Técnicos

1. **Embeddings vectoriales**:
   - Comprensión de cómo el texto se convierte en números
   - Importancia de la normalización para eficiencia
   - Trade-offs entre dimensiones y velocidad

2. **Búsqueda semántica**:
   - Ventajas sobre búsqueda por palabras clave
   - Cómo funciona la similitud del coseno
   - Optimización con índices vectoriales

3. **Arquitecturas multiagente**:
   - Diseño de agentes especializados
   - Orquestación con LangChain
   - Comunicación entre agentes

4. **Integración de APIs**:
   - Uso de Plant.id para identificación
   - Integración con Gemini Vision
   - Manejo de errores y fallbacks

5. **Bases de datos vectoriales**:
   - Configuración de pgvector en Supabase
   - Optimización de índices IVFFlat
   - Funciones SQL para búsqueda vectorial

#### Conceptuales

1. **RAG (Retrieval-Augmented Generation)**:
   - Importancia del chunking en calidad de resultados
   - Balance entre tamaño de chunk y contexto
   - Cómo los embeddings mejoran la recuperación

2. **Trade-offs en modelos**:
   - Precisión vs velocidad en embeddings
   - Costo vs calidad en LLMs
   - Local vs cloud en procesamiento

3. **Diseño de prompts**:
   - Estructura de prompts para LLMs
   - Importancia del contexto
   - Iteración para mejorar resultados

4. **Sistemas robustos**:
   - Importancia de fallbacks
   - Manejo de errores graceful
   - Degradación elegante cuando APIs fallan

#### Desafíos Superados

1. **Configuración de pgvector**:
   - Creación de función SQL personalizada
   - Optimización de índices para búsqueda rápida
   - Conversión de arrays numpy a vectores PostgreSQL

2. **Integración LangChain**:
   - Configuración correcta de AgentExecutor
   - Creación de Tools especializados
   - Manejo de memoria conversacional

3. **Manejo de imágenes**:
   - Codificación base64 para APIs
   - Almacenamiento temporal de archivos
   - Validación de formatos

4. **Fallbacks robustos**:
   - Cadena de fallback: Gemini → Ollama → Documentos → Demo
   - Detección de disponibilidad de servicios
   - Respuestas útiles incluso sin LLM

---

## 5. Limitaciones y Trabajo Futuro

### 5.1 Limitaciones Actuales

1. **Base de conocimiento limitada**:
   - Solo 20+ documentos
   - Cobertura limitada de especies
   - **Solución futura**: Agregar 100+ documentos especializados

2. **Sin persistencia de historial**:
   - Análisis no se guardan entre sesiones
   - No hay seguimiento de evolución de plantas
   - **Solución futura**: Base de datos de usuarios y análisis

3. **API rate limits**:
   - Gemini: 15 requests/minuto (tier gratuito)
   - Plant.id: 100 requests/mes (tier gratuito)
   - **Solución futura**: Caché de resultados + tier pago

4. **Solo análisis reactivo**:
   - No hay seguimiento proactivo
   - No hay notificaciones programadas
   - **Solución futura**: Sistema de recordatorios y seguimiento

5. **Precisión de identificación**:
   - Depende de calidad de imagen
   - Especies raras pueden no identificarse
   - **Solución futura**: Ensamble de múltiples APIs

### 5.2 Mejoras Técnicas Futuras

1. **Ampliar Base de Conocimiento**:
   - Agregar 100+ documentos sobre especies específicas
   - Incluir PDFs de libros de botánica
   - Scrapers web para foros especializados
   - Validación y curación de contenido

2. **Mejorar Precisión**:
   - Fine-tuning de embeddings en datos de plantas
   - Ensamble de múltiples APIs de identificación
   - Validación cruzada de diagnósticos
   - Machine learning para mejorar scores

3. **Optimizar Rendimiento**:
   - Caché de embeddings generados
   - Lazy loading de modelos
   - CDN para imágenes
   - Compresión de vectores

4. **Mejorar LLM**:
   - Fine-tuning en datos de plantas
   - Prompts más estructurados
   - Validación de respuestas generadas
   - Reducción de alucinaciones

### 5.3 Nuevas Funcionalidades

1. **Historial y Seguimiento**:
   - Guardar análisis previos por usuario
   - Gráficas de evolución de salud
   - Comparación temporal
   - Alertas de deterioro

2. **Comunidad**:
   - Foro de usuarios
   - Compartir fotos y consejos
   - Sistema de reputación
   - Expertos verificados

3. **Gamificación**:
   - Logros por mantener plantas saludables
   - Colección de especies identificadas
   - Retos mensuales
   - Ranking de usuarios

4. **Integraciones**:
   - Conexión con viveros
   - Recomendaciones de productos
   - Geolocalización de tiendas
   - Calendario de cuidados

### 5.4 Expansión de Agentes

1. **Agente de Prevención**:
   - Predicción de problemas futuros
   - Alertas proactivas
   - Recomendaciones preventivas

2. **Agente de Aprendizaje**:
   - Aprende de feedback del usuario
   - Mejora diagnósticos con uso
   - Personalización por usuario

3. **Agente Social**:
   - Busca soluciones en comunidad
   - Conecta con expertos
   - Recomendaciones basadas en casos similares

---

## 6. Conclusiones

### 6.1 Logros Principales

PlantCare AI demuestra exitosamente la aplicación de conceptos fundamentales de Inteligencia Artificial en un problema real y tangible:

1. ✅ **Manejo de datos**: Extracción y procesamiento de 20+ documentos
2. ✅ **Segmentación**: Chunking eficiente con overlap para mantener contexto
3. ✅ **Embeddings**: Conversión de texto a vectores de 384 dimensiones
4. ✅ **Similitud**: Búsqueda semántica usando similitud del coseno
5. ✅ **Base de datos vectorial**: Supabase + pgvector para almacenamiento y búsqueda
6. ✅ **Extracción con APIs**: Plant.id y Gemini Vision para análisis de imágenes
7. ✅ **Arquitectura multiagente**: 4 agentes coordinados con LangChain
8. ✅ **Interfaz interactiva**: Frontend web moderno y funcional

### 6.2 Impacto del Proyecto

El proyecto no solo cumple con todos los requisitos académicos, sino que produce una herramienta útil con potencial de impacto real:

- **Democratización del conocimiento**: Hace accesible información especializada
- **Ayuda inmediata**: Respuestas en segundos sin buscar en múltiples fuentes
- **Educación**: Enseña conceptos de IA de forma práctica
- **Base para expansión**: Arquitectura escalable para futuras mejoras

### 6.3 Lecciones Aprendidas

1. **Arquitecturas modulares**: Separación de responsabilidades facilita mantenimiento
2. **Fallbacks robustos**: Sistemas deben funcionar incluso cuando componentes fallan
3. **Iteración en prompts**: Mejorar prompts de LLMs requiere experimentación
4. **Búsqueda semántica**: Embeddings superan búsqueda por palabras clave
5. **APIs gratuitas**: Permiten prototipado rápido pero tienen limitaciones

### 6.4 Mensaje Final

La Inteligencia Artificial no es solo algoritmos complejos, sino herramientas que, bien aplicadas, pueden:

- **Democratizar conocimiento especializado**
- **Mejorar la vida cotidiana de las personas**
- **Resolver problemas reales de forma accesible**
- **Servir como base para sistemas más avanzados**

PlantCare AI es un ejemplo de cómo conceptos fundamentales de IA pueden combinarse para crear soluciones prácticas y útiles.

---

## 7. Referencias y Recursos

### 7.1 Documentación Técnica

1. **Sentence-Transformers**: 
   - Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks
   - https://www.sbert.net/

2. **pgvector**: 
   - Extensión de PostgreSQL para búsqueda vectorial
   - https://github.com/pgvector/pgvector

3. **LangChain**: 
   - Framework para aplicaciones con LLMs
   - https://python.langchain.com/

4. **Google Gemini**: 
   - Documentación de API multimodal
   - https://ai.google.dev/docs

5. **Plant.id API**: 
   - Servicio de identificación de plantas
   - https://plant.id/

6. **Supabase**: 
   - PostgreSQL como servicio con pgvector
   - https://supabase.com/

7. **Ollama**: 
   - Framework para ejecutar LLMs localmente
   - https://ollama.ai/

### 7.2 Código y Repositorios

- **Repositorio del proyecto**: https://github.com/tomasmejiag0/Plant-Care
- **Documentación completa**: `plant-care-ai-backend/README.md`
- **Cumplimiento de requisitos**: `plant-care-ai-backend/docs/CUMPLIMIENTO_REQUISITOS.md`

### 7.3 Herramientas Utilizadas

- **Backend**: FastAPI, Python 3.11+
- **IA**: LangChain, sentence-transformers, Ollama
- **Base de Datos**: Supabase (PostgreSQL + pgvector)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **APIs Externas**: Google Gemini, Plant.id

---

**Documento preparado por**: Tomas Mejia - Johan Gomez  
**Fecha**: Noviembre 2025  
**Versión**: 2.0  
**Última actualización**: Noviembre 2025
