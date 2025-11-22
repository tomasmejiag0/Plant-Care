"""
Agente de Conocimiento
Busca información relevante en la base de datos vectorial de Supabase
"""
import sys
import os
from pathlib import Path

# Agregar src al path si no está
current_dir = Path(__file__).parent
src_dir = current_dir.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from typing import List, Dict
from embeddings import EmbeddingGenerator
from vector_db import SupabaseVectorDB


class KnowledgeAgent:
    """Agente responsable de recuperar conocimiento relevante"""
    
    def __init__(self, use_supabase: bool = True):
        """
        Inicializa el agente de conocimiento
        
        Args:
            use_supabase: Si True, usa Supabase; si False, usa búsqueda en memoria
        """
        self.embedding_generator = EmbeddingGenerator()
        self.use_supabase = use_supabase
        
        if use_supabase:
            try:
                self.vector_db = SupabaseVectorDB()
                print("✓ Conectado a Supabase para búsqueda vectorial")
            except Exception as e:
                print(f"⚠ Error conectando a Supabase: {e}")
                print("  Usando búsqueda en memoria como fallback")
                self.use_supabase = False
        
        if not self.use_supabase:
            # Fallback: búsqueda en memoria
            from similitud import SimilaritySearch
            self.similarity_search = SimilaritySearch()
            print("✓ Usando búsqueda en memoria")
    
    def search_knowledge(self, query: str, species: str = "", problems: List[str] = None, top_k: int = 5) -> List[Dict]:
        if problems is None:
            problems = []
        """
        Busca conocimiento relevante sobre la planta
        
        Args:
            query: Consulta principal
            species: Especie de la planta (opcional)
            problems: Problemas detectados (opcional)
            top_k: Número de resultados
            
        Returns:
            Lista de documentos relevantes
        """
        # Construir consulta mejorada
        enhanced_query = query
        if species:
            enhanced_query = f"{species} {query}"
        if problems:
            enhanced_query += f" problemas: {', '.join(problems)}"
        
        print(f"\n  Consulta: {enhanced_query}")
        
        # Generar embedding de la consulta
        query_embedding = self.embedding_generator.generate_embedding(enhanced_query)
        
        # Buscar en base de datos vectorial
        # Reducido threshold de 0.3 a 0.25 para encontrar más documentos relevantes
        if self.use_supabase:
            results = self.vector_db.search_similar(query_embedding, top_k=top_k, threshold=0.25)
        else:
            results = self.similarity_search.search(query_embedding, top_k=top_k, threshold=0.25)
        
        # Formatear resultados
        documents = []
        for doc, score in results:
            documents.append({
                'text': doc.get('text', ''),
                'source': doc.get('source_file', 'desconocido'),
                'relevance_score': score
            })
        
        return documents
    
    def search_direct(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Búsqueda directa sin contexto de visión
        
        Args:
            query: Consulta del usuario
            top_k: Número de resultados
            
        Returns:
            Lista de documentos relevantes
        """
        return self.search_knowledge(query, species="", problems=[], top_k=top_k)
    
    def execute(self, vision_result: Dict, user_actions: str = "") -> Dict:
        """
        Ejecuta el agente de conocimiento
        
        Args:
            vision_result: Resultado del agente de visión
            user_actions: Acciones del usuario con la planta
            
        Returns:
            Conocimiento relevante encontrado
        """
        print(f"\n📚 AGENTE DE CONOCIMIENTO ejecutando...")
        
        species = vision_result.get('species', 'planta desconocida')
        problems = vision_result.get('visual_problems', [])
        
        # Buscar información relevante
        documents = self.search_knowledge(
            query=user_actions,
            species=species,
            problems=problems,
            top_k=5
        )
        
        print(f"  ✓ Encontrados {len(documents)} documentos relevantes")
        
        # Extraer contexto más relevante
        context = "\n\n".join([
            f"[Relevancia: {doc['relevance_score']:.2f}] {doc['text']}"
            for doc in documents[:3]  # Top 3
        ])
        
        return {
            'agent': 'KnowledgeAgent',
            'documents': documents,
            'context': context,
            'num_results': len(documents)
        }


if __name__ == "__main__":
    # Test
    agent = KnowledgeAgent(use_supabase=False)
    
    # Simular resultado de vision
    vision_result = {
        'species': 'Suculenta',
        'visual_problems': ['hojas amarillas', 'manchas marrones']
    }
    
    result = agent.execute(vision_result, "He estado regando cada día")
    print(f"\nContexto recuperado:\n{result['context'][:200]}...")
