"""
Agente de Respuesta (Orquestador)
Coordina todos los agentes y genera la respuesta final usando LangChain
"""
import sys
sys.path.append('..')

import os
from typing import Dict
from dotenv import load_dotenv
import google.generativeai as genai

from agente_vision import VisionAgent
from agente_conocimiento import KnowledgeAgent
from agente_analisis import AnalysisAgent

load_dotenv()


class ResponseAgent:
    """Agente orquestador que coordina el flujo y genera respuesta final"""
    
    def __init__(self, use_supabase: bool = True):
        """
        Inicializa el agente de respuesta y todos los sub-agentes
        
        Args:
            use_supabase: Si usar Supabase o búsqueda en memoria
        """
        print("\n🤖 Inicializando Sistema Multi-Agente...")
        
        # Inicializar agentes
        self.vision_agent = VisionAgent()
        self.knowledge_agent = KnowledgeAgent(use_supabase=use_supabase)
        self.analysis_agent = AnalysisAgent()
        
        # Configurar LLM para respuesta final (Gemini)
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            genai.configure(api_key=gemini_key)
            # Listar modelos disponibles y usar el primero disponible
            self.llm = None
            try:
                available_models = []
                for model in genai.list_models():
                    if 'generateContent' in model.supported_generation_methods:
                        model_name = model.name.split('/')[-1]  # Extraer solo el nombre
                        available_models.append(model_name)
                
                if available_models:
                    print(f"📋 Modelos Gemini disponibles: {', '.join(available_models)}")
                    
                    # Intentar modelos en orden de preferencia (evitar modelos exp/preview que tienen cuota limitada)
                    preferred_models = ['gemini-pro', 'gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
                    
                    # Filtrar modelos disponibles para excluir exp/preview/experimental
                    stable_models = [m for m in available_models if not any(x in m.lower() for x in ['exp', 'preview', 'experimental', 'thinking'])]
                    
                    for model_name in preferred_models:
                        if model_name in stable_models:
                            try:
                                self.llm = genai.GenerativeModel(model_name)
                                print(f"✓ Gemini LLM ({model_name}) configurado para respuesta final")
                                break
                            except Exception as e:
                                print(f"⚠ Error probando {model_name}: {e}")
                                continue
                    
                    # Si ninguno funcionó, intentar el primer modelo estable disponible
                    if not self.llm and stable_models:
                        try:
                            first_stable = stable_models[0]
                            self.llm = genai.GenerativeModel(first_stable)
                            print(f"✓ Gemini LLM ({first_stable}) configurado para respuesta final")
                        except Exception as e:
                            print(f"⚠ Error configurando Gemini LLM con {first_stable}: {e}")
                            self.llm = None
                    elif not self.llm:
                        print("⚠ No hay modelos estables disponibles (solo exp/preview)")
                        self.llm = None
                else:
                    print("⚠ No se encontraron modelos Gemini disponibles")
                    self.llm = None
            except Exception as e:
                print(f"⚠ Error listando modelos de Gemini: {e}")
                print("   El sistema funcionará sin LLM, usando solo documentos de Supabase")
                self.llm = None
        else:
            self.llm = None
            print("⚠ GEMINI_API_KEY no encontrada - respuestas limitadas (sin LLM)")
        
        print("✓ Sistema Multi-Agente listo\n")
    
    def generate_recommendations(self, analysis_result: Dict, context: str, user_question: str = "") -> list:
        """
        Genera recomendaciones usando el LLM
        
        Args:
            analysis_result: Resultado del análisis
            context: Contexto del knowledge agent
            user_question: Pregunta o preocupación específica del usuario
            
        Returns:
            Lista de recomendaciones
        """
        if not self.llm:
            # Recomendaciones predeterminadas sin LLM
            return self._get_default_recommendations(analysis_result, user_question)
        
        try:
            # Construir prompt para recomendaciones
            user_context = f"\n\nPREGUNTA/PRECUPACIÓN DEL USUARIO:\n{user_question}" if user_question else ""
            
            prompt = f"""Eres un experto en cuidado de plantas. Basándote en el siguiente análisis, 
genera 3-5 recomendaciones específicas y accionables para mejorar la salud de la planta.

ANÁLISIS:
- Especie: {analysis_result.get('species')}
- Estado: {analysis_result.get('overall_status')}
- Diagnóstico: {analysis_result.get('diagnosis')}
- Problemas visuales: {', '.join(analysis_result.get('visual_problems', []))}
- Problemas identificados: {analysis_result.get('identified_issues', [])}
{user_context}

CONOCIMIENTO RELEVANTE:
{context[:500]}

IMPORTANTE: Si el usuario menciona una preocupación específica (como "arranqué una hoja", "creo que la maté", etc.), 
DEBES abordar esa preocupación directamente en las recomendaciones. Tranquiliza al usuario y proporciona 
consejos específicos sobre cómo manejar la situación.

Genera recomendaciones en el siguiente formato:
1. [Recomendación específica que aborde la preocupación del usuario si existe]
2. [Recomendación específica]
...

Sé conciso, práctico, específico y empático."""

            response = self.llm.generate_content(prompt)
            recommendations_text = response.text
            
            # Parsear recomendaciones
            recommendations = []
            for line in recommendations_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Limpiar numeración
                    rec = line.lstrip('0123456789.-) ').strip()
                    if rec:
                        recommendations.append(rec)
            
            return recommendations[:5]  # Máximo 5
            
        except Exception as e:
            print(f"Error generando recomendaciones con LLM: {e}")
            return self._get_default_recommendations(analysis_result, user_question)
    
    def _get_default_recommendations(self, analysis_result: Dict, user_question: str = "") -> list:
        """Recomendaciones predeterminadas sin LLM"""
        recommendations = []
        
        # Si el usuario menciona preocupaciones específicas, abordarlas primero
        user_lower = user_question.lower() if user_question else ""
        
        if "arranqué" in user_lower or "arranque" in user_lower or "hoja" in user_lower:
            recommendations.append("No te preocupes, arrancar una hoja accidentalmente generalmente no mata la planta. La mayoría de las plantas pueden recuperarse de esto.")
            recommendations.append("Si la herida es grande, puedes aplicar canela en polvo o carbón activado en el área cortada para prevenir infecciones.")
            recommendations.append("Mantén la planta en condiciones normales y observa si aparecen signos de estrés. La mayoría de las plantas se recuperan solas.")
        
        if "maté" in user_lower or "mate" in user_lower or "muerte" in user_lower:
            recommendations.append("Es poco probable que la planta esté muerta por un solo incidente. Las plantas son más resistentes de lo que parecen.")
            recommendations.append("Observa la planta durante los próximos días. Si las hojas se mantienen verdes y firmes, la planta está bien.")
            recommendations.append("Si notas que las hojas se marchitan o se vuelven amarillas, puede ser signo de estrés, pero aún es recuperable con los cuidados adecuados.")
        
        issues = analysis_result.get('identified_issues', [])
        
        for issue in issues:
            issue_type = issue.get('type', '')
            
            if issue_type == 'exceso_de_riego':
                recommendations.append("Reduce la frecuencia de riego. Las suculentas necesitan que la tierra se seque completamente entre riegos.")
                recommendations.append("Verifica que la maceta tenga buen drenaje")
            elif issue_type == 'falta_de_riego':
                recommendations.append("Aumenta la frecuencia de riego gradualmente")
                recommendations.append("Riega cuando la tierra esté seca al tacto")
            elif issue_type == 'falta_de_luz':
                recommendations.append("Mueve la planta a un lugar con más luz indirecta")
            elif issue_type == 'exceso_de_luz':
                recommendations.append("Protege la planta de luz solar directa en horas pico")
        
        if not recommendations:
            recommendations.append("Mantén un cronograma regular de riego")
            recommendations.append("Asegura que la planta reciba luz indirecta adecuada")
        
        return recommendations
    
    def execute(self, image_path: str, user_actions: str = "") -> Dict:
        """
        Ejecuta el flujo completo de agentes (orquestación)
        
        Args:
            image_path: Ruta a la imagen de la planta
            user_actions: Descripción de acciones del usuario
            
        Returns:
            Respuesta final completa
        """
        print("=" * 60)
        print("🌱 INICIANDO ANÁLISIS DE PLANTA")
        print("=" * 60)
        
        try:
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
            
            # 4. GENERAR RECOMENDACIONES
            print(f"\n💡 Generando recomendaciones...")
            recommendations = self.generate_recommendations(
                analysis_result,
                knowledge_result.get('context', ''),
                user_actions  # Pasar la pregunta/preocupación del usuario
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
                    'response_agent': 'completed'
                }
            }
            
            print("\n" + "=" * 60)
            print("✅ ANÁLISIS COMPLETADO")
            print("=" * 60)
            print(f"   Especie: {final_response['plant_info']['species']}")
            print(f"   Salud: {final_response['health_assessment']['score']}/10")
            print(f"   Recomendaciones: {len(recommendations)}")
            print("=" * 60 + "\n")
            
            return final_response
            
        except Exception as e:
            print(f"\n❌ Error en flujo de agentes: {e}")
            return {
                'success': False,
                'error': str(e)
            }


if __name__ == "__main__":
    # Test del sistema completo
    agent = ResponseAgent(use_supabase=False)
    
    print("\n📝 Para probar el sistema completo:")
    print("1. Coloca una imagen de planta en test_plant.jpg")
    print("2. Ejecuta: python agente_respuesta.py")
    print("3. El sistema ejecutará los 4 agentes en secuencia\n")
