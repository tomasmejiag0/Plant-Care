-- ================================================
-- CONFIGURACIÓN COMPLETA DE SUPABASE
-- PlantCare AI - Base de Datos Vectorial
-- ================================================
-- Ejecuta estos comandos UNO POR UNO en el SQL Editor de Supabase

-- ================================================
-- PASO 1: Habilitar extensión vectorial
-- ================================================
create extension if not exists vector;

-- ================================================
-- PASO 2: Crear tabla de documentos
-- ================================================
create table if not exists plant_documents (
  id bigserial primary key,
  chunk_id text unique not null,
  source_file text not null,
  chunk_index int not null,
  text text not null,
  embedding vector(384),
  created_at timestamptz default now()
);

-- Comentarios para documentación
comment on table plant_documents is 'Almacena chunks de documentos con embeddings vectoriales';
comment on column plant_documents.embedding is 'Embedding de 384 dimensiones (all-MiniLM-L6-v2)';

-- ================================================
-- PASO 3: Crear índice vectorial para búsqueda rápida
-- ================================================
create index on plant_documents 
using ivfflat (embedding vector_cosine_ops)
with (lists = 100);

-- ================================================
-- PASO 4: Crear función de búsqueda por similitud
-- ================================================
create or replace function match_plant_documents (
  query_embedding vector(384),
  match_threshold float,
  match_count int
)
returns table (
  id bigint,
  chunk_id text,
  source_file text,
  text text,
  similarity float
)
language sql stable
as $$
  select
    id,
    chunk_id,
    source_file,
    text,
    1 - (embedding <=> query_embedding) as similarity
  from plant_documents
  where 1 - (embedding <=> query_embedding) > match_threshold
  order by embedding <=> query_embedding
  limit match_count;
$$;

-- ================================================
-- VERIFICACIÓN: Ejecuta esto para confirmar que todo funciona
-- ================================================
-- Verificar que la tabla existe (debería retornar 0)
select count(*) from plant_documents;

-- Verificar que la función existe (debería retornar 'match_plant_documents')
select proname from pg_proc where proname = 'match_plant_documents';

-- ================================================
-- ¡LISTO! Ahora ejecuta: python process_documents.py
-- ================================================
