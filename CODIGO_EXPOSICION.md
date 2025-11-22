# 💻 Código para Mostrar en la Exposición

## 📁 Archivos Clave a Abrir

1. `src/agentes/agente_vision.py`
2. `src/agentes/agente_conocimiento.py`
3. `src/agentes/agente_analisis.py`
4. `src/agentes/agente_respuesta_langchain.py`
5. `src/embeddings.py`
6. `main.py` (endpoint principal)

---

## 🔍 1. AGENTE DE VISIÓN (agente_vision.py)

### Código a Mostrar - Identificación de Planta

```python
def identify_plant_species(self, image_path: str) -> Optional[Dict]:
    """Identifica la especie usando Plant.id API o Gemini Vision"""
    
    # 1. Intentar con Plant.id API
    if self.plant_id_key:
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        response = requests.post(
            "https://api.plant.id/v2/identify",
            json={"images": [f"data:image/jpeg;base64,{image_data}"]},
            headers={"Api-Key": self.plant_id_key}
        )
        
        result = response.json()
        species = result['suggestions'][0]['plant_name']
        probability = result['suggestions'][0]['probability']
        
        return {'species': species, 'probability': probability}
    
    # 2. Fallback: Gemini Vision
    if self.gemini_model:
        img = Image.open(image_path)
        prompt = "Identifica la especie de esta planta..."
        response = self.gemini_model.generate_content([prompt, img])
        return parse_species(response.text)
```

**Qué explicar:**
- Usa dos APIs diferentes (Plant.id y Gemini Vision)
- Tiene fallback si una falla
- Retorna especie y probabilidad

---

## 🧠 2. AGENTE DE CONOCIMIENTO (agente_conocimiento.py)

### Código a Mostrar - Generación de Embeddings

```python
# src/embeddings.py
from sentence_transformers import SentenceTransformer

class EmbeddingGenerator:
    def __init__(self):
        # Modelo pre-entrenado: 384 dimensiones
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Convierte texto en vector numérico"""
        embedding = self.model.encode(text)
        # Retorna: array de 384 números
        return embedding
```

**Qué explicar:**
- `sentence-transformers` convierte texto en números
- 384 dimensiones capturan el significado
- Mismo modelo para consultas y documentos

### Código a Mostrar - Búsqueda en Supabase

```python
def search_knowledge(self, query: str, species: str, problems: List[str]):
    """Busca información relevante en Supabase"""
    
    # 1. Construir consulta mejorada
    enhanced_query = f"{query} {species} {' '.join(problems)}"
    
    # 2. Generar embedding de la consulta
    query_embedding = self.embedder.generate_embedding(enhanced_query)
    
    # 3. Búsqueda vectorial en Supabase usando pgvector
    results = self.supabase.rpc('match_plant_documents', {
        'query_embedding': query_embedding.tolist(),  # Convertir a lista
        'match_threshold': 0.3,  # Umbral de similitud
        'match_count': 5  # Top 5 documentos
    }).execute()
    
    # 4. Retornar documentos ordenados por relevancia
    documents = []
    for row in results.data:
        documents.append({
            'text': row['text'],
            'relevance_score': row['similarity'],  # Similitud del coseno
            'source': row['source_file']
        })
    
    return documents
```

**Qué explicar:**
- `pgvector` permite búsqueda vectorial en PostgreSQL
- Similitud del coseno compara vectores
- Retorna documentos más relevantes

---

## 🔬 3. AGENTE DE ANÁLISIS (agente_analisis.py)

### Código a Mostrar - Diagnóstico

