# 🌱 PlantCare AI - Guía de Exposición
## Proyecto Final - Introducción a la Inteligencia Artificial

---

## 📋 Índice de Presentación (15 minutos)

### **Persona 1: Arquitectura y Fundamentos (7.5 min)**
1. Introducción al proyecto (1 min)
2. Arquitectura Multi-Agente (2 min)
3. Componentes fundamentales: Embeddings y Supabase (2 min)
4. Flujo de datos y conexiones (2.5 min)

### **Persona 2: Implementación y Demostración (7.5 min)**
5. LangChain y orquestación (2 min)
6. Ejemplos de código clave (3 min)
7. Demostración práctica (2 min)
8. Conclusiones (0.5 min)

---

## 🎯 Puntos Clave a Destacar

### ✅ Componentes Mínimos Cumplidos:
1. ✅ **Fuente de datos**: Documentos de plantas en Supabase
2. ✅ **Extracción**: APIs (Plant.id, Gemini Vision)
3. ✅ **Segmentación (chunks)**: Texto dividido en fragmentos
4. ✅ **Embeddings y similitud**: sentence-transformers + pgvector
5. ✅ **Base de datos vectorial**: Supabase con pgvector
6. ✅ **Arquitectura multiagente en LangChain**: 4 agentes coordinados
7. ✅ **Interfaz**: Frontend web interactivo

---

## 🏗️ ARQUITECTURA MULTI-AGENTE

### Diagrama de Flujo Visual

```
┌─────────────────────────────────────────────────────────────┐
│                    USUARIO (Imagen + Pregunta)              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              AGENTE ORQUESTADOR (ResponseAgent)              │
│              Usa LangChain AgentExecutor                     │
└──────┬──────────────┬──────────────┬──────────────┬────────┘
       │              │              │              │
       ▼              ▼              ▼              ▼
┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────────┐
│ AGENTE   │  │   AGENTE     │  │ AGENTE   │  │   LLM        │
│ VISIÓN   │  │ CONOCIMIENTO │  │ ANÁLISIS │  │ (Gemini/     │
│          │  │              │  │          │  │  Ollama)     │
└────┬─────┘  └──────┬───────┘  └────┬─────┘  └──────┬──────┘
     │                │                │                │
     │                │                │                │
     ▼                ▼                ▼                ▼
┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────────┐
│ Plant.id │  │  SUPABASE    │  │ Reglas   │  │ Generación   │
│ API      │  │  (pgvector)  │  │ Lógica   │  │ Respuesta    │
│ Gemini   │  │  Embeddings   │  │          │  │ Final        │
│ Vision   │  │  Búsqueda    │  │          │  │              │
└──────────┘  └──────────────┘  └──────────┘  └──────────────┘
```

---

## 🤖 AGENTES Y SUS RESPONSABILIDADES

### 1. **AGENTE DE VISIÓN** (`agente_vision.py`)
**Responsabilidad**: Analizar imágenes de plantas

**Flujo**:
1. Recibe imagen de la planta
2. **Plant.id API** → Identifica especie + probabilidad
3. **Gemini Vision** → Analiza salud visual (manchas, color, plagas)
4. Retorna: especie, estado de salud, problemas visuales

**Código clave a mostrar**:
```python
def identify_plant_species(self, image_path: str):
    # 1. Plant.id API
    response = requests.post(url, json=data, headers=headers)
    species = result['suggestions'][0]['plant_name']
    
    # 2. Gemini Vision (fallback)
    response = self.gemini_model.generate_content([prompt, img])
    return species_info
```

---

### 2. **AGENTE DE CONOCIMIENTO** (`agente_conocimiento.py`)
**Responsabilidad**: Buscar información relevante en base vectorial

**Flujo**:
1. Recibe: especie identificada + problemas visuales
2. **Genera embedding** de la consulta usando `sentence-transformers`
3. **Búsqueda vectorial** en Supabase usando `pgvector`
4. Retorna: Top 5 documentos más relevantes

**Código clave a mostrar**:
```python
def search_knowledge(self, query, species, problems):
    # 1. Generar embedding
    query_embedding = self.embedder.encode(query)
    
    # 2. Búsqueda vectorial en Supabase
    results = supabase.rpc('match_plant_documents', {
        'query_embedding': query_embedding.tolist(),
        'match_threshold': 0.3,
        'match_count': 5
    }).execute()
    
    return documents
```

