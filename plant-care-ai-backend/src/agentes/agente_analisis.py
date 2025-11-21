"""
Agente de Análisis
Combina información visual, acciones del usuario y conocimiento para diagnosticar
"""
from typing import Dict, List
import json


class AnalysisAgent:
    """Agente responsable de analizar y diagnosticar problemas de la planta"""
    
    def __init__(self):
        """Inicializa el agente de análisis"""
        print("✓ Agente de Análisis inicializado")
    
    def analyze_watering(self, user_actions: str, problems: List[str]) -> Dict:
        """Analiza problemas relacionados con riego"""
        keywords_overwater = ['riego cada día', 'mucha agua', 'riego diario', 'mucho riego']
        keywords_underwater = ['poco riego', 'no he regado', 'seca', 'falta agua']
        
        actions_lower = user_actions.lower()
        
        watering_issue = None
        severity = 0
        
        # Detectar exceso de riego
        if any(kw in actions_lower for kw in keywords_overwater):
            watering_issue = 'exceso_de_riego'
            severity = 8
            # Confirmar con problemas visuales
            if any(p in ['hojas amarillas', 'manchas marrones', 'pudrición'] for p in problems):
                severity = 9
        
        # Detectar falta de riego
        elif any(kw in actions_lower for kw in keywords_underwater):
            watering_issue = 'falta_de_riego'
            severity = 6
            if any(p in ['hojas secas', 'marchitas'] for p in problems):
                severity = 8
        
        return {
            'issue': watering_issue,
            'severity': severity
        }
    
    def analyze_light(self, problems: List[str]) -> Dict:
        """Analiza problemas relacionados con luz"""
        light_issue = None
        severity = 0
        
        if 'hojas pálidas' in problems or 'crecimiento lento' in problems:
            light_issue = 'falta_de_luz'
            severity = 5
        elif 'hojas quemadas' in problems or 'manchas blancas' in problems:
            light_issue = 'exceso_de_luz'
            severity = 6
        
        return {
            'issue': light_issue,
            'severity': severity
        }
    
    def calculate_health_score(self, visual_score: int, problems_count: int, severity: int) -> int:
        """Calcula puntuación final de salud"""
        # Base: puntuación visual
        score = visual_score
        
        # Penalizar por problemas
        score -= problems_count * 0.5
        
        # Penalizar por severidad
        score -= severity * 0.3
        
        # Mantener en rango 1-10
        return max(1, min(10, int(score)))
    
    def execute(self, vision_result: Dict, knowledge_result: Dict, user_actions: str = "") -> Dict:
        """
        Ejecuta el análisis completo
        
        Args:
            vision_result: Resultado del agente de visión
            knowledge_result: Resultado del agente de conocimiento
            user_actions: Acciones del usuario
            
        Returns:
            Diagnóstico completo
        """
        print(f"\n🔬 AGENTE DE ANÁLISIS ejecutando...")
        
        # Extraer información
        species = vision_result.get('species', 'Desconocida')
        visual_score = vision_result.get('health_score', 5)
        problems = vision_result.get('visual_problems', [])
        
        # Análisis de riego
        watering_analysis = self.analyze_watering(user_actions, problems)
        
        # Análisis de luz
        light_analysis = self.analyze_light(problems)
        
        # Identificar todos los problemas
        identified_issues = []
        max_severity = 0
        
        if watering_analysis['issue']:
            identified_issues.append({
                'type': watering_analysis['issue'],
                'severity': watering_analysis['severity']
            })
            max_severity = max(max_severity, watering_analysis['severity'])
        
        if light_analysis['issue']:
            identified_issues.append({
                'type': light_analysis['issue'],
                'severity': light_analysis['severity']
            })
            max_severity = max(max_severity, light_analysis['severity'])
        
        # Calcular puntuación final
        final_health_score = self.calculate_health_score(
            visual_score,
            len(problems),
            max_severity
        )
        
        # Estado general
        if final_health_score >= 8:
            overall_status = "Excelente"
        elif final_health_score >= 6:
            overall_status = "Bueno"
        elif final_health_score >= 4:
            overall_status = "Regular - Requiere atención"
        else:
            overall_status = "Crítico - Acción inmediata necesaria"
        
        # Diagnóstico
        diagnosis = f"La {species} presenta "
        if identified_issues:
            issue_names = [issue['type'].replace('_', ' ') for issue in identified_issues]
            diagnosis += ', '.join(issue_names)
        else:
            diagnosis += "un estado general saludable"
        
        print(f"  ✓ Diagnóstico: {diagnosis}")
        print(f"  ✓ Puntuación final: {final_health_score}/10")
        print(f"  ✓ Problemas identificados: {len(identified_issues)}")
        
        return {
            'agent': 'AnalysisAgent',
            'species': species,
            'health_score': final_health_score,
            'overall_status': overall_status,
            'diagnosis': diagnosis,
            'identified_issues': identified_issues,
            'visual_problems': problems,
            'context_used': knowledge_result.get('num_results', 0)
        }


if __name__ == "__main__":
    # Test
    agent = AnalysisAgent()
    
    vision = {
        'species': 'Suculenta',
        'health_score': 6,
        'visual_problems': ['hojas amarillas', 'manchas marrones']
    }
    
    knowledge = {
        'num_results': 3,
        'context': 'Las suculentas requieren poco riego...'
    }
    
    result = agent.execute(vision, knowledge, "He estado regando cada día")
    print(f"\nResultado:\n{json.dumps(result, indent=2, ensure_ascii=False)}")
