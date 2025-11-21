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

@app.on_event("startup")
async def startup_event():
    """Inicializa el sistema al arrancar"""
    global response_agent
    print("\n🚀 Iniciando PlantCare AI Backend...")
    
    # Inicializar agente (use_supabase=False para desarrollo sin Supabase)
    use_supabase = os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY")
    response_agent = ResponseAgent(use_supabase=use_supabase)
    
    print("✅ Backend listo para recibir peticiones\n")


# Modelos Pydantic
class HealthResponse(BaseModel):
    status: str
    message: str


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
    try:
        # Validar formato de imagen
        if not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="El archivo debe ser una imagen"
            )
        
        # Guardar imagen temporalmente
        file_extension = Path(image.filename).suffix
        temp_file_path = UPLOAD_DIR / f"temp_plant{file_extension}"
        
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        print(f"\n📸 Imagen recibida: {image.filename}")
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
        print(f"❌ Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando imagen: {str(e)}"
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
    print(f"  - GET  http://{host}:{port}/api/stats")
    print(f"  - GET  http://{host}:{port}/docs (Swagger UI)")
    print("\n")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug
    )
