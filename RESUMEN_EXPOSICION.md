# 🌱 PlantCare AI - Script de Exposición Completo
## Proyecto Final - Introducción a la Inteligencia Artificial

## ⏱️ TIMING: 15 minutos (7.5 min cada uno)

---

## 👤 PERSONA 1: Fundamentos y Arquitectura (7.5 minutos)

### 1️⃣ Introducción (1 min)

**Decir exactamente:**

"Buenos días/tardes. Somos [Nombres] y hoy presentamos **PlantCare AI**, un sistema de inteligencia artificial diseñado para ayudar a las personas a cuidar sus plantas de forma inteligente.

Este proyecto integra los conceptos fundamentales de IA que aprendimos en el curso: **embeddings y similitud**, **bases de datos vectoriales**, **extracción de datos con APIs**, y una **arquitectura multiagente construida con LangChain**.

El sistema permite a los usuarios subir una imagen de su planta y recibir un análisis completo que incluye identificación de la especie, diagnóstico de salud, y recomendaciones personalizadas basadas en conocimiento especializado."

---

### 2️⃣ Arquitectura Multi-Agente (2 min)

**Decir exactamente:**

"El corazón de nuestro sistema es una **arquitectura de 4 agentes especializados** que trabajan juntos para proporcionar análisis completos.

*[Mostrar diagrama de flujo]*

Primero, tenemos el **Agente de Visión**. Este agente se encarga de analizar la imagen de la planta. Utiliza dos APIs: Plant.id para identificar la especie de la planta, y Gemini Vision para analizar el estado de salud visual, detectando problemas como manchas, hojas amarillas, o plagas.

Segundo, el **Agente de Conocimiento**. Este agente busca información relevante en nuestra base de datos vectorial. Cuando el usuario pregunta algo como '¿Cómo cuido una suculenta?', este agente genera un embedding de la pregunta y busca documentos similares en Supabase usando búsqueda vectorial.

Tercero, el **Agente de Análisis**. Este agente combina toda la información: los datos visuales del Agente de Visión, el conocimiento recuperado del Agente de Conocimiento, y las acciones que el usuario ha mencionado. Aplica reglas de diagnóstico para identificar problemas específicos como exceso de riego o falta de luz, y calcula una puntuación de salud del 1 al 10.

Y finalmente, el **Agente de Respuesta**, que actúa como orquestador. Este agente coordina a todos los demás usando LangChain AgentExecutor, y utiliza un LLM - en nuestro caso Gemini u Ollama local - para generar recomendaciones finales personalizadas y en lenguaje natural.

¿Por qué usar múltiples agentes en lugar de uno solo? Porque cada agente tiene una responsabilidad específica y clara. Esto hace que el sistema sea más modular, fácil de mantener, y permite que cada agente se especialice en su tarea."

---

### 3️⃣ Embeddings y Supabase (2 min)

**Decir exactamente:**

"Ahora voy a explicar cómo funciona la búsqueda de información en nuestro sistema, que es uno de los componentes más importantes.

*[Abrir `src/embeddings.py`]*

Primero, los **embeddings**. Un embedding es una representación numérica del texto que captura su significado semántico. En nuestro código, usamos el modelo `sentence-transformers/all-MiniLM-L6-v2`, que convierte cualquier texto en un vector de 384 números.

*[Mostrar código]*

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode("¿Cómo cuido una suculenta?")
# Resultado: array de 384 números como [0.23, -0.45, 0.12, ...]
```

Estos 384 números no son aleatorios. Cada posición en el vector captura algún aspecto del significado del texto. Textos similares tendrán vectores similares, y textos diferentes tendrán vectores diferentes.

*[Abrir `src/agentes/agente_conocimiento.py` o `src/vector_db.py`]*

Ahora, para buscar información relevante, usamos **Supabase con pgvector**. Supabase es PostgreSQL en la nube, y pgvector es una extensión que permite almacenar y buscar vectores eficientemente.

*[Mostrar código]*

```python
# Generar embedding de la consulta
query_embedding = self.embedding_generator.generate_embedding("¿Cómo cuido una suculenta?")

