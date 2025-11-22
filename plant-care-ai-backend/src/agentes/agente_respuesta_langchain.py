"""
Agente de Respuesta con LangChain
Orquestador que coordina todos los agentes usando LangChain AgentExecutor
"""
import sys
import os
from pathlib import Path

# Agregar src y src/agentes al path
current_dir = Path(__file__).parent
src_dir = current_dir.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from typing import Dict, List
from dotenv import load_dotenv

# LangChain imports
try:
    from langchain.agents import AgentExecutor, create_structured_chat_agent
    from langchain.tools import Tool
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.memory import ConversationBufferMemory
    from langchain.schema import HumanMessage, AIMessage
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGCHAIN_IMPORTS_OK = True
except ImportError as e:
    print(f"⚠ Error importando LangChain: {e}")
    LANGCHAIN_IMPORTS_OK = False

# Google Gemini
import google.generativeai as genai

from agente_vision import VisionAgent
from agente_conocimiento import KnowledgeAgent
from agente_analisis import AnalysisAgent

load_dotenv()


class ResponseAgentLangChain:
    """
    Agente orquestador usando LangChain para coordinar el flujo multiagente
    Implementa arquitectura de agentes múltiples con LangChain AgentExecutor
    """
    
    def __init__(self, use_supabase: bool = True):
        """
        Inicializa el sistema multiagente con LangChain
        
        Args:
            use_supabase: Si usar Supabase o búsqueda en memoria
        """
        if not LANGCHAIN_IMPORTS_OK:
            raise ImportError("LangChain no está disponible. Verifica la instalación.")
        
        print("\n🤖 Inicializando Sistema Multi-Agente con LangChain...")
        
        # Inicializar agentes especializados
        self.vision_agent = VisionAgent()
        self.knowledge_agent = KnowledgeAgent(use_supabase=use_supabase)
        self.analysis_agent = AnalysisAgent()
        
        # Configurar LLM de LangChain con Gemini
        self.llm = self._setup_llm()
        
        # Crear herramientas (Tools) para los agentes
        self.tools = self._create_tools()
        
        # Configurar memoria para el agente
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Crear agente estructurado con LangChain
        self.agent_executor = self._create_agent_executor()
        
        print("✓ Sistema Multi-Agente con LangChain listo\n")
    
    def _setup_llm(self):
        """Configura el LLM de LangChain con Gemini"""
        if not LANGCHAIN_IMPORTS_OK:
            return None
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            print("⚠ GEMINI_API_KEY no encontrada")
            return None
        
        try:
            # Listar modelos disponibles
            genai.configure(api_key=gemini_key)
            available_models = []
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    model_name = model.name.split('/')[-1]
                    available_models.append(model_name)
            
            if available_models:
                print(f"📋 Modelos Gemini disponibles: {', '.join(available_models)}")
                
                # Intentar modelos en orden de preferencia
                preferred_models = ['gemini-pro', 'gemini-1.5-pro', 'gemini-1.5-flash']
                for model_name in preferred_models:
                    if model_name in available_models:
                        try:
                            llm = ChatGoogleGenerativeAI(
                                model=model_name,
                                temperature=0.7,
                                google_api_key=gemini_key
                            )
                            print(f"✓ LangChain LLM ({model_name}) configurado")
                            return llm
                        except Exception as e:
                            continue
                
                # Fallback al primer modelo disponible
                if available_models:
                    try:
                        llm = ChatGoogleGenerativeAI(
                            model=available_models[0],
                            temperature=0.7,
                            google_api_key=gemini_key
                        )
                        print(f"✓ LangChain LLM ({available_models[0]}) configurado")
                        return llm
                    except Exception as e:
                        print(f"⚠ Error configurando LLM: {e}")
            
            return None
        except Exception as e:
            print(f"⚠ Error configurando LangChain LLM: {e}")
            return None
    
    def _create_tools(self) -> List[Tool]:
        """
        Crea herramientas (Tools) para que el agente las use
        Cada herramienta representa una capacidad de un agente especializado
        """
        def vision_tool(image_path: str, user_context: str = "") -> str:
            """Herramienta para análisis de visión de plantas"""
            try:
                result = self.vision_agent.execute(image_path, user_context)
                return f"Especie identificada: {result.get('species', 'desconocida')}. " \
                       f"Estado de salud: {result.get('health_status', 'desconocido')}. " \
                       f"Problemas visuales: {', '.join(result.get('visual_problems', []))}"
            except Exception as e:
                return f"Error en análisis visual: {str(e)}"
        
        def knowledge_tool(query: str, species: str = "", problems: List[str] = None) -> str:
            """Herramienta para búsqueda de conocimiento en base vectorial"""
            try:
                if problems is None:
                    problems = []
                documents = self.knowledge_agent.search_knowledge(query, species, problems, top_k=3)
                if documents:
                    context = "\n".join([doc['text'][:200] for doc in documents[:2]])
                    return f"Información encontrada: {context}"
                return "No se encontró información relevante"
            except Exception as e:
                return f"Error en búsqueda de conocimiento: {str(e)}"
        
        def analysis_tool(vision_data: dict, knowledge_data: dict, user_actions: str = "") -> str:
            """Herramienta para análisis y diagnóstico"""
            try:
                result = self.analysis_agent.execute(vision_data, knowledge_data, user_actions)
                return f"Diagnóstico: {result.get('diagnosis', 'N/A')}. " \
                       f"Score de salud: {result.get('health_score', 0)}/10. " \
                       f"Estado: {result.get('overall_status', 'N/A')}"
            except Exception as e:
                return f"Error en análisis: {str(e)}"
        
        # Crear herramientas LangChain
        # Nota: Las herramientas se simplifican para uso con LangChain
        # En producción, estos se integrarían mejor con el AgentExecutor
        tools = [
            Tool(
                name="vision_analysis",
                func=lambda x: vision_tool(x if isinstance(x, str) else x.get('image_path', ''), 
                                         x if isinstance(x, dict) else ''),
                description="Analiza imágenes de plantas para identificar especie y estado de salud. Input: ruta de imagen o dict"
            ),
            Tool(
                name="knowledge_search",
                func=lambda x: knowledge_tool(
                    x if isinstance(x, str) else x.get('query', ''),
                    x if isinstance(x, dict) else '',
                    x.get('problems', []) if isinstance(x, dict) else []
                ),
                description="Busca información relevante en la base de conocimiento vectorial. Input: query string o dict"
            ),
            Tool(
                name="plant_analysis",
                func=lambda x: analysis_tool(
                    x.get('vision_data', {}) if isinstance(x, dict) else {},
                    x.get('knowledge_data', {}) if isinstance(x, dict) else {},
                    x.get('user_actions', '') if isinstance(x, dict) else ''
                ),
                description="Realiza análisis completo y diagnóstico de la planta. Input: dict con datos"
            )
        ]
        
        return tools
    
    def _create_agent_executor(self):
        """Crea el AgentExecutor de LangChain"""
        if not self.llm or not self.tools:
            return None
        
        # Prompt template para el agente (debe incluir {tools} y {tool_names})
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un asistente experto en cuidado de plantas que coordina múltiples agentes especializados.

