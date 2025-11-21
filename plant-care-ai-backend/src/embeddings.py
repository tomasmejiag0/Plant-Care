"""
Módulo de Embeddings
Genera embeddings vectoriales usando sentence-transformers
"""
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union


class EmbeddingGenerator:
    """Genera embeddings usando modelos de sentence-transformers"""
    
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        """
        Inicializa el generador de embeddings
        
        Args:
            model_name: Nombre del modelo de sentence-transformers
                       'all-MiniLM-L6-v2' genera embeddings de 384 dimensiones
        """
        print(f"Cargando modelo de embeddings: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"✓ Modelo cargado. Dimensiones: {self.embedding_dim}")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Genera embedding para un texto
        
        Args:
            text: Texto a convertir en embedding
            
        Returns:
            Vector numpy de embedding normalizado
        """
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding
    
    def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """
        Genera embeddings para múltiples textos (más eficiente)
        
        Args:
            texts: Lista de textos
            
        Returns:
            Array numpy de embeddings normalizados
        """
        embeddings = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
        return embeddings
    
    def cosine_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calcula similitud del coseno entre dos embeddings
        
        Args:
            embedding1: Primer vector
            embedding2: Segundo vector
            
        Returns:
            Similitud (0-1, donde 1 es más similar)
        """
        # Si ya están normalizados, el producto punto es la similitud del coseno
        similarity = np.dot(embedding1, embedding2)
        return float(similarity)


if __name__ == "__main__":
    # Test
    generator = EmbeddingGenerator()
    
    text1 = "Las suculentas necesitan poco riego"
    text2 = "Las plantas crasas requieren poca agua"
    text3 = "Los cactus necesitan mucha luz solar"
    
    emb1 = generator.generate_embedding(text1)
    emb2 = generator.generate_embedding(text2)
    emb3 = generator.generate_embedding(text3)
    
    print(f"\nDimensión de embedding: {len(emb1)}")
    print(f"Similitud texto1-texto2: {generator.cosine_similarity(emb1, emb2):.3f}")
    print(f"Similitud texto1-texto3: {generator.cosine_similarity(emb1, emb3):.3f}")
