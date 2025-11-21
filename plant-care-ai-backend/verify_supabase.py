"""
Script para verificar la indexación en Supabase
Muestra estadísticas de documentos indexados
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Conectar a Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("❌ Error: SUPABASE_URL o SUPABASE_KEY no configurados en .env")
    exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

print("\n" + "=" * 60)
print("📊 ESTADÍSTICAS DE SUPABASE - plant_documents")
print("=" * 60 + "\n")

# Contar total de chunks
result = supabase.table('plant_documents').select('id', count='exact').execute()
total_chunks = result.count

print(f"📚 Total de chunks indexados: {total_chunks}")
print("\n" + "-" * 60 + "\n")

# Obtener chunks por documento
result = supabase.table('plant_documents').select('source_file').execute()

if result.data:
    # Contar por archivo
    file_counts = {}
    for row in result.data:
        source_file = row['source_file']
        file_counts[source_file] = file_counts.get(source_file, 0) + 1
    
    # Ordenar por nombre
    sorted_files = sorted(file_counts.items())
    
    print("📄 Chunks por documento:\n")
    for i, (filename, count) in enumerate(sorted_files, 1):
        print(f"{i:2d}. {filename:30s} → {count:3d} chunks")
    
    print("\n" + "-" * 60 + "\n")
    print(f"✅ Total de documentos: {len(file_counts)}")
    print(f"✅ Total de chunks: {sum(file_counts.values())}")
    
    # Documentos más grandes
    top_docs = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"\n🏆 Top 5 documentos más grandes:\n")
    for i, (filename, count) in enumerate(top_docs, 1):
        print(f"{i}. {filename} - {count} chunks")
else:
    print("⚠️ No se encontraron documentos en Supabase")

print("\n" + "=" * 60 + "\n")
