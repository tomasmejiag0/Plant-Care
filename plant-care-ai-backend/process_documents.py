"""
Script para procesar documentos e indexarlos en Supabase
"""
import sys
sys.path.append('src')

from extraccion import DataExtractor
from chunking import TextChunker
from embeddings import EmbeddingGenerator
from vector_db import SupabaseVectorDB


def process_and_index_documents():
    """Procesa todos los documentos y los indexa en Supabase"""
    print("\n" + "="*60)
    print("📚 PROCESANDO DOCUMENTOS DE CONOCIMIENTO")
    print("="*60 + "\n")
    
    # 1. Extraer documentos
    extractor = DataExtractor(data_dir="data/plantas")
    documents = extractor.extract_all_documents()
    
    if not documents:
        print("⚠ No se encontraron documentos en data/plantas/")
        return
    
    # 2. Dividir en chunks
    print(f"\n📝 Dividiendo documentos en chunks...")
    chunker = TextChunker(chunk_size=400, overlap=50)
    
    all_chunks = []
    for doc in documents:
        chunks = chunker.chunk_document(doc)
        all_chunks.extend(chunks)
        print(f"  ✓ {doc['filename']}: {len(chunks)} chunks")
    
    print(f"\n✅ Total chunks creados: {len(all_chunks)}")
    
    # 3. Generar embeddings
    print(f"\n🧮 Generando embeddings...")
    generator = EmbeddingGenerator()
    
    texts = [chunk['text'] for chunk in all_chunks]
    embeddings = generator.generate_embeddings_batch(texts)
    
    print(f"✅ Embeddings generados: {embeddings.shape}")
    
    # 4. Indexar en Supabase
    print(f"\n💾 Indexando en Supabase...")
    try:
        db = SupabaseVectorDB()
        db.insert_chunks(all_chunks, embeddings)
        print(f"✅ Indexación completada")
    except Exception as e:
        print(f"⚠ Error indexando en Supabase: {e}")
        print(f"\n📝 NOTA: Si no has configurado Supabase:")
        print(f"  1. Crea un proyecto en supabase.com")
        print(f"  2. Ejecuta el SQL de creación de tablas (ver vector_db.py)")
        print(f"  3. Agrega SUPABASE_URL y SUPABASE_KEY al .env")
        print(f"\n  Por ahora, la búsqueda funcionará en memoria sin Supabase")
    
    print("\n" + "="*60)
    print("✅ PROCESAMIENTO COMPLETADO")
    print("="*60 + "\n")


if __name__ == "__main__":
    process_and_index_documents()
