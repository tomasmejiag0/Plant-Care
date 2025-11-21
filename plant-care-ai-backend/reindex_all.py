"""
Script para RE-INDEXAR toda la base de conocimiento
1. Limpia la tabla plant_documents
2. Procesa todos los documentos de nuevo
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import sys
sys.path.append('src')

from data_extractor import DataExtractor
from text_chunker import TextChunker
from embeddings import EmbeddingGenerator
from vector_db import SupabaseVectorDB

load_dotenv()

print("\n" + "=" * 60)
print("🔄 RE-INDEXACIÓN COMPLETA DE DOCUMENTOS")
print("=" * 60 + "\n")

# Conectar a Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("❌ Error: SUPABASE_URL o SUPABASE_KEY no configurados")
    exit(1)

supabase = create_client(supabase_url, supabase_key)

# 1. LIMPIAR TABLA
print("🗑️  Limpiando tabla plant_documents...")
try:
    # Eliminar TODOS los registros
    result = supabase.table('plant_documents').delete().neq('id', 0).execute()
    print(f"✅ Tabla limpiada\n")
except Exception as e:
    print(f"⚠️  Error limpiando tabla: {e}\n")

# 2. PROCESAR DOCUMENTOS
print("📚 PROCESANDO DOCUMENTOS DE CONOCIMIENTO\n")

# Extraer documentos
extractor = DataExtractor(data_dir="data/plantas")
documents = extractor.extract_all_documents()

print(f"📄 Documentos encontrados: {len(documents)}\n")

# Chunking
chunker = TextChunker(chunk_size=400, overlap=50)
all_chunks = []
chunk_metadata = []

for doc in documents:
    chunks = chunker.chunk_document(doc)
    for chunk in chunks:
        all_chunks.append(chunk['text'])
        chunk_metadata.append({
            'chunk_id': chunk['chunk_id'],
            'source_file': chunk['source_file'],
            'chunk_index': chunk['chunk_index']
        })
    
    print(f"  ✓ {doc['filename']}: {len(chunks)} chunks")

print(f"\n✅ Total chunks creados: {len(all_chunks)}\n")

# Generar embeddings
print("🧮 Generando embeddings...")
generator = EmbeddingGenerator()
embeddings = generator.generate_embeddings(all_chunks)
print(f"✅ Embeddings generados: {embeddings.shape}\n")

# Indexar en Supabase
print("💾 Indexando en Supabase...")
try:
    db = SupabaseVectorDB()
    db.insert_chunks(all_chunks, embeddings, chunk_metadata)
    print(f"✅ Indexación completada: {len(all_chunks)} chunks\n")
except Exception as e:
    print(f"❌ Error indexando: {e}\n")
    raise

print("=" * 60)
print("✅ RE-INDEXACIÓN COMPLETADA")
print("=" * 60 + "\n")
