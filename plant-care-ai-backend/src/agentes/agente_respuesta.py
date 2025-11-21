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
            self.llm = genai.GenerativeModel('gemini-1.5-pro')
            print("✓ Gemini LLM configurado para respuesta final")
        else:
            self.llm = None
            print("⚠ GEMINI_API_KEY no encontrada - respuestas limitadas")
        
        print("✓ Sistema Multi-Agente listo\n")
    
    def generate_recommendations(self, analysis_result: Dict, context: str) -> list:
        """
        Genera recomendaciones usando el LLM
        
        Args:
            analysis_result: Resultado del análisis
            context: Contexto del knowledge agent
            
        Returns:
            Lista de recomendaciones
        """
        if not self.llm:
            # Recomendaciones predeterminadas sin LLM
            return self._get_default_recommendations(analysis_result)
        
        try:
            # Construir prompt para recomendaciones
            prompt = f"""Eres un experto en cuidado de plantas. Basándote en el siguiente análisis, 
genera 3-5 recomendaciones específicas y accionables para mejorar la salud de la planta.

ANÁLISIS:
- Especie: {analysis_result.get('species')}
- Estado: {analysis_result.get('overall_status')}
- Diagnóstico: {analysis_result.get('diagnosis')}
- Problemas visuales: {', '.join(analysis_result.get('visual_problems', []))}
- Problemas identificados: {analysis_result.get('identified_issues', [])}

CONOCIMIENTO RELEVANTE:
{context[:500]}

Genera recomendaciones en el siguiente formato:
1. [Recomendación específica]
2. [Recomendación específica]
...

Sé conciso, práctico y específico."""

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
            return self._get_default_recommendations(analysis_result)
    
    def _get_default_recommendations(self, analysis_result: Dict) -> list:
        """Recomendaciones predeterminadas sin LLM"""
        recommendations = []
        
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