```python
def execute(self, vision_result, knowledge_result, user_actions: str):
    """Combina información y genera diagnóstico"""
    
    identified_issues = []
    
    # Analizar acciones del usuario
    user_lower = user_actions.lower()
    
    if "riego cada día" in user_lower or "riego diario" in user_lower:
        identified_issues.append({
            'type': 'exceso_de_riego',
            'severity': 7,
            'description': 'Riego excesivo detectado'
        })
    
    if "sin luz" in user_lower or "oscuro" in user_lower:
        identified_issues.append({
            'type': 'falta_de_luz',
            'severity': 6,
            'description': 'Falta de iluminación'
        })
    
    # Calcular puntuación de salud
    visual_score = vision_result.get('health_score', 5)
    problem_penalty = sum(issue['severity'] for issue in identified_issues) * 0.3
    health_score = max(1, min(10, visual_score - problem_penalty))
    
    # Generar diagnóstico
    diagnosis = self._generate_diagnosis(identified_issues, vision_result)
    
    return {
        'health_score': health_score,
        'diagnosis': diagnosis,
        'identified_issues': identified_issues
    }
```

**Qué explicar:**
- Combina datos visuales + conocimiento + acciones del usuario
- Aplica reglas de diagnóstico
- Calcula puntuación de salud

---

## 🎯 4. AGENTE DE RESPUESTA CON LANGCHAIN (agente_respuesta_langchain.py)

### Código a Mostrar - Creación de Tools

```python
def _create_tools(self):
    """Crea herramientas (Tools) para LangChain"""
    
    def vision_tool(image_path: str, user_actions: str) -> str:
        """Herramienta para análisis visual"""
        result = self.vision_agent.execute(image_path, user_actions)
        return f"Especie: {result['species']}, Salud: {result['health_score']}/10"
    
    def knowledge_tool(query: str, species: str) -> str:
        """Herramienta para búsqueda de conocimiento"""
        documents = self.knowledge_agent.search_knowledge(query, species)
        return f"Encontré {len(documents)} documentos relevantes"
    
    def analysis_tool(vision_data: dict, knowledge_data: dict) -> str:
        """Herramienta para análisis"""
        result = self.analysis_agent.execute(vision_data, knowledge_data)
        return f"Diagnóstico: {result['diagnosis']}"
    
    # Crear Tools de LangChain
    tools = [
        Tool(
            name="vision_analysis",
            func=vision_tool,
            description="Analiza imágenes de plantas"
        ),
        Tool(
            name="knowledge_search",
            func=knowledge_tool,
            description="Busca información en base de conocimiento"
        ),
        Tool(
            name="plant_analysis",
            func=analysis_tool,
            description="Realiza análisis y diagnóstico"
        )
    ]
    
    return tools
```

**Qué explicar:**
- Cada agente se convierte en un Tool de LangChain
- Tools permiten que el LLM decida cuándo usarlos
- Descripción ayuda al LLM a entender qué hace cada tool

### Código a Mostrar - AgentExecutor

```python
def _create_agent_executor(self):
    """Crea el AgentExecutor de LangChain"""
    
    # Prompt template para el agente
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Eres un experto en plantas. Tienes acceso a:
        - vision_analysis: Analiza imágenes
        - knowledge_search: Busca información
        - plant_analysis: Diagnostica problemas
        
        Usa estas herramientas para responder."""),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    # Crear agente estructurado
    agent = create_structured_chat_agent(
        llm=self.llm,
        tools=self.tools,
        prompt=prompt
    )
    
    # Crear ejecutor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=self.tools,
        memory=self.memory,  # Memoria de conversación
        verbose=True,
        handle_parsing_errors=True
    )
    
    return agent_executor
```

**Qué explicar:**
- `AgentExecutor` coordina la ejecución
- El LLM decide qué tool usar y cuándo
- `memory` mantiene contexto de la conversación

---

## 🤖 5. USO DEL LLM (agente_respuesta.py)

### Código a Mostrar - Generación de Recomendaciones