**Conceptos clave**:
- **Embeddings**: Representación numérica del texto (384 dimensiones)
- **Similitud del coseno**: Compara embeddings para encontrar documentos similares
- **pgvector**: Extensión de PostgreSQL para búsqueda vectorial

---

### 3. **AGENTE DE ANÁLISIS** (`agente_analisis.py`)
**Responsabilidad**: Diagnosticar problemas y calcular salud

**Flujo**:
1. Combina: datos visuales + conocimiento recuperado + acciones del usuario
2. Aplica reglas de diagnóstico (exceso de riego, falta de luz, etc.)
3. Calcula puntuación de salud (1-10)
4. Genera diagnóstico estructurado

**Código clave a mostrar**:
```python
def execute(self, vision_result, knowledge_result, user_actions):
    # Análisis de problemas
    issues = []
    if "riego cada día" in user_actions.lower():
        issues.append({'type': 'exceso_de_riego', 'severity': 7})
    
    # Cálculo de salud
    health_score = vision_score - (problemas × 0.5) - (severidad × 0.3)
    
    return {
        'health_score': health_score,
        'diagnosis': diagnosis,
        'identified_issues': issues
    }
```

---

### 4. **AGENTE DE RESPUESTA** (`agente_respuesta.py` / `agente_respuesta_langchain.py`)
**Responsabilidad**: Orquestar todos los agentes y generar respuesta final

**Flujo con LangChain**:
1. Crea **Tools** para cada agente
2. Usa **AgentExecutor** de LangChain para coordinar
3. **LLM (Gemini/Ollama)** genera recomendaciones finales
4. Combina toda la información en respuesta estructurada

**Código clave a mostrar**:
```python
# LangChain AgentExecutor
tools = [
    Tool(name="vision_analysis", func=vision_tool, ...),
    Tool(name="knowledge_search", func=knowledge_tool, ...),
    Tool(name="plant_analysis", func=analysis_tool, ...)
]

agent = create_structured_chat_agent(llm=self.llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory)

# Ejecutar
result = agent_executor.invoke({"input": "Analiza esta planta..."})
```

---

## 🔗 CONEXIÓN CON SUPABASE

### Base de Datos Vectorial

**Estructura**:
```sql
CREATE TABLE plant_documents (
    id BIGSERIAL PRIMARY KEY,
    chunk_id TEXT NOT NULL,
    text TEXT NOT NULL,
    embedding vector(384),  -- pgvector
    source_file TEXT,
    created_at TIMESTAMP
);
```

**Flujo de búsqueda**:
1. Usuario pregunta: "¿Cómo cuido una suculenta?"
2. Sistema genera embedding de la pregunta
3. Búsqueda en Supabase usando similitud del coseno
4. Retorna documentos más relevantes (top 5)

**Código a mostrar**:
```python
# Generar embedding
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode("¿Cómo cuido una suculenta?")

# Búsqueda en Supabase
results = supabase.rpc('match_plant_documents', {
    'query_embedding': embedding.tolist(),
    'match_threshold': 0.3,
    'match_count': 5
}).execute()
```

---

## 🧠 LLM (Large Language Model)

### ¿Qué es un LLM?
Modelo de lenguaje que genera texto basado en contexto.

### ¿Cómo lo usamos?
1. **Gemini (Google)**: Principal, para análisis y recomendaciones
2. **Ollama (Local)**: Fallback cuando Gemini no está disponible
3. **Sin LLM**: Usa solo documentos de Supabase

### Integración con LangChain:
```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)

# Generar recomendaciones
prompt = f"""
Eres un experto en plantas. Basándote en:
- Especie: {species}
- Diagnóstico: {diagnosis}
- Conocimiento: {context}

Genera 3-5 recomendaciones específicas.
"""

response = llm.generate_content(prompt)
```

---

## 📝 SCRIPT DE PRESENTACIÓN

### **PERSONA 1 (7.5 minutos)**

#### **1. Introducción (1 min)**
"Hola, somos [Nombres]. Hoy presentamos **PlantCare AI**, un sistema de inteligencia artificial que ayuda a cuidar plantas mediante análisis de imágenes y conocimiento especializado."

