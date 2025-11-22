"""
LLM Local para Modo Demo
Usa Ollama u otros LLMs locales para generar respuestas sin depender de APIs externas
"""
import os
import requests
from typing import Optional, Dict, List
import json


class LocalLLM:
    """Wrapper para LLMs locales (Ollama, Hugging Face, etc.)"""
    
    def __init__(self, provider: str = "ollama", model: str = "llama3.2"):
        """
        Inicializa el LLM local
        
        Args:
            provider: "ollama" o "huggingface"
            model: Nombre del modelo a usar
        """
        self.provider = provider
        self.model = model
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.available = False
        
        if provider == "ollama":
            self.available = self._check_ollama()
        elif provider == "huggingface":
            self.available = self._check_huggingface()
    
    def _check_ollama(self) -> bool:
        """Verifica si Ollama está disponible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                print(f"[OK] Ollama disponible con {len(models)} modelos")
                # Verificar si el modelo solicitado está disponible
                model_names = [m.get("name", "") for m in models]
                if self.model not in model_names:
                    # Intentar con modelos alternativos
                    alternatives = ["llama3.2", "llama3.2:1b", "mistral", "phi3", "gemma2:2b"]
                    for alt in alternatives:
                        if any(alt in name for name in model_names):
                            self.model = alt
                            print(f"[OK] Usando modelo alternativo: {self.model}")
                            break
                    else:
                        print(f"[WARN] Modelo {self.model} no encontrado. Usa: ollama pull {self.model}")
                        return False
                return True
        except Exception as e:
            print(f"[WARN] Ollama no disponible: {e}")
            print("   Instala Ollama desde https://ollama.ai y ejecuta: ollama pull llama3.2")
            return False
    
    def _check_huggingface(self) -> bool:
        """Verifica si Hugging Face está disponible"""
        # Implementación futura
        return False
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> Optional[str]:
        """
        Genera una respuesta usando el LLM local
        
        Args:
            prompt: Prompt para el LLM
            max_tokens: Máximo de tokens a generar
            temperature: Temperatura para la generación (0.0-1.0)
            
        Returns:
            Respuesta generada o None si hay error
        """
        if not self.available:
            return None
        
        if self.provider == "ollama":
            return self._generate_ollama(prompt, max_tokens, temperature)
        elif self.provider == "huggingface":
            return self._generate_huggingface(prompt, max_tokens, temperature)
        
        return None
    
    def _generate_ollama(self, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Genera respuesta usando Ollama"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                print(f"[ERROR] Error de Ollama: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"[ERROR] Error generando con Ollama: {e}")
            return None
    
    def _generate_huggingface(self, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Genera respuesta usando Hugging Face (implementación futura)"""
        # TODO: Implementar usando transformers
        return None


def get_local_llm() -> Optional[LocalLLM]:
    """
    Intenta inicializar un LLM local disponible
    
    Returns:
        LocalLLM si está disponible, None si no
    """
    # Intentar Ollama primero (más fácil de usar)
    ollama = LocalLLM(provider="ollama", model="llama3.2")
    if ollama.available:
        return ollama
    
    # Intentar con modelo más pequeño si llama3.2 no está disponible
    ollama_small = LocalLLM(provider="ollama", model="llama3.2:1b")
    if ollama_small.available:
        return ollama_small
    
    # Intentar otros modelos comunes
    for model in ["mistral", "phi3", "gemma2:2b"]:
        ollama_alt = LocalLLM(provider="ollama", model=model)
        if ollama_alt.available:
            return ollama_alt
    
    return None