# Buscar en Supabase usando pgvector
results = supabase.rpc('match_plant_documents', {
    'query_embedding': query_embedding.tolist(),  # Convertir a lista
    'match_threshold': 0.3,  # Umbral de similitud mínimo
    'match_count': 5  # Top 5 documentos
})
```

La función `match_plant_documents` en Supabase calcula la **similitud del coseno** entre el embedding de la consulta y todos los embeddings almacenados. La similitud del coseno mide qué tan similares son dos vectores, retornando un valor entre -1 y 1, donde 1 significa idénticos y -1 significa opuestos.

Esto nos permite encontrar documentos relevantes incluso si el usuario no usa las palabras exactas que están en nuestros documentos. Por ejemplo, si el usuario pregunta 'riego de suculentas' y nuestro documento dice 'cuidado de suculentas con agua', el sistema los encontrará como similares porque tienen embeddings cercanos."

---

### 4️⃣ Flujo Completo (2.5 min)

**Decir exactamente:**

"Ahora voy a explicar el flujo completo de cómo todos estos componentes trabajan juntos cuando un usuario sube una imagen.

*[Mostrar diagrama de flujo paso a paso]*

**Paso 1**: El usuario sube una imagen de su planta y opcionalmente escribe una pregunta o preocupación, como 'le arranqué una hoja sin querer'.

**Paso 2**: El **Agente de Visión** se ejecuta. Primero intenta identificar la especie usando Plant.id API. Si eso falla o la confianza es muy baja, usa Gemini Vision como respaldo. Luego analiza la salud visual de la planta, detectando problemas como hojas amarillas o manchas.

**Paso 3**: Con la especie identificada y los problemas visuales detectados, el **Agente de Conocimiento** construye una consulta mejorada. Por ejemplo, si la especie es 'Cestrum nocturnum' y hay problemas de 'hojas amarillas', la consulta sería algo como 'Cestrum nocturnum hojas amarillas cuidado'. Esta consulta se convierte en un embedding y se busca en Supabase, retornando los 5 documentos más relevantes.

**Paso 4**: El **Agente de Análisis** recibe toda esta información: los datos visuales, el conocimiento recuperado, y las acciones del usuario. Aplica reglas de diagnóstico. Por ejemplo, si el usuario dice 'riego cada día' y hay hojas amarillas, identifica 'exceso de riego' con una severidad alta. Calcula una puntuación de salud final considerando el estado visual y los problemas identificados.

**Paso 5**: Finalmente, el **Agente de Respuesta** toma todo este análisis y lo pasa a un LLM - Gemini u Ollama local - junto con el conocimiento relevante. El LLM genera recomendaciones personalizadas y en lenguaje natural. Si el usuario mencionó una preocupación específica, como 'arranqué una hoja', el LLM aborda directamente esa preocupación, tranquilizando al usuario y dando consejos específicos.

Todo este flujo está orquestado por LangChain AgentExecutor, que coordina la ejecución de cada agente de forma inteligente."

---

## 👤 PERSONA 2: Implementación y Demo (7.5 minutos)

### 5️⃣ LangChain y Orquestación (2 min)

**Decir exactamente:**

"Ahora voy a mostrar cómo implementamos la orquestación de agentes usando LangChain.

*[Abrir `src/agentes/agente_respuesta_langchain.py`]*

LangChain es un framework diseñado específicamente para construir aplicaciones con LLMs y agentes. En nuestro caso, usamos **AgentExecutor**, que es el componente que coordina la ejecución de múltiples agentes.

*[Mostrar código de creación de Tools, líneas 137-200 aproximadamente]*

Primero, convertimos cada agente en una **Tool** - una herramienta que el LLM puede usar. Por ejemplo:

```python
def vision_tool(image_path: str, user_context: str) -> str:
    """Herramienta para análisis visual"""
    result = self.vision_agent.execute(image_path, user_context)
    return f"Especie: {result['species']}, Salud: {result['health_score']}/10"

tools = [
    Tool(name="vision_analysis", func=vision_tool, 
         description="Analiza imágenes de plantas"),
    Tool(name="knowledge_search", func=knowledge_tool,
         description="Busca información en base de conocimiento"),
    Tool(name="plant_analysis", func=analysis_tool,
         description="Realiza análisis y diagnóstico")
]
```

*[Mostrar código de AgentExecutor, líneas 207-250 aproximadamente]*

Luego, creamos el **AgentExecutor**:

```python
from langchain.agents import AgentExecutor, create_structured_chat_agent

agent = create_structured_chat_agent(
    llm=self.llm,  # Gemini u Ollama
    tools=self.tools,  # Las 3 herramientas
    prompt=prompt  # Instrucciones para el agente
)

