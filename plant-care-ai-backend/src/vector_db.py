"""
Módulo de Base de Datos Vectorial
Integración con Supabase usando pgvector
"""
import os
from typing import List, Tuple, Optional
import numpy as np
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


class SupabaseVectorDB:
    """Base de datos vectorial usando Supabase con pgvector"""
    
    def __init__(self):
        """Inicializa conexión a Supabase"""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar en .env")
        
        self.client: Client = create_client(url, key)
        print("✓ Conectado a Supabase")
    
    def create_table(self, embedding_dim: int = 384):
        """
        Crea la tabla de documentos con soporte vectorial
        NOTA: Esto requiere que pgvector esté habilitado en Supabase
        
        Args:
            embedding_dim: Dimensión de los embeddings (384 para all-MiniLM-L6-v2)
        """
        # Esta operación se debe hacer una sola vez desde el SQL Editor de Supabase:
        # 
        # create extension if not exists vector;
        # 
        # create table if not exists plant_documents (
        #   id bigserial primary key,
        #   chunk_id text unique not null,
        #   source_file text not null,
        #   chunk_index int not null,
        #   text text not null,
        #   embedding vector(384),
        #   created_at timestamptz default now()
        # );
        # 
        # create index on plant_documents using ivfflat (embedding vector_cosine_ops);
        
        print("⚠ Ejecuta el SQL de creación de tabla en el SQL Editor de Supabase")
        print("Ver comentarios en el código para el SQL necesario")
    
    def insert_chunks(self, chunks: List[dict], embeddings: np.ndarray):
        """
        Inserta chunks con sus embeddings en Supabase
        
        Args:
            chunks: Lista de chunks con metadata
            embeddings: Array de embeddings correspondientes
        """
        records = []
        for chunk, embedding in zip(chunks, embeddings):
            record = {
                'chunk_id': chunk['chunk_id'],
                'source_file': chunk['source_file'],
                'chunk_index': chunk['chunk_index'],
                'text': chunk['text'],
                'embedding': embedding.tolist()  # Convertir a lista para JSON
            }
            records.append(record)
        
        # Insertar en batch
        result = self.client.table('plant_documents').insert(records).execute()
        print(f"✓ Insertados {len(records)} chunks en Supabase")
        return result
    
    def search_similar(self, query_embedding: np.ndarray, top_k: int = 5, threshold: float = 0.3) -> List[Tuple[dict, float]]:
        """
        Busca documentos similares usando pgvector
        
        Args:
            query_embedding: Embedding de la consulta
            top_k: Número de resultados
            threshold: Umbral mínimo de similitud
            
        Returns:
            Lista de (documento, score)
        """
        # Convertir embedding a lista
        query_vector = query_embedding.tolist()
        
        # Usar RPC para búsqueda vectorial personalizada
        # Primero necesitamos crear esta función en Supabase:
        #
        # create or replace function match_plant_documents (
        #   query_embedding vector(384),
        #   match_threshold float,
        #   match_count int
        # )
        # returns table (
        #   id bigint,
        #   chunk_id text,
        #   source_file text,
        #   text text,
        #   similarity float
        # )
        # language sql stable
        # as $$
        #   select
        #     id,
        #     chunk_id,
        #     source_file,
        #     text,
        #     1 - (embedding <=> query_embedding) as similarity
        #   from plant_documents
        #   where 1 - (embedding <=> query_embedding) > match_threshold
        #   order by embedding <=> query_embedding
        #   limit match_count;
        # $$;
        
        try:
            result = self.client.rpc(
                'match_plant_documents',
                {
                    'query_embedding': query_vector,
                    'match_threshold': threshold,
                    'match_count': top_k
                }
            ).execute()
            
            # Formatear resultados
            results = []
            for row in result.data:
                doc = {
                    'chunk_id': row['chunk_id'],
                    'source_file': row['source_file'],
                    'text': row['text']
                }
                score = row['similarity']
                results.append((doc, score))
            
            return results
        except Exception as e:
            print(f"Error en búsqueda: {e}")
            print("Asegúrate de crear la función match_plant_documents en Supabase")
            return []
    
    def clear_all(self):
        """Borra todos los documentos (útil para testing)"""
        result = self.client.table('plant_documents').delete().neq('id', 0).execute()
        print("✓ Base de datos limpiada")
        return result


if __name__ == "__main__":
    # Test
    db = SupabaseVectorDB()
    print("\n📝 Instrucciones:")
    print("1. Ve al SQL Editor en Supabase")
    print("2. Ejecuta los comandos SQL de create_table() y search_similar()")
    print("3. Luego podrás usar insert_chunks() y search_similar()")