#### **2. Arquitectura Multi-Agente (2 min)**
"El sistema usa una **arquitectura de 4 agentes especializados** coordinados con LangChain:

- **Agente de Visión**: Analiza imágenes usando Plant.id API y Gemini Vision
- **Agente de Conocimiento**: Busca información en nuestra base de datos vectorial
- **Agente de Análisis**: Diagnostica problemas y calcula salud
- **Agente de Respuesta**: Orquesta todo y genera la respuesta final

*[Mostrar diagrama de flujo]*"

#### **3. Embeddings y Supabase (2 min)**
"Para buscar información relevante, usamos **embeddings** - representaciones numéricas del texto. 

*[Mostrar código de embeddings]*

Convertimos las preguntas del usuario en vectores de 384 dimensiones usando `sentence-transformers`. Luego buscamos en **Supabase con pgvector** documentos similares usando similitud del coseno.

*[Mostrar código de búsqueda en Supabase]*

Esto nos permite encontrar información relevante incluso si el usuario no usa las palabras exactas de nuestros documentos."

#### **4. Flujo de Datos (2.5 min)**
"Cuando un usuario sube una imagen:

1. El **Agente de Visión** identifica la especie y analiza la salud
2. El **Agente de Conocimiento** busca información relevante en Supabase
3. El **Agente de Análisis** combina todo y genera un diagnóstico
4. El **LLM** (Gemini u Ollama) genera recomendaciones personalizadas

*[Mostrar código del flujo en agente_respuesta.py]*

Todo esto se coordina usando **LangChain AgentExecutor**, que permite que los agentes trabajen juntos de forma inteligente."

---

### **PERSONA 2 (7.5 minutos)**

#### **5. LangChain y Orquestación (2 min)**
"LangChain nos permite orquestar los agentes de forma elegante. Creamos **Tools** para cada agente y usamos **AgentExecutor** para coordinar su ejecución.

*[Mostrar código de LangChain]*

El sistema decide automáticamente qué agente usar en cada momento, creando un flujo inteligente y dinámico."

#### **6. Ejemplos de Código Clave (3 min)**

**Ejemplo 1: Agente de Visión**
*[Abrir `agente_vision.py`]*
"Este agente combina dos APIs: Plant.id para identificación y Gemini Vision para análisis de salud. Si una falla, usa la otra como respaldo."

**Ejemplo 2: Búsqueda Vectorial**
*[Abrir `agente_conocimiento.py`]*
"Aquí vemos cómo generamos embeddings y buscamos en Supabase. El sistema encuentra documentos relevantes incluso con consultas diferentes."

**Ejemplo 3: LangChain AgentExecutor**
*[Abrir `agente_respuesta_langchain.py`]*
"Este es el corazón del sistema. Coordina todos los agentes usando LangChain, permitiendo que trabajen juntos de forma inteligente."

#### **7. Demostración Práctica (2 min)**
*[Abrir terminal y mostrar logs del backend]*

"Cuando procesamos una imagen, vemos en los logs cómo cada agente se ejecuta:
- Vision Agent identifica la planta
- Knowledge Agent busca información
- Analysis Agent diagnostica
- Response Agent genera recomendaciones

*[Mostrar ejemplo de respuesta completa]*"

#### **8. Conclusiones (0.5 min)**
"El proyecto demuestra la integración exitosa de:
- ✅ Arquitectura multiagente con LangChain
- ✅ Embeddings y búsqueda vectorial
- ✅ Integración con LLMs (Gemini/Ollama)
- ✅ Base de datos vectorial (Supabase + pgvector)

Gracias por su atención. ¿Preguntas?"

---

## 💻 CÓDIGO CLAVE A MOSTRAR

### 1. **Generación de Embeddings**
```python
# src/agentes/agente_conocimiento.py (líneas 30-40)
from embeddings import EmbeddingGenerator

embedder = EmbeddingGenerator()
query_embedding = embedder.generate_embedding("¿Cómo cuido una suculenta?")
# Retorna: array de 384 números (vector)
```

### 2. **Búsqueda en Supabase**
```python
# src/agentes/agente_conocimiento.py (líneas 60-80)
results = supabase.rpc('match_plant_documents', {
    'query_embedding': query_embedding.tolist(),
    'match_threshold': 0.3,
    'match_count': 5
}).execute()

# Retorna documentos ordenados por relevancia (similitud del coseno)
```