executor = AgentExecutor(
    agent=agent,
    tools=self.tools,
    memory=self.memory,  # Memoria de conversación
    verbose=True
)
```

El AgentExecutor es inteligente: el LLM decide qué herramienta usar y en qué orden, basándose en el contexto. Por ejemplo, si el usuario pregunta sobre una planta, el LLM primero usará `vision_analysis`, luego `knowledge_search`, luego `plant_analysis`, y finalmente generará la respuesta.

Esto es diferente a una implementación manual donde nosotros controlamos el flujo explícitamente. Con LangChain, el LLM puede tomar decisiones inteligentes sobre cómo orquestar los agentes."

---

### 6️⃣ LLM y Generación de Respuestas (2 min)

**Decir exactamente:**

"Ahora voy a explicar cómo usamos los LLMs - Large Language Models - para generar respuestas.

*[Abrir `src/agentes/agente_respuesta.py`, sección de generate_recommendations]*

Un **LLM** es un modelo de lenguaje que puede generar texto basado en contexto. En nuestro sistema, usamos principalmente **Google Gemini**, pero también tenemos un fallback a **Ollama** que corre localmente.

*[Mostrar código]*

```python
from langchain_google_genai import ChatGoogleGenerativeAI

# Configurar Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7  # Controla la creatividad
)

# Generar recomendaciones
prompt = f"""Eres un experto en plantas. Basándote en:
- Especie: {species}
- Diagnóstico: {diagnosis}
- Conocimiento: {context}
- Pregunta del usuario: {user_question}

Genera 3-5 recomendaciones específicas."""
```

El LLM recibe todo este contexto y genera recomendaciones en lenguaje natural. Si el usuario tiene una preocupación específica, como 'arranqué una hoja', el LLM la aborda directamente.

*[Mostrar código de fallback]*

```python
# Si Gemini falla, usar Ollama local
if not self.llm:
    from src.local_llm import get_local_llm
    local_llm = get_local_llm()  # Ollama con llama3.2
    response = local_llm.generate(prompt)
```

¿Por qué tener múltiples fallbacks? Porque las APIs externas pueden fallar o agotar su cuota. Nuestro sistema tiene esta cadena: Gemini → Ollama local → Solo documentos → Modo demo. Esto asegura que el sistema siempre funcione, incluso sin conexión a internet o sin APIs externas."

---

### 7️⃣ Ejemplos de Código Clave (3 min)

**Decir exactamente:**

"Ahora voy a mostrar ejemplos específicos de código de cada agente para que vean cómo está implementado.

*[Abrir `src/agentes/agente_vision.py`, función identify_plant_species]*

**Primer ejemplo: Agente de Visión**

Aquí vemos cómo el agente identifica la especie de la planta. Primero intenta con Plant.id API:

```python
def identify_plant_species(self, image_path: str):
    # Codificar imagen en base64
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Llamar a Plant.id API
    response = requests.post(
        "https://api.plant.id/v2/identify",
        json={"images": [f"data:image/jpeg;base64,{image_data}"]},
        headers={"Api-Key": self.plant_id_key}
    )
    
    species = response.json()['suggestions'][0]['plant_name']
    probability = response.json()['suggestions'][0]['probability']
    
    return {'species': species, 'probability': probability}
```

Si esto falla, usa Gemini Vision como respaldo. Esto es importante porque garantiza que siempre tengamos una identificación, aunque sea con menor confianza.

*[Abrir `src/agentes/agente_conocimiento.py`, función search_knowledge]*

**Segundo ejemplo: Agente de Conocimiento**

Este es el código que realiza la búsqueda vectorial:

```python
def search_knowledge(self, query: str, species: str, problems: List[str]):
    # 1. Construir consulta mejorada
    enhanced_query = f"{species} {query} problemas: {', '.join(problems)}"
    
    # 2. Generar embedding
    query_embedding = self.embedding_generator.generate_embedding(enhanced_query)
    
    # 3. Buscar en Supabase con pgvector
    results = self.vector_db.search_similar(
        query_embedding, 
        top_k=5, 
        threshold=0.25
    )
    
    return documents  # Ordenados por relevancia
```

La función `search_similar` internamente llama a la función SQL `match_plant_documents` en Supabase, que usa el operador `<=>` de pgvector para calcular la distancia entre vectores. Esto es muy eficiente incluso con miles de documentos.

*[Abrir `src/agentes/agente_respuesta_langchain.py`, sección de _create_agent_executor]*

**Tercer ejemplo: LangChain AgentExecutor**

Este es el código que crea el orquestador:

```python
def _create_agent_executor(self):
    # Crear Tools
    tools = [
        Tool(name="vision_analysis", func=vision_tool, ...),
        Tool(name="knowledge_search", func=knowledge_tool, ...),
        Tool(name="plant_analysis", func=analysis_tool, ...)
    ]
    
    # Crear agente estructurado
    agent = create_structured_chat_agent(
        llm=self.llm,
        tools=tools,
        prompt=prompt
    )
    
    # Crear ejecutor
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=self.memory
    )
    
    return executor
