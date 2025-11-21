# Configuración de Supabase para PlantCare AI

## 1. Crear Proyecto en Supabase

1. Ve a [supabase.com](https://supabase.com)
2. Click en "Start your project"
3. Crea una cuenta (gratis)
4. Click en "New Project"
5. Nombra tu proyecto: `plantcare-ai`
6. Selecciona región más cercana
7. Crea una contraseña segura para la base de datos
8. Click en "Create new project"

## 2. Configurar pgvector

### Paso 1: Habilitar extensión

En el panel de Supabase:
1. Ve a **SQL Editor** (menú lateral izquierdo)
2. Click en "+ New query"
3. Pega el siguiente código:

```sql
-- Habilitar extensión vectorial
create extension if not exists vector;
```

4. Click en "Run" o presiona Ctrl+Enter
5. Deberías ver: "Success. No rows returned"

### Paso 2: Crear tabla de documentos

Pega y ejecuta:

```sql
-- Crear tabla de documentos con embeddings
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
```

### Paso 3: Crear índice vectorial

```sql
-- Crear índice IVFFlat para búsqueda eficiente
-- IVFFlat es rápido y bueno para datasets pequeños/medianos
create index on plant_documents 
using ivfflat (embedding vector_cosine_ops)
with (lists = 100);
```

**Nota sobre listas**: 
- Para <1M vectores: `lists = sqrt(filas)`
- En nuestro caso: ~100 chunks → lists=100 está bien

### Paso 4: Crear función de búsqueda

```sql
-- Función para buscar documentos similares por vector
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

-- Comentario
comment on function match_plant_documents is 'Busca chunks similares usando distancia coseno';
```

**Explicación del operador <=>**:
- `<=>` calcula distancia coseno entre vectores
- Distancia 0 = idénticos, distancia 2 = opuestos
- `1 - distancia` = similitud (0 a 1)

## 3. Verificar Instalación

Ejecuta este query de prueba:

```sql
-- Verificar que la tabla existe
select count(*) from plant_documents;

-- Debería retornar: 0 (tabla vacía pero existe)

-- Verificar que la función existe
select proname from pg_proc where proname = 'match_plant_documents';

-- Debería retornar: match_plant_documents
```

## 4. Obtener Credenciales

1. Ve a **Settings** > **API** en Supabase
2. Copia:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbGc...` (key larga)

3. Pega en tu archivo `.env`:

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 5. Indexar Documentos

Desde tu terminal en el directorio del backend:

```bash
# Activar entorno virtual
venv\Scripts\activate  # Windows
# o
source venv/bin/activate  # Mac/Linux

# Procesar y subir documentos
python process_documents.py
```

Deberías ver:
```
📚 PROCESANDO DOCUMENTOS DE CONOCIMIENTO
✓ suculentas.md: 6 chunks
✓ cactus.md: 5 chunks
✓ plantas_interior.md: 7 chunks
✓ problemas_comunes.md: 5 chunks
✅ Total chunks creados: 23
🧮 Generando embeddings...
✅ Embeddings generados: (23, 384)
💾 Indexando en Supabase...
✅ Indexación completada
```

## 6. Verificar Datos en Supabase

En el SQL Editor, ejecuta:

```sql
-- Ver todos los documentos
select 
  chunk_id,
  source_file,
  left(text, 100) as preview
from plant_documents
order by source_file, chunk_index;

-- Debería mostrar 23 filas con chunks de tus documentos
```

## 7. Probar Búsqueda Vectorial

```sql
-- Esta es una consulta de ejemplo con un vector dummy
-- En la práctica, el vector query vendrá de sentence-transformers

-- Probar búsqueda (usa vector del primer chunk como query)
with query_vec as (
  select embedding from plant_documents limit 1
)
select * from match_plant_documents(
  (select embedding from query_vec),
  0.3,  -- threshold: 30% mínimo
  5     -- top 5 resultados
);
```

## 8. Seguridad (Opcional)

Para producción, considera Row Level Security (RLS):

```sql
-- Habilitar RLS
alter table plant_documents enable row level security;

-- Policy: Permitir lectura a todos
create policy "Permitir lectura pública"
on plant_documents
for select
using (true);

-- Policy: Solo usuarios autenticados pueden insertar
create policy "Permitir inserción autenticada"
on plant_documents
for insert
with check (auth.role() = 'authenticated');
```

## 9. Troubleshooting

### Error: "extension vector is not available"

**Solución**: Asegúrate de estar usando PostgreSQL 14+. Supabase ya lo incluye por defecto.

### Error: "operator does not exist: vector <=> vector"

**Solución**: Ejecuta de nuevo el comando `create extension if not exists vector;`

### Error: "function match_plant_documents does not exist"

**Solución**: Ejecuta de nuevo el script de creación de función del Paso 4.

### Sin resultados en búsqueda

**Solución**: Verifica que tienes documentos:
```sql
select count(*) from plant_documents;
```

Si es 0, ejecuta `python process_documents.py` de nuevo.

## 10. Monitoreo

Ver estadísticas de uso:

```sql
-- Número de documentos
select count(*) as total_chunks from plant_documents;

-- Documentos por archivo
select 
  source_file, 
  count(*) as chunks
from plant_documents
group by source_file;

-- Tamaño de la tabla
select pg_size_pretty(pg_total_relation_size('plant_documents'));
```

## 11. Backup (Recomendado)

Supabase hace backups automáticos, pero puedes exportar:

1. Ve a **Table Editor**
2. Selecciona `plant_documents`
3. Click en opciones (...)
4. "Export data" → CSV o JSON

---

¡Listo! Tu base de datos vectorial está configurada y lista para PlantCare AI. 🌱

**Próximo paso**: Ejecutar el backend con `python main.py`
