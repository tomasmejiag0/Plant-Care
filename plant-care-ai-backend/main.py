"""
FastAPI Server - PlantCare AI Backend
API REST para análisis de plantas usando arquitectura multi-agente
"""
import os
import sys
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from pathlib import Path
import shutil
from dotenv import load_dotenv

# Agregar src al path
sys.path.append('src')
sys.path.append('src/agentes')

from agentes.agente_respuesta import ResponseAgent
# Importar versión con LangChain para cumplir requisitos académicos
try:
    from agentes.agente_respuesta_langchain import ResponseAgentLangChain
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠ LangChain no disponible, usando implementación manual")

load_dotenv()

# Inicializar FastAPI
app = FastAPI(
    title="PlantCare AI API",
    description="API de análisis inteligente de plantas usando multi-agentes",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde el navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directorio para uploads temporales
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Inicializar sistema multi-agente (global)
response_agent = None
response_agent_langchain = None
gemini_available = False
gemini_vision_available = False
local_llm = None

@app.on_event("startup")  # Deprecated pero funcional - mantener para compatibilidad
async def startup_event():
    """Inicializa el sistema al arrancar"""
    global response_agent, response_agent_langchain, gemini_available, gemini_vision_available, local_llm
    print("\n🚀 Iniciando PlantCare AI Backend...")
    
    # Inicializar agente tradicional
    use_supabase = os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY")
    response_agent = ResponseAgent(use_supabase=use_supabase)
    
    # Verificar disponibilidad de Gemini
    gemini_available = response_agent.llm is not None
    gemini_vision_available = response_agent.vision_agent.gemini_model is not None
    
    # Intentar inicializar LLM local como fallback (siempre, incluso si Gemini está disponible)
    try:
        from src.local_llm import get_local_llm
        local_llm = get_local_llm()
        if local_llm:
            print(f"[OK] LLM local disponible ({local_llm.model}) - disponible como respaldo")
        else:
            print("[INFO] LLM local no disponible - se usará solo documentos si Gemini falla")
    except Exception as e:
        print(f"[WARN] Error inicializando LLM local: {e}")
        local_llm = None
    
    if not gemini_available:
        if local_llm:
            print("[OK] Usando LLM local como principal (Gemini no disponible)")
        else:
            print("[WARN] Gemini LLM no disponible y LLM local no disponible - sistema funcionará solo con documentos")
    
    if not gemini_vision_available:
        print("⚠️ Gemini Vision no disponible - análisis de imágenes deshabilitado")
    
    # Inicializar agente con LangChain (para cumplir requisitos académicos)
    if LANGCHAIN_AVAILABLE:
        try:
            response_agent_langchain = ResponseAgentLangChain(use_supabase=use_supabase)
            print("✓ Agente LangChain inicializado")
        except Exception as e:
            print(f"⚠ Error inicializando LangChain agent: {e}")
            response_agent_langchain = None
    
    print("✅ Backend listo para recibir peticiones\n")


# Modelos Pydantic
class HealthResponse(BaseModel):
    status: str
    message: str

class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []

class ChatResponse(BaseModel):
    success: bool
    response: str
    error: str = None


@app.get("/", response_model=HealthResponse)
async def root():
    """Endpoint raíz"""
    return {
        "status": "online",
        "message": "PlantCare AI API está funcionando 🌱"
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check del API"""
    return {
        "status": "healthy",
        "message": "API operativa"
    }

@app.get("/api/capabilities")
async def get_capabilities():
    """
    Endpoint para verificar qué capacidades están disponibles
    Útil para el frontend para saber qué funciones habilitar/deshabilitar
    """
    global gemini_available, gemini_vision_available
    
    return {
        "gemini_llm_available": gemini_available,
        "gemini_vision_available": gemini_vision_available,
        "image_analysis_available": gemini_vision_available,  # Requiere Gemini Vision
        "chat_available": True,  # Siempre disponible (usa documentos si no hay LLM)
        "message": "Capacidades del sistema"
    }


@app.post("/api/analyze-plant")
async def analyze_plant(
    image: UploadFile = File(..., description="Imagen de la planta"),
    user_actions: str = Form("", description="Descripción de acciones del usuario con la planta")
):
    """
    Endpoint principal: Analiza una imagen de planta
    
    Parámetros:
    - image: Archivo de imagen (JPEG, PNG)
    - user_actions: Texto describiendo qué ha hecho el usuario con la planta
    
    Retorna:
    - Análisis completo de la planta con recomendaciones
    """
    global gemini_vision_available
    
    # Verificar si Gemini Vision está disponible
    if not gemini_vision_available:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "image_analysis_unavailable",
                "message": "El análisis de imágenes no está disponible en este momento. Por favor, usa el chat de texto para hacer preguntas sobre cuidado de plantas."
            }
        )
    
    try:
        # Validar formato de imagen
        if not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="El archivo debe ser una imagen"
            )
        
        # Guardar imagen temporalmente con nombre único
        import time
        import uuid
        file_extension = Path(image.filename).suffix or '.jpg'
        unique_id = f"{int(time.time())}_{uuid.uuid4().hex[:8]}"
        temp_file_path = UPLOAD_DIR / f"temp_plant_{unique_id}{file_extension}"
        
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        print(f"\n📸 Imagen recibida: {image.filename} (guardada como {temp_file_path.name})")
        print(f"📝 Acciones del usuario: {user_actions if user_actions else '(ninguna)'}")
        
        # Ejecutar sistema multi-agente
        result = response_agent.execute(
            image_path=str(temp_file_path),
            user_actions=user_actions
        )
        
        # Limpiar archivo temporal (Windows fix: asegurar que está cerrado)
        try:
            if temp_file_path.exists():
                import time
                time.sleep(0.1)  # Pequeña pausa para Windows
                temp_file_path.unlink()
        except Exception as e:
            print(f"⚠ No se pudo eliminar archivo temporal: {e}")
        
        if result.get('success'):
            return JSONResponse(
                status_code=200,
                content=result
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Error en análisis')
            )
    
    except HTTPException:
        raise
    except Exception as e:
        error_str = str(e)
        print(f"❌ Error: {e}")
        
        # Detectar si es error de quota o servicio no disponible
        is_quota_error = (
            "429" in error_str or 
            "ResourceExhausted" in error_str or 
            "quota" in error_str.lower() or
            "exceeded" in error_str.lower()
        )
        
        if is_quota_error:
            # Deshabilitar Gemini Vision para evitar más intentos
            response_agent.vision_agent.gemini_model = None
            gemini_vision_available = False
            
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "image_analysis_unavailable",
                    "message": "El análisis de imágenes no está disponible en este momento debido a limitaciones del servicio. Por favor, usa el chat de texto para hacer preguntas sobre cuidado de plantas."
                }
            )
        
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando imagen: {str(e)}"
        )


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Endpoint de chat con RAG - Responde preguntas usando la base de conocimiento
    
    Parámetros:
    - message: Mensaje del usuario
    - history: Historial de conversación (opcional)
    
    Retorna:
    - Respuesta del agente basada en la base de conocimiento
    """
    global local_llm
    try:
        print(f"\n💬 Chat request recibido")
        print(f"📝 Mensaje: {request.message}")
        print(f"📚 Historial: {len(request.history)} mensajes")
        
        # Usar el knowledge agent para buscar información relevante
        knowledge_agent = response_agent.knowledge_agent
        
        # Verificar si la pregunta es sobre plantas ANTES de buscar
        message_lower = request.message.lower().strip()
        
        # Detectar preguntas conceptuales generales que no son sobre cuidado de plantas
        conceptual_questions = [
            'que es una', 'que es un', 'que es el', 'que es la', 'que son las', 'que son los',
            'que significa', 'definicion', 'definición', 'concepto de', 'que quiere decir'
        ]
        
        is_conceptual_general = any(pattern in message_lower for pattern in conceptual_questions)
        
        # Palabras clave específicas de cuidado de plantas (no solo palabras relacionadas)
        plant_care_keywords = ['riego', 'cuidado', 'cuidar', 'mantener', 'regar', 'suelo', 'tierra',
                               'luz', 'sol', 'sombra', 'maceta', 'trasplante', 'poda', 'fertilizante',
                               'enfermedad', 'plaga', 'problema', 'hoja amarilla', 'hoja marron',
                               'como cuidar', 'como mantener', 'como regar', 'cuando regar',
                               'suculenta', 'cactus', 'bonsai', 'orquidea', 'helecho']
        
        # Verificar si es una pregunta sobre cuidado de plantas específicamente
        is_plant_care_question = any(keyword in message_lower for keyword in plant_care_keywords)
        
        # Si es una pregunta conceptual general sin contexto de cuidado, responder directamente
        if is_conceptual_general and not is_plant_care_question:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "response": "Soy un asistente especializado en el cuidado práctico de plantas. Puedo ayudarte con:\n\n• Cómo cuidar diferentes tipos de plantas\n• Problemas comunes y sus soluciones\n• Recomendaciones de riego, luz y suelo\n• Identificación de problemas de salud\n• Propagación y trasplante\n\nSi tienes una pregunta específica sobre cómo cuidar una planta, estaré encantado de ayudarte. Por ejemplo: '¿Cómo cuido una suculenta?' o '¿Cuándo debo regar mi planta?'"
                }
            )
        
        # Verificar si tiene palabras relacionadas con plantas (para búsqueda)
        plant_keywords = ['planta', 'flor', 'hoja', 'jardín', 'verde', 'semilla', 'raíz', 'tallo']
        has_plant_keyword = any(keyword in message_lower for keyword in plant_keywords)
        
        # Si no tiene ninguna relación con plantas, responder directamente
        if not has_plant_keyword and not is_plant_care_question:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "response": "Lo siento, pero esa pregunta no está relacionada con plantas. Soy un asistente especializado en cuidado de plantas. Puedo ayudarte con:\n\n• Identificación de plantas\n• Cuidado y mantenimiento\n• Problemas de salud de plantas\n• Recomendaciones de riego, luz y suelo\n• Tratamiento de plagas\n\n¿Tienes alguna pregunta sobre plantas que pueda ayudarte a resolver?"
                }
            )
        
        # Buscar en la base de conocimiento
        documents = knowledge_agent.search_direct(request.message, top_k=5)
        
        # Debug: mostrar documentos encontrados
        if documents:
            print(f"📊 Documentos encontrados: {len(documents)}")
            for i, doc in enumerate(documents[:3]):
                print(f"  Doc {i+1}: relevancia={doc['relevance_score']:.3f}, fuente={doc.get('source', 'N/A')[:50]}")
                print(f"    Texto preview: {doc.get('text', '')[:100]}...")
        else:
            print("⚠️ No se encontraron documentos")
        
        # Verificar relevancia de los documentos encontrados
        if documents:
            max_relevance = max([d['relevance_score'] for d in documents])
            print(f"📈 Relevancia máxima: {max_relevance:.3f}")
            # Si la relevancia es muy baja (< 0.3), los documentos probablemente no son relevantes
            if max_relevance < 0.3:
                print(f"⚠️ Relevancia máxima muy baja: {max_relevance:.3f}")
                # Aún así, intentar usar los documentos si hay alguno con relevancia > 0.25
                if max_relevance >= 0.25:
                    print(f"📝 Usando documentos con relevancia baja pero aceptable")
                else:
                    return JSONResponse(
                        status_code=200,
                        content={
                            "success": True,
                            "response": f"Lo siento, no encontré información específica sobre '{request.message}' en mi base de conocimiento sobre cuidado de plantas. Puedo ayudarte con:\n\n• Cuidado de suculentas, cactus, plantas de interior\n• Problemas comunes de plantas\n• Riego, luz y suelo\n• Propagación y trasplante\n\n¿Te gustaría hacer una pregunta más específica sobre cuidado de plantas? Por ejemplo: '¿Cómo cuido una suculenta?'"
                        }
                    )
        
        # Construir contexto del historial
        history_context = ""
        if request.history:
            history_context = "\n".join([
                f"{'Usuario' if msg.role == 'user' else 'Asistente'}: {msg.content}"
                for msg in request.history[-6:]  # Últimos 6 mensajes
            ])
        
        # Construir contexto de conocimiento (texto completo de documentos más relevantes)
        knowledge_context = ""
        if documents:
            # Limpiar el texto de los documentos antes de pasarlo al LLM
            import re
            cleaned_docs = []
            for doc in documents[:3]:  # Top 3 documentos
                doc_text = doc['text']
                # Limpiar markdown de los documentos también
                doc_text = re.sub(r'^#{1,6}\s+', '', doc_text, flags=re.MULTILINE)
                doc_text = re.sub(r'#{1,6}\s+', '', doc_text)
                # Limpiar puntos suspensivos
                doc_text = re.sub(r'\.\.\.+', '', doc_text)
                cleaned_docs.append({
                    'text': doc_text,
                    'score': doc['relevance_score']
                })
            
            # Usar texto limpio pero organizado
            knowledge_context = "\n\n--- INFORMACIÓN DE REFERENCIA ---\n\n".join([
                f"Fuente {i+1} (Relevancia: {doc['score']:.2f}):\n{doc['text']}"
                for i, doc in enumerate(cleaned_docs)
            ])
        else:
            # No se encontraron documentos relevantes
            knowledge_context = "No se encontró información relevante en la base de conocimiento sobre esta pregunta."
        
        # Usar LLM para generar respuesta
        if response_agent.llm:
            print("🤖 Usando LLM para generar respuesta")
            prompt = f"""Eres un experto en cuidado de plantas hablando directamente con un amigo que te pregunta sobre plantas. Responde de forma completamente natural y conversacional.

⚠️ REGLAS ABSOLUTAS - NO PUEDES ROMPER ESTAS:
1. NUNCA uses símbolos # ## ### #### ##### ###### en tu respuesta - está completamente prohibido
2. NUNCA copies texto directamente - SIEMPRE explica con tus propias palabras de forma natural
3. NUNCA uses frases como "Basándome en", "Según", "De acuerdo a" - responde directamente
4. NUNCA dejes respuestas incompletas o truncadas - completa TODO lo que vas a explicar
5. NUNCA uses formato técnico o de documento - solo lenguaje conversacional normal

FORMATO DE RESPUESTA CORRECTO:
- Comienza respondiendo directamente la pregunta
- Usa párrafos normales y fluidos (no títulos, no secciones)
- Si hay pasos o listas, usa viñetas (•) o números (1. 2. 3.) de forma natural dentro del texto
- Explica todo completamente antes de terminar
- Puedes usar emojis ocasionalmente (🌱💧☀️🌿)
- Termina con una pregunta amigable opcional

EJEMPLO INCORRECTO (NO HAGAS ESTO):
"# Cuidado de Suculentas
## Descripción General
Las suculentas son plantas que almacenan agua...
## Propagación
1. Usar tierra..."

EJEMPLO CORRECTO (HAZ ESTO):
"Las suculentas son plantas increíbles que almacenan agua en sus hojas y tallos, lo que las hace muy resistentes. Son perfectas para principiantes porque requieren muy poco mantenimiento.

Para cuidarlas correctamente, aquí tienes lo más importante:

• Riego: Solo riega cuando la tierra esté completamente seca. En invierno puede ser cada 2-4 semanas.

• Luz: Necesitan al menos 6 horas de luz solar directa al día.

• Suelo: Usa una mezcla especial para cactus con buen drenaje.

Si quieres propagarlas, puedes cortar una hoja, dejarla secar unos días, y luego plantarla. En 4-12 semanas deberías ver raíces nuevas.

¿Te gustaría saber más sobre algún aspecto específico?"

HISTORIAL DE CONVERSACIÓN:
{history_context if history_context else "Primera pregunta del usuario."}

INFORMACIÓN DE REFERENCIA DE SUPABASE (usa esto SOLO para entender el tema, luego explica TODO con tus propias palabras de forma natural):
{knowledge_context}

⚠️ IMPORTANTE: NO copies texto directamente de la información de referencia. NO uses títulos como "Descripción General", "Propagación por Semillas", "Ventajas", "Desventajas", etc. Explica TODO con tus propias palabras de forma conversacional y natural.

PREGUNTA DEL USUARIO: {request.message}

IMPORTANTE: Responde SOLO con texto normal, sin símbolos #, sin copiar texto, explicando todo con tus propias palabras de forma natural y completa. Responde ahora:"""

            try:
                # Configurar parámetros para respuestas más completas y naturales
                import google.generativeai as genai
                try:
                    generation_config = genai.types.GenerationConfig(
                        temperature=0.9,  # Más creatividad para respuestas naturales y parafraseadas
                        top_p=0.95,
                        top_k=40,
                        max_output_tokens=2048,  # Respuestas más largas y completas
                    )
                except:
                    # Fallback si GenerationConfig no está disponible
                    generation_config = {
                        "temperature": 0.9,
                        "top_p": 0.95,
                        "top_k": 40,
                        "max_output_tokens": 2048,
                    }
                
                # Intentar generar respuesta hasta 2 veces si contiene markdown
                max_attempts = 2
                response_text = None
                
                for attempt in range(max_attempts):
                    response = response_agent.llm.generate_content(
                        prompt,
                        generation_config=generation_config
                    )
                    response_text = response.text.strip()
                    
                    # Verificar si tiene markdown
                    if not re.search(r'#{1,6}\s+', response_text):
                        break  # Respuesta limpia, salir del loop
                    elif attempt < max_attempts - 1:
                        print(f"⚠️ Intento {attempt + 1}: Respuesta contiene markdown, regenerando...")
                        # Agregar instrucción adicional al prompt
                        prompt += "\n\nRECUERDA: NO uses símbolos # en tu respuesta. Responde solo con texto normal."
                    else:
                        print("⚠️ Respuesta aún contiene markdown después de múltiples intentos")
                
                if not response_text:
                    response_text = response.text.strip()
                
                # Validar si la respuesta contiene markdown - si es así, limpiar agresivamente
                import re
                has_markdown = bool(re.search(r'#{1,6}\s+', response_text))
                
                if has_markdown:
                    print("⚠️ Respuesta contiene markdown, aplicando limpieza agresiva...")
                
                # Limpieza MUY agresiva de markdown y texto truncado
                
                # PRIMERO: Detectar y eliminar fragmentos que parecen venir directamente de documentos
                # Patrones que indican texto copiado de documentos
                document_patterns = [
                    r'Cuidado de [A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+ Descripción General',
                    r'Descripción General[:\s]*',
                    r'Propagación por Semillas[:\s]*',
                    r'Ventajas[:\s]*-',
                    r'Desventajas[:\s]*-',
                    r'Método Básico[:\s]*\d+\.',
                    r'Problemas Comunes[:\s]*-',
                    r'Trasplante Frecuencia[:\s]*-',
                    r'Procedimiento[:\s]*\d+\.',
                ]
                for pattern in document_patterns:
                    response_text = re.sub(pattern, '', response_text, flags=re.IGNORECASE | re.MULTILINE)
                
                # Eliminar líneas que son claramente títulos de documentos
                lines = response_text.split('\n')
                cleaned_lines = []
                skip_until_content = False
                for line in lines:
                    stripped = line.strip()
                    # Detectar títulos de documentos comunes
                    if any(title in stripped for title in ['Descripción General', 'Propagación por Semillas', 
                                                           'Ventajas', 'Desventajas', 'Método Básico', 
                                                           'Problemas Comunes', 'Trasplante Frecuencia', 'Procedimiento']):
                        skip_until_content = True
                        continue
                    # Si encontramos contenido real después de un título, dejar de saltar
                    if skip_until_content and len(stripped) > 20 and not re.match(r'^[\d\.\-\•\*]+', stripped):
                        skip_until_content = False
                    if not skip_until_content:
                        cleaned_lines.append(line)
                response_text = '\n'.join(cleaned_lines)
                
                # Eliminar TODOS los headers de markdown (# ## ### #### ##### ######) - múltiples pasos
                response_text = re.sub(r'^#{1,6}\s+', '', response_text, flags=re.MULTILINE)
                response_text = re.sub(r'#{1,6}\s+', '', response_text)  # En cualquier lugar
                response_text = re.sub(r'#+', '', response_text)  # Cualquier secuencia de #
                
                # Eliminar puntos suspensivos (truncados)
                response_text = re.sub(r'\.\.\.+', '', response_text)
                response_text = re.sub(r'\.\.\.\s*$', '', response_text, flags=re.MULTILINE)
                
                # Eliminar frases genéricas comunes
                phrases_to_remove = [
                    r'Basándome en la información disponible[:\s]*',
                    r'Según los documentos[:\s]*',
                    r'Según la información[:\s]*',
                    r'De acuerdo a[:\s]*',
                    r'Basándome en[:\s]*',
                    r'De acuerdo con[:\s]*',
                    r'Con base en[:\s]*',
                    r'Propagación por Semillas',
                    r'Ventajas',
                    r'Desventajas',
                    r'Método Básico'
                ]
                for phrase in phrases_to_remove:
                    response_text = re.sub(phrase, '', response_text, flags=re.IGNORECASE)
                
                # Procesar líneas para eliminar formato técnico y fragmentos de documentos
                lines = response_text.split('\n')
                cleaned_lines = []
                skip_next = False
                
                # Lista de frases que indican texto copiado de documentos
                document_indicators = [
                    'Descripción General', 'Propagación por Semillas', 'Ventajas', 'Desventajas',
                    'Método Básico', 'Problemas Comunes', 'Trasplante Frecuencia', 'Procedimiento',
                    'Cuidado de Suculentas', 'Cuidado de Cactus', 'Plantas de Interior Comunes'
                ]
                
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    
                    # Saltar líneas vacías
                    if not stripped:
                        if cleaned_lines and cleaned_lines[-1].strip():  # Solo agregar si la anterior no estaba vacía
                            cleaned_lines.append('')
                        continue
                    
                    # Eliminar líneas que contienen indicadores de documentos
                    if any(indicator in stripped for indicator in document_indicators):
                        # Si es solo el título sin contenido adicional, saltarlo
                        if len(stripped) < 50 or stripped in document_indicators:
                            continue
                        # Si tiene contenido adicional, intentar limpiarlo
                        for indicator in document_indicators:
                            stripped = stripped.replace(indicator, '').strip()
                    
                    # Eliminar líneas que son solo números, viñetas o muy cortas
                    if re.match(r'^[\d\.\-\•\*]+$', stripped) or len(stripped) < 4:
                        continue
                    
                    # Eliminar líneas que parecen títulos técnicos (todo en mayúsculas y cortas)
                    if stripped.isupper() and len(stripped) < 50 and len(stripped.split()) < 5:
                        continue
                    
                    # Si la línea anterior era un número/viñeta y esta parece ser continuación, unirlas
                    if cleaned_lines and re.match(r'^\d+\.', cleaned_lines[-1].strip()):
                        cleaned_lines[-1] += ' ' + stripped
                    else:
                        cleaned_lines.append(stripped if stripped else line)
                
                response_text = '\n'.join(cleaned_lines)
                
                # Limpiar espacios múltiples y saltos de línea
                response_text = re.sub(r'\n{3,}', '\n\n', response_text)
                response_text = re.sub(r' {2,}', ' ', response_text)
                response_text = response_text.strip()
                
                # Si la respuesta todavía contiene markdown después de la limpieza, eliminarlo completamente
                if '#' in response_text:
                    # Dividir por líneas y eliminar las que tienen # o que parecen títulos
                    final_lines = []
                    for line in response_text.split('\n'):
                        stripped = line.strip()
                        # Eliminar líneas con # o que parecen títulos técnicos
                        if '#' not in stripped and not re.match(r'^[A-ZÁÉÍÓÚÑ\s]{3,50}$', stripped):
                            # También eliminar líneas que son solo palabras en mayúsculas (títulos)
                            if not (stripped.isupper() and len(stripped.split()) < 5):
                                final_lines.append(line)
                    response_text = '\n'.join(final_lines).strip()
                
                # Eliminar frases específicas que aparecen en las respuestas problemáticas
                problematic_phrases = [
                    'Propagación por Semillas',
                    'Ventajas',
                    'Desventajas',
                    'Método Básico',
                    'Descripción General',
                    'Cuidado de Suculentas',
                    'Cuidado de Cactus',
                    'Plantas de Interior Comunes',
                ]
                for phrase in problematic_phrases:
                    # Eliminar la frase completa y su contexto
                    response_text = re.sub(rf'^{re.escape(phrase)}[:\s]*\n?', '', response_text, flags=re.MULTILINE | re.IGNORECASE)
                    response_text = re.sub(rf'\n{re.escape(phrase)}[:\s]*\n?', '\n', response_text, flags=re.IGNORECASE)
                    # Eliminar también cuando aparece en medio de una línea
                    response_text = re.sub(rf'{re.escape(phrase)}[:\s]*', '', response_text, flags=re.IGNORECASE)
                
                # LIMPIEZA AGRESIVA: Detectar y eliminar fragmentos copiados de documentos
                # Primero, detectar patrones específicos de texto copiado
                
                # Patrón 1: "Cuidado de X Descripción General" seguido de texto técnico
                response_text = re.sub(
                    r'Cuidado de [A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+ Descripción General[^\n]*\n?',
                    '',
                    response_text,
                    flags=re.IGNORECASE | re.MULTILINE
                )
                
                # Patrón 2: Líneas que empiezan con títulos técnicos conocidos
                technical_titles = [
                    r'^Descripción General[:\s]*',
                    r'^Propagación por Semillas[:\s]*',
                    r'^Ventajas[:\s]*-',
                    r'^Desventajas[:\s]*-',
                    r'^Método Básico[:\s]*',
                    r'^Problemas Comunes[:\s]*-',
                    r'^Trasplante Frecuencia[:\s]*-',
                    r'^Procedimiento[:\s]*\d+\.',
                    r'^Cuidado de Suculentas[:\s]*',
                    r'^Cuidado de Cactus[:\s]*',
                ]
                for pattern in technical_titles:
                    response_text = re.sub(pattern, '', response_text, flags=re.MULTILINE | re.IGNORECASE)
                
                # Patrón 3: Fragmentos que parecen listas técnicas copiadas
                # Detectar líneas que son solo "número. texto corto" o "guion texto corto"
                lines = response_text.split('\n')
                cleaned_final = []
                skip_technical_block = False
                
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if not stripped:
                        if cleaned_final and cleaned_final[-1].strip():
                            cleaned_final.append('')
                        skip_technical_block = False
                        continue
                    
                    # Detectar inicio de bloque técnico (títulos conocidos)
                    if any(title in stripped for title in ['Descripción General', 'Propagación por Semillas', 
                                                           'Ventajas', 'Desventajas', 'Método Básico', 
                                                           'Problemas Comunes', 'Trasplante Frecuencia', 'Procedimiento']):
                        skip_technical_block = True
                        continue
                    
                    # Si estamos en un bloque técnico, saltar líneas que parecen técnicas
                    if skip_technical_block:
                        # Detectar si la línea es parte de una lista técnica
                        is_technical_line = (
                            re.match(r'^[\d\.\-\•\*]+\s+[A-Z]', stripped) or  # Empieza con número/guion y mayúscula
                            re.match(r'^[A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+:\s*[A-Z]', stripped) or  # "Título: Texto"
                            (stripped.count('- ') > 0 and len(stripped) < 80) or  # Lista con guiones corta
                            (re.match(r'^\d+\.\s+', stripped) and len(stripped) < 50)  # Pasos numerados cortos
                        )
                        if is_technical_line:
                            continue
                        else:
                            # Si encontramos texto normal, salir del bloque técnico
                            skip_technical_block = False
                    
                    # Si la línea empieza con un número y punto, verificar que tenga suficiente contenido
                    if re.match(r'^\d+\.\s+', stripped):
                        content = re.sub(r'^\d+\.\s+', '', stripped)
                        # Solo mantener si tiene contenido sustancial Y no parece copiado
                        if len(content) > 15 and not any(indicator in content for indicator in 
                                                         ['Corte limpio', 'horizontal ambos', 'Sacar de maceta']):
                            cleaned_final.append(line)
                    elif stripped and not re.match(r'^[\d\.\-\•\*]+$', stripped):
                        # Verificar que no sea un fragmento técnico aislado
                        if not (len(stripped) < 30 and any(indicator in stripped for indicator in 
                                                          ['Corte limpio', 'horizontal ambos', 'Quemaduras solares',
                                                           'Cochinillas y áfidos', 'Hojas blandas'])):
                            cleaned_final.append(line)
                
                response_text = '\n'.join(cleaned_final).strip()
                
                # Eliminar fragmentos específicos problemáticos que se detectaron
                problematic_fragments = [
                    r'Corte limpio horizontal ambos \d+',
                    r'Cuidado de Suculentas Descripción General',
                    r'Hojas blandas y amarillas desde la base',
                    r'Quemaduras solares: Manchas marrones',
                ]
                for fragment in problematic_fragments:
                    response_text = re.sub(fragment, '', response_text, flags=re.IGNORECASE)
                
                # Detectar y eliminar bloques de texto que parecen venir directamente de documentos
                # Dividir en párrafos y analizar cada uno
                paragraphs = response_text.split('\n\n')
                cleaned_paragraphs = []
                for para in paragraphs:
                    para_stripped = para.strip()
                    if not para_stripped:
                        continue
                    
                    # Detectar párrafos que son claramente copiados de documentos
                    # Si contiene múltiples indicadores de documentos o estructura técnica
                    document_indicators_count = sum(1 for indicator in [
                        'Descripción General', 'Propagación por Semillas', 'Ventajas', 'Desventajas',
                        'Método Básico', 'Problemas Comunes', 'Trasplante Frecuencia', 'Procedimiento',
                        'Cuidado de Suculentas', 'Cuidado de Cactus', 'Plantas de Interior Comunes',
                        'Hojas blandas y amarillas', 'Quemaduras solares', 'Cochinillas y áfidos'
                    ] if indicator in para_stripped)
                    
                    # Si tiene más de 1 indicador, probablemente es texto copiado
                    if document_indicators_count > 1:
                        print(f"⚠️ Detectado párrafo copiado de documento (indicadores: {document_indicators_count})")
                        continue
                    
                    # Si el párrafo empieza con un título técnico conocido, saltarlo
                    first_line = para_stripped.split('\n')[0].strip()
                    if first_line in ['Descripción General', 'Propagación por Semillas', 'Ventajas', 
                                     'Desventajas', 'Método Básico', 'Problemas Comunes', 
                                     'Trasplante Frecuencia', 'Procedimiento']:
                        continue
                    
                    # Si el párrafo es muy técnico y estructurado (muchos guiones o números), puede ser copiado
                    if para_stripped.count('- ') > 3 and len(para_stripped.split('\n')) > 2:
                        # Verificar si parece una lista técnica copiada
                        lines_in_para = para_stripped.split('\n')
                        technical_lines = sum(1 for line in lines_in_para if re.match(r'^[\s]*[-•]\s+[A-Z]', line))
                        if technical_lines > 2:
                            print(f"⚠️ Detectado párrafo con estructura técnica copiada")
                            continue
                    
                    cleaned_paragraphs.append(para)
                
                response_text = '\n\n'.join(cleaned_paragraphs).strip()
                
                # Limpiar espacios múltiples y saltos de línea
                response_text = re.sub(r'\n{3,}', '\n\n', response_text)
                response_text = re.sub(r' {2,}', ' ', response_text)
                response_text = response_text.strip()
                
                # LIMPIEZA FINAL: Eliminar cualquier fragmento restante que parezca copiado
                # Dividir en oraciones y filtrar las que parecen fragmentos técnicos
                sentences = re.split(r'[.!?]\s+', response_text)
                cleaned_sentences = []
                for sent in sentences:
                    sent_stripped = sent.strip()
                    if not sent_stripped or len(sent_stripped) < 10:
                        continue
                    
                    # Detectar oraciones que son fragmentos técnicos
                    is_fragment = (
                        sent_stripped.startswith('Corte limpio') or
                        sent_stripped.startswith('horizontal ambos') or
                        sent_stripped.startswith('Sacar de maceta') or
                        'Cuidado de Suculentas' in sent_stripped or
                        'Cuidado de Cactus' in sent_stripped or
                        'Descripción General' in sent_stripped or
                        (len(sent_stripped) < 30 and any(indicator in sent_stripped for indicator in 
                                                         ['Quemaduras solares', 'Cochinillas', 'Hojas blandas']))
                    )
                    
                    if not is_fragment:
                        cleaned_sentences.append(sent_stripped)
                
                if cleaned_sentences:
                    response_text = '. '.join(cleaned_sentences)
                    if response_text[-1] not in '.!?':
                        response_text += '.'
                else:
                    # Si se eliminó todo, usar el texto original pero con limpieza básica
                    response_text = re.sub(r'Cuidado de [A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+ Descripción General[^\n]*', '', response_text, flags=re.IGNORECASE)
                    response_text = re.sub(r'Corte limpio horizontal ambos \d+', '', response_text, flags=re.IGNORECASE)
                
                # Si la respuesta termina abruptamente, agregar punto final
                if response_text and response_text[-1] not in '.!?':
                    response_text += '.'
                
                # Validación final - si todavía tiene problemas, intentar una limpieza más agresiva
                if re.search(r'#{1,6}', response_text) or len(response_text) < 50:
                    print("⚠️ Respuesta aún tiene problemas después de limpieza")
                    # Eliminar completamente cualquier línea con #
                    final_clean = []
                    for line in response_text.split('\n'):
                        if '#' not in line and len(line.strip()) > 5:
                            final_clean.append(line)
                    if final_clean:
                        response_text = '\n'.join(final_clean).strip()
                
                print(f"✅ Respuesta del LLM generada ({len(response_text)} caracteres)")
                
                # Verificar si la respuesta indica que está fuera del conocimiento
                if not documents or (documents and max([d['relevance_score'] for d in documents]) < 0.4):
                    # Baja relevancia, verificar si la pregunta es sobre plantas
                    if not any(word in request.message.lower() for word in ['planta', 'planta', 'flor', 'hoja', 'riego', 'cuidado', 'suelo', 'luz', 'agua', 'maceta', 'jardín', 'verde', 'semilla', 'raíz', 'tallo', 'bonsai', 'suculenta', 'cactus', 'tropical']):
                        response_text = f"Lo siento, pero esa pregunta no está relacionada con plantas. Soy un asistente especializado en cuidado de plantas. Puedo ayudarte con:\n\n• Identificación de plantas\n• Cuidado y mantenimiento\n• Problemas de salud de plantas\n• Recomendaciones de riego, luz y suelo\n• Tratamiento de plagas\n\n¿Tienes alguna pregunta sobre plantas que pueda ayudarte a resolver?"
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "response": response_text
                    }
                )
            except Exception as e:
                error_str = str(e)
                print(f"❌ Error generando respuesta con LLM: {e}")
                
                # Detectar si es error de quota (429) o ResourceExhausted
                is_quota_error = (
                    "429" in error_str or 
                    "ResourceExhausted" in error_str or 
                    "quota" in error_str.lower() or
                    "exceeded" in error_str.lower()
                )
                
                if is_quota_error:
                    print("⚠️ Quota de Gemini agotada - deshabilitando LLM para esta sesión")
                    # Deshabilitar LLM para evitar más intentos
                    response_agent.llm = None
                    global gemini_available
                    gemini_available = False
                
                import traceback
                traceback.print_exc()
                
                # Fallback: Intentar LLM local primero, luego documentos
                print("⚠️ Gemini LLM no disponible o falló")
                
                # Intentar usar LLM local si está disponible (ya declarado como global al inicio de la función)
                if local_llm and local_llm.available:
                    print(f"🤖 Intentando generar respuesta con LLM local ({local_llm.model})...")
                    try:
                        # Construir prompt similar al de Gemini pero más simple
                        local_prompt = f"""Eres un experto en cuidado de plantas. Responde de forma natural y conversacional.

HISTORIAL:
{history_context if history_context else "Primera pregunta."}

INFORMACIÓN DE REFERENCIA:
{knowledge_context[:1500] if knowledge_context else "No hay información específica disponible."}

PREGUNTA: {request.message}

Responde de forma natural, sin usar símbolos #, sin copiar texto directamente. Explica con tus propias palabras:"""
                        
                        local_response = local_llm.generate(
                            prompt=local_prompt,
                            max_tokens=800,
                            temperature=0.8
                        )
                        
                        if local_response:
                            # Aplicar limpieza básica
                            local_response = re.sub(r'#{1,6}\s+', '', local_response)
                            local_response = re.sub(r'\.\.\.+', '', local_response)
                            local_response = re.sub(r'\s+', ' ', local_response).strip()
                            
                            if len(local_response) > 50:
                                print(f"✅ Respuesta generada con LLM local ({len(local_response)} caracteres)")
                                return JSONResponse(
                                    status_code=200,
                                    content={
                                        "success": True,
                                        "response": local_response
                                    }
                                )
                    except Exception as e:
                        print(f"⚠️ Error con LLM local: {e}")
                
                # Si LLM local falló o no está disponible, usar documentos o modo demo
                print("📝 LLM local no disponible - usando procesador de documentos o modo demo")
                if documents and max([d['relevance_score'] for d in documents]) >= 0.25:
                    print(f"📝 Usando procesador inteligente de documentos con {len(documents)} documentos")
                    
                    try:
                        from src.document_processor import DocumentProcessor
                        processor = DocumentProcessor()
                        response_text = processor.extract_relevant_info(request.message, documents)
                        
                        if response_text:
                            # Limpiar respuesta final
                            response_text = re.sub(r'\s+', ' ', response_text)
                            if not response_text.endswith('.'):
                                response_text += '.'
                            response_text += '\n\n¿Te gustaría saber más sobre algún aspecto específico?'
                            
                            return JSONResponse(
                                status_code=200,
                                content={
                                    "success": True,
                                    "response": response_text
                                }
                            )
                    except ImportError:
                        print("⚠️ DocumentProcessor no disponible, usando método simple")
                        # Fallback a método simple
                        pass
                    
                    # Método simple si el procesador no está disponible
                    import re
                    relevant_docs = [d for d in documents if d['relevance_score'] >= 0.25]
                    all_text = []
                    for doc in relevant_docs[:3]:
                        doc_text = doc['text']
                        doc_text = re.sub(r'^#{1,6}\s+', '', doc_text, flags=re.MULTILINE)
                        doc_text = re.sub(r'#{1,6}\s+', '', doc_text)
                        doc_text = re.sub(r'\.\.\.+', '', doc_text)
                        lines = [l.strip() for l in doc_text.split('\n') if l.strip() and len(l.strip()) > 10]
                        doc_text = ' '.join(lines)
                        if doc_text:
                            all_text.append(doc_text[:500])
                    
                    if all_text:
                        combined = ' '.join(all_text[:2])
                        combined = re.sub(r'\s+', ' ', combined)
                        response_text = combined[:800]
                        if len(combined) > 800:
                            response_text += '...'
                        response_text += '\n\n¿Te gustaría saber más sobre algún aspecto específico?'
                        
                        return JSONResponse(
                            status_code=200,
                            content={
                                "success": True,
                                "response": response_text
                            }
                        )
                
                # Si no hay documentos relevantes, usar modo demo
                print("📝 No se encontraron documentos relevantes - usando modo demo")
                try:
                    from demo_mode import get_demo_response
                    response_text = get_demo_response(request.message)
                    print("✅ Respuesta generada con modo demo")
                    return JSONResponse(
                        status_code=200,
                        content={
                            "success": True,
                            "response": response_text
                        }
                    )
                except ImportError:
                    print("⚠️ Modo demo no disponible")
                    return JSONResponse(
                        status_code=200,
                        content={
                            "success": True,
                            "response": "Lo siento, no encontré información específica sobre esa pregunta en mi base de conocimiento. Por favor, intenta reformular tu pregunta o pregunta sobre otro aspecto del cuidado de plantas."
                        }
                    )
        else:
            # Sin LLM, usar procesador inteligente de documentos
            if documents and max([d['relevance_score'] for d in documents]) >= 0.25:
                try:
                    from src.document_processor import DocumentProcessor
                    processor = DocumentProcessor()
                    response_text = processor.extract_relevant_info(request.message, documents)
                    
                    if response_text:
                        import re
                        response_text = re.sub(r'\s+', ' ', response_text)
                        if not response_text.endswith('.'):
                            response_text += '.'
                        response_text += '\n\n¿Te gustaría saber más sobre algún aspecto específico?'
                        
                        return JSONResponse(
                            status_code=200,
                            content={
                                "success": True,
                                "response": response_text
                            }
                        )
                except ImportError:
                    print("⚠️ DocumentProcessor no disponible, usando método simple")
                    pass
            
            # Método simple o modo demo
            if documents:
                import re
                # Combinar información de múltiples documentos
                combined_info = []
                for doc in documents[:3]:
                    doc_text = doc['text']
                    # Limpiar markdown
                    doc_text = re.sub(r'^#{1,6}\s+', '', doc_text, flags=re.MULTILINE)
                    doc_text = re.sub(r'#{1,6}\s+', '', doc_text)
                    doc_text = re.sub(r'\.\.\.+', '', doc_text)
                    # Eliminar líneas vacías o muy cortas
                    lines = [l.strip() for l in doc_text.split('\n') if l.strip() and len(l.strip()) > 15]
                    doc_text = ' '.join(lines)
                    combined_info.append(doc_text)
                
                # Crear respuesta estructurada
                full_text = ' '.join(combined_info)
                
                # Extraer información relevante según la pregunta
                response_parts = []
                
                # Información general sobre suculentas
                if 'suculent' in request.message.lower():
                    response_parts.append("Las suculentas son plantas que almacenan agua en sus hojas y tallos, lo que las hace muy resistentes y perfectas para principiantes.")
                
                # Extraer información específica
                topics = {
                    'riego': ['riego', 'agua', 'regar', 'humedad'],
                    'luz': ['luz', 'sol', 'iluminación', 'sombra'],
                    'suelo': ['suelo', 'tierra', 'drenaje', 'maceta'],
                    'temperatura': ['temperatura', 'frío', 'calor', 'clima'],
                    'propagación': ['propagación', 'reproducir', 'semilla', 'esqueje']
                }
                
                for topic, keywords in topics.items():
                    relevant_sentences = []
                    for sentence in full_text.split('.'):
                        sentence = sentence.strip()
                        if any(kw in sentence.lower() for kw in keywords) and 20 < len(sentence) < 200:
                            relevant_sentences.append(sentence)
                    
                    if relevant_sentences:
                        # Tomar las 2 más relevantes
                        topic_info = '. '.join(relevant_sentences[:2])
                        # Limpiar markdown residual
                        topic_info = re.sub(r'#{1,6}\s+', '', topic_info)
                        if topic_info:
                            response_parts.append(topic_info + '.')
                
                # Si no encontramos información específica, usar las primeras oraciones útiles
                if len(response_parts) < 2:
                    sentences = [s.strip() for s in full_text.split('.') if 30 < len(s.strip()) < 250][:4]
                    if sentences:
                        response_parts.extend(sentences[:2])
                
                if response_parts:
                    response_text = ' '.join(response_parts)
                    # Limpieza final
                    response_text = re.sub(r'#{1,6}\s+', '', response_text)
                    response_text = re.sub(r'\.\.\.+', '', response_text)
                    response_text = re.sub(r'\s+', ' ', response_text)
                    if not response_text.endswith('.'):
                        response_text += '.'
                    response_text += '\n\n¿Te gustaría saber más sobre algún aspecto específico?'
                else:
                    # Fallback a modo demo
                    try:
                        from demo_mode import get_demo_response
                        response_text = get_demo_response(request.message)
                    except ImportError:
                        response_text = "Encontré información sobre suculentas en mi base de conocimiento. Las suculentas requieren poco mantenimiento y son muy resistentes. ¿Te gustaría que te explique algún aspecto específico del cuidado de suculentas?"
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "response": response_text
                    }
                )
            else:
                # Sin documentos, usar modo demo
                try:
                    from demo_mode import get_demo_response
                    response_text = get_demo_response(request.message)
                except ImportError:
                    response_text = "No encontré información específica sobre esa pregunta. Por favor, intenta hacer preguntas sobre cuidado de plantas, identificación de especies, problemas comunes, o recomendaciones de mantenimiento."
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "response": response_text
                    }
                )
    
    except Exception as e:
        print(f"❌ Error en chat: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando mensaje: {str(e)}"
        )


@app.get("/api/stats")
async def get_stats():
    """Estadísticas del sistema"""
    return {
        "total_agents": 4,
        "agents": [
            "VisionAgent (Gemini Vision + Plant.id)",
            "KnowledgeAgent (Supabase pgvector)",
            "AnalysisAgent (Diagnóstico)",
            "ResponseAgent (Orquestador LangChain)"
        ],
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "llm": "Google Gemini Pro"
    }


if __name__ == "__main__":
    # Configuración del servidor
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print("=" * 60)
    print("🌱 PlantCare AI Backend")
    print("=" * 60)
    print(f"🌐 Host: {host}")
    print(f"🔌 Puerto: {port}")
    print(f"🐛 Debug: {debug}")
    print("=" * 60)
    print("\n📡 Endpoints disponibles:")
    print(f"  - GET  http://{host}:{port}/")
    print(f"  - GET  http://{host}:{port}/api/health")
    print(f"  - POST http://{host}:{port}/api/analyze-plant")
    print(f"  - POST http://{host}:{port}/api/chat")
    print(f"  - GET  http://{host}:{port}/api/stats")
    print(f"  - GET  http://{host}:{port}/docs (Swagger UI)")
    print("\n")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug
    )