```

El AgentExecutor usa el LLM para decidir qué tool usar. El LLM lee las descripciones de las tools y decide automáticamente el orden de ejecución basándose en el contexto de la conversación."

---

### 8️⃣ Demostración Práctica (1 min)

**Decir exactamente:**

"Ahora voy a mostrar cómo funciona el sistema en tiempo real.

*[Abrir terminal con backend corriendo, mostrar logs]*

Cuando procesamos una imagen, podemos ver en los logs cómo cada agente se ejecuta secuencialmente:

```
🔍 AGENTE DE VISIÓN ejecutando...
  ✓ Plant.id identificó: Cestrum nocturnum (confianza: 32%)
  ✓ Estado de salud: Regular (5/10)

🔍 AGENTE DE CONOCIMIENTO ejecutando...
  Consulta: Cestrum nocturnum ¿Cómo la cuido?
  ✓ Encontrados 5 documentos relevantes

🔬 AGENTE DE ANÁLISIS ejecutando...
  ✓ Diagnóstico: Estado general saludable
  ✓ Problemas identificados: falta_de_luz

💡 Generando recomendaciones...
  ✓ LangChain LLM generó 4 recomendaciones
```

Cada agente pasa su resultado al siguiente, y al final tenemos un análisis completo que incluye la especie identificada, el estado de salud, el diagnóstico, y recomendaciones personalizadas.

El sistema está diseñado para ser robusto: si una API falla, hay un fallback. Si el LLM no está disponible, usa solo los documentos. Esto asegura que siempre podamos dar una respuesta útil al usuario."

---

### 9️⃣ Conclusiones (0.5 min)

**Decir exactamente:**

"Para concluir, nuestro proyecto **PlantCare AI** demuestra la integración exitosa de todos los componentes requeridos:

✅ **Fuente de datos**: Documentos de plantas almacenados en Supabase
✅ **Extracción**: APIs como Plant.id y Gemini Vision para analizar imágenes
✅ **Segmentación**: Texto dividido en chunks para búsqueda eficiente
✅ **Embeddings**: Usando sentence-transformers para convertir texto en vectores
✅ **Similitud**: Búsqueda vectorial con similitud del coseno usando pgvector
✅ **Base de datos vectorial**: Supabase con extensión pgvector
✅ **Arquitectura multiagente**: 4 agentes coordinados con LangChain AgentExecutor
✅ **Interfaz**: Frontend web interactivo

El sistema muestra cómo estos conceptos fundamentales de IA se combinan para crear una aplicación práctica y funcional. Gracias por su atención. ¿Hay alguna pregunta?"

---

## 🎯 PUNTOS CLAVE A RECORDAR

### ✅ Cumplimos todos los requisitos:
1. ✅ Fuente de datos (documentos en Supabase)
2. ✅ Extracción (APIs: Plant.id, Gemini Vision)
3. ✅ Segmentación (chunks de texto)
4. ✅ Embeddings (sentence-transformers)
5. ✅ Similitud (coseno con pgvector)
6. ✅ Base vectorial (Supabase + pgvector)
7. ✅ Arquitectura multiagente (LangChain)
8. ✅ Interfaz (frontend web)

### 🔑 Conceptos técnicos:
- **Embedding**: Texto → Vector numérico (384 dims)
- **Similitud del coseno**: Compara vectores
- **pgvector**: Búsqueda vectorial en PostgreSQL
- **LangChain**: Framework para orquestar agentes
- **AgentExecutor**: Coordina ejecución de agentes
- **RAG**: Retrieval-Augmented Generation

---

## 📊 DIAGRAMA SIMPLIFICADO

```
Usuario → [Imagen + Pregunta]
           │
           ▼
    ┌──────────────┐
    │ ResponseAgent│ ← LangChain AgentExecutor
    │ (Orquestador)│
    └──────┬───────┘
           │
    ┌──────┼──────┬──────┐
    │      │      │      │
    ▼      ▼      ▼      ▼
[Vision] [Know] [Anal] [LLM]
    │      │      │      │
    ▼      ▼      ▼      ▼
[APIs] [Supabase] [Lógica] [Gemini]
         │
         ▼
    [pgvector]
    [Embeddings]
```

---

## 💡 FRASES CLAVE PARA USAR

- "Usamos embeddings para convertir texto en números que capturan su significado"
- "Supabase con pgvector nos permite buscar documentos similares eficientemente"
- "LangChain AgentExecutor coordina los agentes de forma inteligente"
- "El sistema tiene múltiples fallbacks para funcionar sin APIs externas"
- "Cada agente tiene una responsabilidad específica y clara"

---

## 🚀 DEMOSTRACIÓN RÁPIDA

**Si tienen tiempo, mostrar:**
1. Abrir terminal con backend corriendo
2. Mostrar logs cuando se procesa una imagen
3. Explicar cada paso que aparece en los logs
4. Mostrar resultado final formateado

---

**¡Éxito! 🌿**

