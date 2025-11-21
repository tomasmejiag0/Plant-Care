"""
Módulo de Similitud
Implementa búsqueda por similitud del coseno
"""
import numpy as np
from typing import List, Tuple


class SimilaritySearch:
    """Búsqueda de documentos similares usando similitud del coseno"""
    
    def __init__(self):
        self.embeddings = None
        self.documents = None
    
    def add_documents(self, embeddings: np.ndarray, documents: List[dict]):
        """
        Agrega documentos y sus embeddings para búsqueda
        
        Args:
            embeddings: Array de embeddings (n_docs x embedding_dim)
            documents: Lista de documentos correspondientes
        """
        self.embeddings = embeddings
        self.documents = documents
        print(f"✓ Indexados {len(documents)} documentos para búsqueda")
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5, threshold: float = 0.3) -> List[Tuple[dict, float]]:
        """
        Busca documentos más similares a la consulta
        
        Args:
            query_embedding: Embedding de la consulta
            top_k: Número de resultados a retornar
            threshold: Umbral mínimo de similitud (0-1)
            
        Returns:
            Lista de tuplas (documento, score) ordenadas por similitud
        """
        if self.embeddings is None:
            return []
        
        # Calcular similitud del coseno con todos los documentos
        # Como los embeddings están normalizados, el producto punto = similitud coseno
        similarities = np.dot(self.embeddings, query_embedding)
        
        # Obtener índices de los top_k más similares
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Filtrar por umbral y preparar resultados
        results = []
        for idx in top_indices:
            score = similarities[idx]
            if score >= threshold:
                results.append((self.documents[idx], float(score)))
        
        return results


if __name__ == "__main__":
    # Test
    from embeddings import EmbeddingGenerator
    
    generator = EmbeddingGenerator()
    search = SimilaritySearch()
    
    # Documentos de ejemplo
    docs = [
        {'text': 'Las suculentas necesitan poco riego', 'id': 1},
        {'text': 'Los cactus requieren mucha luz solar directa', 'id': 2},
        {'text': 'Las plantas de interior prefieren sombra', 'id': 3},
        {'text': 'El exceso de agua mata las suculentas', 'id': 4}
    ]
    
    # Generar embeddings
    texts = [d['text'] for d in docs]
    embeddings = generator.generate_embeddings_batch(texts)
    
    # Indexar
    search.add_documents(embeddings, docs)
    
    # Buscar
    query = "problemas con regar demasiado mis plantas crasas"
    query_emb = generator.generate_embedding(query)
    results = search.search(query_emb, top_k=3)
    
    print(f"\nConsulta: {query}")
    print("\nResultados:")
    for doc, score in results:
        print(f"  [{score:.3f}] {doc['text']}")
