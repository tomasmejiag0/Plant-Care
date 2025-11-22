"""
Agente de Visión
Analiza imágenes de plantas usando Google Gemini Vision y Plant.id API
"""
import os
import base64
import requests
from typing import Dict, Optional
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()


class VisionAgent:
    """Agente responsable de analizar imágenes de plantas"""
    
    def __init__(self):
        """Inicializa el agente con APIs de visión"""
        # Configurar Gemini
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            genai.configure(api_key=gemini_key)
            # Listar modelos disponibles y usar el primero disponible
            try:
                available_models = [model.name for model in genai.list_models() 
                                  if 'generateContent' in model.supported_generation_methods]
                
                # Intentar modelos en orden de preferencia
                model_names = ['models/gemini-pro', 'models/gemini-1.5-pro', 'models/gemini-1.5-flash', 'gemini-pro']
                self.gemini_model = None
                
                for model_name in model_names:
                    # Verificar si el modelo está disponible
                    if any(model_name.replace('models/', '') in m or m.endswith(model_name.replace('models/', '')) for m in available_models):
                        try:
                            self.gemini_model = genai.GenerativeModel(model_name.replace('models/', ''))
                            print(f"✓ Gemini Vision ({model_name}) inicializado")
                            break
                        except Exception as e:
                            continue
                
                if not self.gemini_model:
                    # Último intento con el primer modelo disponible
                    if available_models:
                        try:
                            first_model = available_models[0].split('/')[-1]
                            self.gemini_model = genai.GenerativeModel(first_model)
                            print(f"✓ Gemini Vision ({first_model}) inicializado")
                        except Exception as e:
                            print(f"⚠ Error configurando Gemini Vision: {e}")
                            self.gemini_model = None
                    else:
                        print("⚠ No se encontraron modelos disponibles para Vision")
                        self.gemini_model = None
            except Exception as e:
                print(f"⚠ Error listando modelos de Gemini: {e}")
                # Fallback: intentar gemini-pro directamente
                try:
                    self.gemini_model = genai.GenerativeModel('gemini-pro')
                    print("✓ Gemini Vision (gemini-pro) inicializado (fallback)")
                except Exception as e2:
                    print(f"⚠ Error configurando Gemini Vision: {e2}")
                    self.gemini_model = None
        else:
            self.gemini_model = None
            print("⚠ GEMINI_API_KEY no encontrada")
        
        # API Key de Plant.id
        self.plant_id_key = os.getenv("PLANT_ID_API_KEY")
        if not self.plant_id_key:
            print("⚠ PLANT_ID_API_KEY no encontrada")
    
    def identify_plant_species(self, image_path: str) -> Optional[Dict]:
        """
        Identifica la especie de planta usando Plant.id API o Gemini Vision como fallback
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            Diccionario con especie y probabilidad
        """
        # Intentar primero con Plant.id API si está disponible
        if self.plant_id_key:
            try:
                print("  🔍 Identificando especie con Plant.id API...")
                # Leer y codificar imagen
                with open(image_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                
                # Llamada a Plant.id API
                url = "https://api.plant.id/v2/identify"
                headers = {
                    "Content-Type": "application/json",
                    "Api-Key": self.plant_id_key
                }
                data = {
                    "images": [f"data:image/jpeg;base64,{image_data}"],
                    "modifiers": ["similar_images"],
                    "plant_details": ["common_names", "taxonomy", "url"]
                }
                
                response = requests.post(url, json=data, headers=headers, timeout=10)
                response.raise_for_status()
                result = response.json()
                
                if 'suggestions' in result and len(result['suggestions']) > 0:
                    top_match = result['suggestions'][0]
                    species_name = top_match.get('plant_name', 'Desconocida')
                    probability = top_match.get('probability', 0)
                    common_names = top_match.get('plant_details', {}).get('common_names', [])
                    
                    print(f"  ✓ Plant.id identificó: {species_name} (confianza: {probability:.0%})")
                    
                    return {
                        'species': species_name,
                        'probability': probability,
                        'common_names': common_names
                    }
                else:
                    print("  ⚠ Plant.id no encontró sugerencias")
            except requests.exceptions.RequestException as e:
                print(f"  ⚠ Error en Plant.id API (HTTP): {e}")
            except Exception as e:
                print(f"  ⚠ Error en Plant.id API: {e}")
        else:
            print("  ⚠ PLANT_ID_API_KEY no configurada")
        
        # Fallback: usar Gemini Vision para identificar la planta
        if self.gemini_model:
            try:
                print("  🔍 Intentando identificación con Gemini Vision...")
                from PIL import Image
                img = Image.open(image_path)
                
                prompt = """Identifica la especie de esta planta. Responde SOLO con el nombre científico (género y especie) o el nombre común más conocido si no conoces el científico.

Formato de respuesta:
ESPECIE: [nombre científico o común]
CONFIANZA: [alto/medio/bajo]

Si no puedes identificar la planta, responde:
ESPECIE: Desconocida
CONFIANZA: bajo"""
                
                response = self.gemini_model.generate_content([prompt, img])
                analysis_text = response.text
                
                # Parsear respuesta
                species = "Desconocida"
                confidence = 0.3  # Baja confianza para identificación con Gemini Vision
                
                for line in analysis_text.split('\n'):
                    if line.startswith('ESPECIE:'):
                        species = line.replace('ESPECIE:', '').strip()
                    elif line.startswith('CONFIANZA:'):
                        conf_text = line.replace('CONFIANZA:', '').strip().lower()
                        if 'alto' in conf_text:
                            confidence = 0.6
                        elif 'medio' in conf_text:
                            confidence = 0.4
                        else:
                            confidence = 0.3
                
                if species and species != "Desconocida":
                    print(f"  ✓ Gemini Vision identificó: {species} (confianza estimada: {confidence:.0%})")
                    return {
                        'species': species,
                        'probability': confidence,
                        'common_names': []
                    }
            except Exception as e:
                print(f"  ⚠ Error en identificación con Gemini Vision: {e}")
        
        print("  ⚠ No se pudo identificar la especie")
        return None
    
    def analyze_plant_health(self, image_path: str, user_actions: str = "") -> Dict:
        """
        Analiza la salud de la planta usando Gemini Vision
        
        Args:
            image_path: Ruta a la imagen
            user_actions: Descripción de lo que el usuario ha hecho con la planta
            
        Returns:
            Análisis visual de la planta
        """
        if not self.gemini_model:
            return {
                'health_status': 'No se pudo analizar (falta API key)',
                'visual_problems': [],
                'health_score': 5
            }
        
        try:
            # Cargar imagen
            from PIL import Image
            img = Image.open(image_path)
            
            # Prompt para Gemini
            prompt = f"""Eres un experto botánico. Analiza esta imagen de planta y proporciona:
1. Estado visual de salud (excelente/bueno/regular/malo/crítico)
2. Problemas visuales detectados (manchas, hojas amarillas, plagas, etc.)
3. Puntuación de salud del 1-10
4. Observaciones sobre color de hojas, tallo, tierra

Contexto del usuario: {user_actions if user_actions else "Sin información adicional"}

Responde en formato:
ESTADO: [estado]
PROBLEMAS: [lista de problemas separados por comas, o "ninguno"]
PUNTUACIÓN: [número del 1-10]
OBSERVACIONES: [detalles visuales]"""
            
            response = self.gemini_model.generate_content([prompt, img])
            analysis_text = response.text
            
            # Parsear respuesta
            result = self._parse_gemini_response(analysis_text)
            return result
            
        except Exception as e:
            print(f"Error en Gemini Vision: {e}")
            return {
                'health_status': 'Error en análisis',
                'visual_problems': [],
                'health_score': 5,
                'observations': str(e)
            }
    
    def _parse_gemini_response(self, text: str) -> Dict:
        """Parsea la respuesta de Gemini"""
        lines = text.split('\n')
        result = {
            'health_status': 'Desconocido',
            'visual_problems': [],
            'health_score': 5,
            'observations': ''
        }
        
        for line in lines:
            if line.startswith('ESTADO:'):
                result['health_status'] = line.replace('ESTADO:', '').strip()
            elif line.startswith('PROBLEMAS:'):
                problems = line.replace('PROBLEMAS:', '').strip()
                if problems.lower() != 'ninguno':
                    result['visual_problems'] = [p.strip() for p in problems.split(',')]
            elif line.startswith('PUNTUACIÓN:'):
                try:
                    score = line.replace('PUNTUACIÓN:', '').strip()
                    result['health_score'] = int(score.split('/')[0])
                except:
                    result['health_score'] = 5
            elif line.startswith('OBSERVACIONES:'):
                result['observations'] = line.replace('OBSERVACIONES:', '').strip()
        
        return result
    
    def execute(self, image_path: str, user_actions: str = "") -> Dict:
        """
        Ejecuta el agente completo: identificación + análisis
        
        Args:
            image_path: Ruta a la imagen de la planta
            user_actions: Lo que el usuario ha hecho con la planta
            
        Returns:
            Análisis completo
        """
        print(f"\n🔍 AGENTE DE VISIÓN ejecutando...")
        
        # 1. Identificar especie
        species_info = self.identify_plant_species(image_path)
        
        # 2. Analizar salud
        health_info = self.analyze_plant_health(image_path, user_actions)
        
        # Combinar resultados
        result = {
            'agent': 'VisionAgent',
            'species': species_info.get('species', 'Desconocida') if species_info else 'Desconocida',
            'species_probability': species_info.get('probability', 0) if species_info else 0,
            'common_names': species_info.get('common_names', []) if species_info else [],
            **health_info
        }
        
        print(f"  ✓ Especie identificada: {result['species']} (confianza: {result['species_probability']:.0%})")
        print(f"  ✓ Estado de salud: {result['health_status']} ({result['health_score']}/10)")
        
        return result


if __name__ == "__main__":
    # Test
    agent = VisionAgent()
    print("\n📝 Para probar, coloca una imagen en test_plant.jpg")
