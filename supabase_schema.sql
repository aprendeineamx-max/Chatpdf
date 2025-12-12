-- Enable the pgvector extension to work with embedding vectors
create extension if not exists vector;

-- Create a table to store your documents
create table if not exists pdf_cortex_vectors (
  id uuid primary key default gen_random_uuid(),
  content text, -- The text chunk
  metadata jsonb, -- Page number, PDF ID, etc.
  embedding vector(384) -- Dimension depends on model (all-MiniLM-L6-v2 is 384)
);

-- Search Function
create or replace function match_documents (
  query_embedding vector(384),
  match_threshold float,
  match_count int,
  filter jsonb DEFAULT '{}'
) returns table (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
) language plpgsql stable as $$
begin
  return query
  select
    pdf_cortex_vectors.id,
    pdf_cortex_vectors.content,
    pdf_cortex_vectors.metadata,
    1 - (pdf_cortex_vectors.embedding <=> query_embedding) as similarity
  from pdf_cortex_vectors
  where 1 - (pdf_cortex_vectors.embedding <=> query_embedding) > match_threshold
  and pdf_cortex_vectors.metadata @> filter
  order by pdf_cortex_vectors.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- [NEW] CHAT PERSISTENCE TABLES --

-- 1. Chat Sessions (Conversations)
create table if not exists chat_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid, -- For future Auth
  title text default 'New Conversation',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- 2. Chat Messages (Individual interactions)
create table if not exists chat_messages (
  id uuid primary key default gen_random_uuid(),
  session_id uuid references chat_sessions(id) on delete cascade,
  role text not null check (role in ('user', 'assistant', 'system')),
  content text not null,
  sources jsonb default '[]'::jsonb, -- Store sources used for this answer
  created_at timestamptz default now()
);

-- Index for fast history loading
create index if not exists idx_messages_session_id on chat_messages(session_id);