```python
def generate_recommendations(self, analysis_result: Dict, context: str, user_question: str = ""):
    """Genera recomendaciones usando LLM"""
    
    # Construir prompt
    prompt = f"""Eres un experto en plantas. Basándote en:
    
    ANÁLISIS:
    - Especie: {analysis_result.get('species')}
    - Estado: {analysis_result.get('overall_status')}
    - Diagnóstico: {analysis_result.get('diagnosis')}
    - Problemas: {analysis_result.get('identified_issues')}
    
    PREGUNTA DEL USUARIO:
    {user_question}
    
    CONOCIMIENTO RELEVANTE:
    {context[:500]}
    
    Genera 3-5 recomendaciones específicas y accionables.
    Si el usuario tiene una preocupación específica, abórdala directamente."""
    
    # Generar con Gemini
    if self.llm:
        response = self.llm.generate_content(prompt)
        recommendations = parse_recommendations(response.text)
        return recommendations
    
    # Fallback: usar solo documentos
    return self._get_default_recommendations(analysis_result, user_question)
```

**Qué explicar:**
- El LLM genera texto basado en contexto
- Prompt incluye análisis completo + conocimiento
- Tiene fallback si LLM no está disponible

---

## 🔄 6. FLUJO PRINCIPAL (main.py)

### Código a Mostrar - Endpoint Principal

```python
@app.post("/api/analyze-plant")
async def analyze_plant(
    image: UploadFile = File(...),
    user_actions: str = Form("")
):
    """Endpoint principal: Analiza una imagen de planta"""
    
    # 1. Guardar imagen temporalmente
    temp_file_path = UPLOAD_DIR / f"temp_plant_{unique_id}.jpg"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    # 2. Ejecutar sistema multi-agente
    result = response_agent.execute(
        image_path=str(temp_file_path),
        user_actions=user_actions
    )
    
    # 3. Retornar resultado
    return JSONResponse(content=result)
```

**Qué explicar:**
- Endpoint recibe imagen y pregunta del usuario
- Ejecuta el sistema completo de agentes
- Retorna análisis completo

---

## 📊 7. EJEMPLO DE RESULTADO

### Estructura de Respuesta

```python
{
    "success": True,
    "plant_info": {
        "species": "Cestrum nocturnum",
        "common_names": ["night jessamine", "queen of the night"],
        "confidence": 0.32
    },
    "health_assessment": {
        "score": 5,
        "status": "Regular - Requiere atención"
    },
    "diagnosis": {
        "summary": "La planta presenta un estado general saludable",
        "visual_problems": ["hojas ligeramente amarillas"],
        "identified_issues": [
            {"type": "falta_de_luz", "severity": 6}
        ]
    },
    "recommendations": [
        "Mueve la planta a un lugar con más luz indirecta",
        "Ajusta el riego según la temporada",
        "Fertiliza durante primavera-verano"
    ]
}
```

---

## 🎯 SECUENCIA DE DEMOSTRACIÓN

### Orden Sugerido para Mostrar Código:

1. **main.py** - Mostrar endpoint principal (30 seg)
2. **agente_respuesta_langchain.py** - Mostrar AgentExecutor (1 min)
3. **agente_vision.py** - Mostrar identificación (30 seg)
4. **embeddings.py** - Mostrar generación de embeddings (1 min)
5. **agente_conocimiento.py** - Mostrar búsqueda en Supabase (1 min)
6. **agente_analisis.py** - Mostrar diagnóstico (30 seg)
7. **agente_respuesta.py** - Mostrar generación con LLM (1 min)

**Total: ~6 minutos de código**

---

## 💡 FRASES PARA USAR AL MOSTRAR CÓDIGO

- "Aquí vemos cómo el agente genera un embedding..."
- "Este código muestra la búsqueda vectorial en Supabase..."
- "LangChain AgentExecutor coordina todos estos agentes..."
- "El LLM recibe todo este contexto y genera recomendaciones..."
- "Este fallback asegura que el sistema funcione sin APIs externas..."

---

**¡Usa estos ejemplos de código para demostrar cómo funciona el sistema! 💻**

