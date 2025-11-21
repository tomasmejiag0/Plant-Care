"""
Script simple para limpiar la tabla plant_documents en Supabase
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("❌ Error: Configurar SUPABASE_URL y SUPABASE_KEY en .env")
    exit(1)

supabase = create_client(supabase_url, supabase_key)

print("\n🗑️  Limpiando tabla plant_documents...")

try:
    # Eliminar todos los registros
    result = supabase.table('plant_documents').delete().neq('id', 0).execute()
    print("✅ Tabla limpiada exitosamente\n")
    print("Ahora ejecuta: python process_documents.py\n")
except Exception as e:
    print(f"❌ Error: {e}\n")
