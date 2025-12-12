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

-- [NEW] GRAND ARCHITECT TABLES (GENESIS) --

-- 3. Atomic Contexts (The "Folders")
create table if not exists atomic_contexts (
  id uuid primary key default gen_random_uuid(),
  folder_name text not null unique, -- e.g. "2025-12-12_15-03-07_373ddb76"
  timestamp timestamptz not null,
  batch_id text, -- e.g. "373ddb76"
  created_at timestamptz default now()
);

-- 4. Atomic Artifacts (The "Files")
create table if not exists atomic_artifacts (
  id uuid primary key default gen_random_uuid(),
  context_id uuid references atomic_contexts(id) on delete cascade,
  filename text not null,
  file_type text, -- "USER_SENT" or "AGENT_RECEIVED" or "UNKNOWN"
  file_hash text,
  local_path text,
  content text, -- Optional: Text content during search
  created_at timestamptz default now()
);

-- 5. Artifact Embeddings (Liquid Memory)
create table if not exists artifact_embeddings (
  id uuid primary key default gen_random_uuid(),
  artifact_id uuid references atomic_artifacts(id) on delete cascade,
  embedding vector(384),
  metadata jsonb
);

-- 6. Agent Skills (Meta-Learning)
create table if not exists agent_skills (
  id uuid primary key default gen_random_uuid(),
  name text not null unique, -- Python, React, SQL
  category text, -- Language, Framework, Tool
  proficiency int default 0,
  last_used timestamptz default now()
);

-- 7. Skill Evidence (Proof of Work)
create table if not exists skill_evidence (
  id uuid primary key default gen_random_uuid(),
  skill_id uuid references agent_skills(id) on delete cascade,
  context_id uuid references atomic_contexts(id) on delete set null,
  outcome text, -- SUCCESS, FAILURE
  timestamp timestamptz default now()
);

-- 8. Genesis Optimizations (Auto-Correction)
create table if not exists genesis_optimizations (
  id uuid primary key default gen_random_uuid(),
  target_artifact text, -- The file to fix
  issue_detected text,  -- The error
  proposed_fix text,    -- The solution
  status text default 'PENDING', -- PENDING, APPLIED, REJECTED
  created_at timestamptz default now()
);
