"""
Script de prueba para demostrar que el sistema funciona SIN Gemini
Solo usa los componentes básicos: extracción, chunking, embeddings, similitud, BD vectorial
"""
import sys
import os
sys.path.append('src')

from extraccion import DataExtractor
from chunking import TextChunker
from embeddings import EmbeddingGenerator
from similitud import SimilaritySearch
import numpy as np

def test_sistema_sin_gemini():
    """
    Prueba completa del sistema usando solo componentes básicos
    Sin usar Gemini ni ningún LLM externo
    """
    print("=" * 60)
    print("🧪 PRUEBA: Sistema SIN Gemini (Solo Componentes Básicos)")
    print("=" * 60)
    
    # 1. EXTRACCIÓN
    print("\n1️⃣ EXTRACCIÓN DE DATOS")
    print("-" * 60)
    extractor = DataExtractor("data/plantas")
    documents = extractor.extract_all_documents()
    print(f"✅ Documentos extraídos: {len(documents)}")
    assert len(documents) > 0, "Debe haber documentos"
    
    # 2. CHUNKING
    print("\n2️⃣ SEGMENTACIÓN (CHUNKING)")
    print("-" * 60)
    chunker = TextChunker(chunk_size=400, overlap=50)
    all_chunks = []
    for doc in documents[:3]:  # Procesar primeros 3 documentos
        chunks = chunker.chunk_document(doc)
        all_chunks.extend(chunks)
        print(f"✅ Documento '{doc['filename']}': {len(chunks)} chunks")
    print(f"✅ Total chunks creados: {len(all_chunks)}")
    assert len(all_chunks) > 0, "Debe haber chunks"
    
    # 3. EMBEDDINGS
    print("\n3️⃣ GENERACIÓN DE EMBEDDINGS")
    print("-" * 60)
    generator = EmbeddingGenerator()
    chunk_texts = [chunk['text'] for chunk in all_chunks]
    embeddings = generator.generate_embeddings_batch(chunk_texts)
    print(f"✅ Embeddings generados: {embeddings.shape}")
    print(f"✅ Dimensiones: {embeddings.shape[1]} (esperado: 384)")
    assert embeddings.shape[1] == 384, "Debe tener 384 dimensiones"
    
    # 4. SIMILITUD
    print("\n4️⃣ BÚSQUEDA POR SIMILITUD DEL COSENO")
    print("-" * 60)
    search = SimilaritySearch()
    search.add_documents(embeddings, all_chunks)
    
    # Consulta de prueba
    query = "Como cuido una suculenta"
    query_embedding = generator.generate_embedding(query)
    results = search.search(query_embedding, top_k=3, threshold=0.25)
    
    print(f"✅ Consulta: '{query}'")
    print(f"✅ Resultados encontrados: {len(results)}")
    for i, (doc, score) in enumerate(results, 1):
        print(f"   {i}. [Relevancia: {score:.3f}] {doc['text'][:80]}...")
    
    assert len(results) > 0, "Debe encontrar resultados"
    
    # 5. DEMOSTRACIÓN DE SIMILITUD DEL COSENO
    print("\n5️⃣ DEMOSTRACIÓN DE SIMILITUD DEL COSENO")
    print("-" * 60)
    # Comparar dos textos similares
    text1 = "Las suculentas necesitan poco riego"
    text2 = "Las plantas crasas requieren poca agua"
    text3 = "Los cactus necesitan mucha luz solar"
    
    emb1 = generator.generate_embedding(text1)
    emb2 = generator.generate_embedding(text2)
    emb3 = generator.generate_embedding(text3)
    
    sim12 = generator.cosine_similarity(emb1, emb2)
    sim13 = generator.cosine_similarity(emb1, emb3)
    
    print(f"✅ Texto 1: '{text1}'")
    print(f"✅ Texto 2: '{text2}'")
    print(f"✅ Texto 3: '{text3}'")
    print(f"✅ Similitud 1-2 (similares): {sim12:.3f}")
    print(f"✅ Similitud 1-3 (diferentes): {sim13:.3f}")
    assert sim12 > sim13, "Textos similares deben tener mayor similitud"
    
    print("\n" + "=" * 60)
    print("✅ TODAS LAS PRUEBAS PASARON")
    print("=" * 60)
    print("\n📊 RESUMEN:")
    print(f"   • Documentos extraídos: {len(documents)}")
    print(f"   • Chunks creados: {len(all_chunks)}")
    print(f"   • Embeddings generados: {embeddings.shape[0]}")
    print(f"   • Búsqueda por similitud: ✅ Funcional")
    print(f"   • Similitud del coseno: ✅ Implementada")
    print(f"\n🎯 CONCLUSIÓN: El sistema funciona completamente SIN Gemini")
    print("   Todos los componentes básicos están implementados correctamente.")

if __name__ == "__main__":
    try:
        test_sistema_sin_gemini()
    except Exception as e:
        print(f"\n❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()