Tienes acceso a las siguientes herramientas:
{tools}

Nombres de herramientas disponibles: {tool_names}

Tu trabajo es orquestar estos agentes para proporcionar respuestas completas sobre cuidado de plantas.

Cuando recibas una imagen de planta:
1. Usa vision_analysis para identificar la especie y problemas visuales
2. Usa knowledge_search para buscar información relevante
3. Usa plant_analysis para generar diagnóstico completo
4. Genera recomendaciones basadas en toda la información

Responde de forma clara, completa y útil.

Usa el siguiente formato:

Question: la pregunta o tarea del usuario
Thought: debes pensar qué hacer
Action: la acción a tomar, debe ser una de [{tool_names}]
Action Input: la entrada para la acción
Observation: el resultado de la acción
... (este Thought/Action/Action Input/Observation puede repetirse N veces)
Thought: Ahora sé la respuesta final
Final Answer: la respuesta final al usuario"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        try:
            # Crear agente estructurado
            agent = create_structured_chat_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt
            )
            
            # Crear ejecutor del agente
            agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                memory=self.memory,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5
            )
            
            print("✓ AgentExecutor de LangChain creado correctamente")
            return agent_executor
        except Exception as e:
            print(f"⚠ Error creando AgentExecutor: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def execute(self, image_path: str, user_actions: str = "") -> Dict:
        """
        Ejecuta el flujo completo usando LangChain AgentExecutor
        
        Args:
            image_path: Ruta a la imagen de la planta
            user_actions: Descripción de acciones del usuario
            
        Returns:
            Respuesta final completa
        """
        print("=" * 60)
        print("🌱 INICIANDO ANÁLISIS CON LANGCHAIN")
        print("=" * 60)
        
        try:
            # Si tenemos AgentExecutor, usarlo
            if self.agent_executor:
                # Construir input para el agente
                agent_input = {
                    "input": f"Analiza esta imagen de planta: {image_path}. Contexto del usuario: {user_actions}"
                }
                
                # Ejecutar agente
                result = self.agent_executor.invoke(agent_input)
                print(f"✓ LangChain Agent ejecutado")
                
                # El resultado viene del agente, pero necesitamos estructurarlo
                # Por ahora, ejecutar flujo tradicional y usar LLM para respuesta final
                pass
            
            # Flujo tradicional (más controlado)
            # 1. AGENTE DE VISIÓN
            vision_result = self.vision_agent.execute(image_path, user_actions)
            
            # 2. AGENTE DE CONOCIMIENTO
            knowledge_result = self.knowledge_agent.execute(vision_result, user_actions)
            
            # 3. AGENTE DE ANÁLISIS
            analysis_result = self.analysis_agent.execute(
                vision_result,
                knowledge_result,
                user_actions
            )
            
            # 4. GENERAR RECOMENDACIONES CON LANGCHAIN LLM
            recommendations = self._generate_recommendations_with_langchain(
                analysis_result,
                knowledge_result.get('context', '')
            )
            
            # Construir respuesta final
            final_response = {
                'success': True,
                'plant_info': {
                    'species': vision_result.get('species'),
                    'common_names': vision_result.get('common_names', []),
                    'confidence': vision_result.get('species_probability', 0)
                },
                'health_assessment': {
                    'score': analysis_result.get('health_score'),
                    'status': analysis_result.get('overall_status'),
                    'visual_health': vision_result.get('health_status')
                },
                'diagnosis': {
                    'summary': analysis_result.get('diagnosis'),
                    'visual_problems': analysis_result.get('visual_problems', []),
                    'identified_issues': analysis_result.get('identified_issues', [])
                },
                'recommendations': recommendations,
                'agent_flow': {
                    'vision_agent': 'completed',
                    'knowledge_agent': f"{knowledge_result.get('num_results', 0)} documents retrieved",
                    'analysis_agent': 'completed',
                    'response_agent': 'completed (LangChain)'
                }
            }
            
            print("\n" + "=" * 60)
            print("✅ ANÁLISIS COMPLETADO CON LANGCHAIN")
            print("=" * 60)
            print(f"   Especie: {final_response['plant_info']['species']}")
            print(f"   Salud: {final_response['health_assessment']['score']}/10")
            print(f"   Recomendaciones: {len(recommendations)}")
            print("=" * 60 + "\n")
            
            return final_response
            
        except Exception as e:
            print(f"\n❌ Error en flujo LangChain: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_recommendations_with_langchain(self, analysis_result: Dict, context: str) -> list:
        """Genera recomendaciones usando LangChain LLM"""
        if not self.llm:
            return self._get_default_recommendations(analysis_result)
        
        try:
            prompt = f"""Eres un experto en cuidado de plantas. Basándote en el siguiente análisis, 
genera 3-5 recomendaciones específicas y accionables.

ANÁLISIS:
- Especie: {analysis_result.get('species')}
- Estado: {analysis_result.get('overall_status')}
- Diagnóstico: {analysis_result.get('diagnosis')}
- Problemas visuales: {', '.join(analysis_result.get('visual_problems', []))}

CONOCIMIENTO RELEVANTE:
{context[:500]}

Genera recomendaciones numeradas, concisas y prácticas:"""
            
            response = self.llm.invoke(prompt)
            recommendations_text = response.content if hasattr(response, 'content') else str(response)
            
            # Parsear recomendaciones
            recommendations = []
            for line in recommendations_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    rec = line.lstrip('0123456789.-) ').strip()
                    if rec:
                        recommendations.append(rec)
            
            return recommendations[:5] if recommendations else self._get_default_recommendations(analysis_result)
            
        except Exception as e:
            print(f"Error generando recomendaciones con LangChain: {e}")
            return self._get_default_recommendations(analysis_result)
    
    def _get_default_recommendations(self, analysis_result: Dict) -> list:
        """Recomendaciones predeterminadas sin LLM"""
        recommendations = []
        issues = analysis_result.get('identified_issues', [])
        
        for issue in issues:
            issue_type = issue.get('type', '')
            if issue_type == 'exceso_de_riego':
                recommendations.append("Reduce la frecuencia de riego")
            elif issue_type == 'falta_de_riego':
                recommendations.append("Aumenta la frecuencia de riego gradualmente")
            elif issue_type == 'falta_de_luz':
                recommendations.append("Mueve la planta a un lugar con más luz indirecta")
        
        if not recommendations:
            recommendations = [
                "Mantén un cronograma regular de riego",
                "Asegura que la planta reciba luz indirecta adecuada"
            ]
        
        return recommendations


if __name__ == "__main__":
    # Test
    agent = ResponseAgentLangChain(use_supabase=False)
    print("\n✓ Agente LangChain inicializado correctamente")