### 3. **LangChain AgentExecutor**
```python
# src/agentes/agente_respuesta_langchain.py (líneas 175-250)
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.tools import Tool

tools = [
    Tool(name="vision_analysis", func=vision_tool, ...),
    Tool(name="knowledge_search", func=knowledge_tool, ...),
    Tool(name="plant_analysis", func=analysis_tool, ...)
]

agent = create_structured_chat_agent(llm=llm, tools=tools, prompt=prompt)
executor = AgentExecutor(agent=agent, tools=tools, memory=memory)
result = executor.invoke({"input": "Analiza esta planta..."})
```

### 4. **Uso del LLM**
```python
# src/agentes/agente_respuesta.py (líneas 110-140)
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
response = llm.generate_content(prompt)
recommendations = parse_recommendations(response.text)
```

---

## 🎨 DIAGRAMA PARA MOSTRAR EN PANTALLA

```
┌─────────────────────────────────────────────────────────┐
│                    PLANTCARE AI                         │
│         Sistema Multi-Agente con LangChain              │
└─────────────────────────────────────────────────────────┘

                    [Imagen de Planta]
                           │
                           ▼
        ┌──────────────────────────────────┐
        │   RESPONSE AGENT (LangChain)     │
        │   AgentExecutor + Tools          │
        └───────────┬──────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
    ┌──────┐   ┌────────┐   ┌──────┐
    │VISION│   │KNOWLEDGE│   │ANALYSIS│
    └──┬──┘   └────┬───┘   └───┬──┘
       │           │           │
       ▼           ▼           ▼
  [Plant.id]  [Supabase]   [Reglas]
  [Gemini]    [pgvector]   [Lógica]
  Vision      [Embeddings]  [Cálculos]
                    │
                    ▼
            ┌──────────────┐
            │  LLM (Gemini)│
            │  / Ollama    │
            └──────┬───────┘
                   │
                   ▼
            [Recomendaciones]
```

---

## 📊 MÉTRICAS Y RESULTADOS

### Lo que funciona bien:
- ✅ Identificación de especies (Plant.id API)
- ✅ Búsqueda vectorial precisa (Supabase + pgvector)
- ✅ Diagnóstico automático de problemas
- ✅ Recomendaciones personalizadas con LLM

### Fallbacks implementados:
- Gemini → Ollama (local) → Documentos → Demo Mode
- Plant.id → Gemini Vision
- Sistema funciona incluso sin APIs externas

---

## 🔑 CONCEPTOS CLAVE PARA EXPLICAR

1. **Embeddings**: "Convertimos texto en números que capturan su significado"
2. **Similitud del coseno**: "Comparamos vectores para encontrar documentos similares"
3. **pgvector**: "Extensión de PostgreSQL para búsqueda vectorial eficiente"
4. **LangChain**: "Framework que coordina agentes y LLMs"
5. **AgentExecutor**: "Orquestador que decide qué agente usar y cuándo"
6. **RAG (Retrieval-Augmented Generation)**: "Buscamos información relevante antes de generar respuesta"

---

## 📁 ARCHIVOS CLAVE A MENCIONAR

1. `src/agentes/agente_vision.py` - Análisis de imágenes
2. `src/agentes/agente_conocimiento.py` - Búsqueda vectorial
3. `src/agentes/agente_analisis.py` - Diagnóstico
4. `src/agentes/agente_respuesta_langchain.py` - Orquestación con LangChain
5. `src/embeddings.py` - Generación de embeddings
6. `src/vector_db.py` - Conexión con Supabase

---

## ✅ CHECKLIST PRE-EXPOSICIÓN

- [ ] Tener diagrama de flujo visible
- [ ] Abrir archivos de código clave
- [ ] Tener terminal con backend corriendo
- [ ] Preparar ejemplo de imagen de planta
- [ ] Tener logs del backend visibles
- [ ] Probar que Supabase responde
- [ ] Verificar que LangChain funciona

---

## 🎯 MENSAJE FINAL

"Este proyecto demuestra cómo los conceptos fundamentales de IA - embeddings, búsqueda vectorial, y arquitectura multiagente - se combinan para crear un sistema práctico y funcional que ayuda a las personas a cuidar sus plantas de forma inteligente."

---

**¡Éxito en la exposición! 🌱**

