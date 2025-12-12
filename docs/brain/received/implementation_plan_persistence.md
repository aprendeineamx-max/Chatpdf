# Implementation Plan - Phase 3: Infinite Memory (Persistence & Speed)

## Goal
Implement a robust, high-performance Chat Persistence layer ensuring users never lose their conversations.
**Philosophy:** "Fastest Data Travel & 100% Retention."

## Technology Stack Selection (Hybrid Synergy)
1.  **Primary Storage (The Vault):** **Supabase (PostgreSQL)**.
    *   *Why:* Proven robustness, native Vector support (pgvector), JSONB flexibility, and massive scale. Perfect for the "AI Hub" structure.
2.  **Hot Memory (The Reflex):** **Redis**.
    *   *Why:* Sub-millisecond read/writes. We will use this to cache the "Active Conversation Context" so the AI doesn't need to fetch from DB every time.
3.  **Intelligence (The Brain):** **Gemini 1.5 Pro/Flash (1M Token)**.
    *   *Why:* To achieve the "100% Book Context" goal. We will upgrade the prompt strategy to stuff massive context when needed.

## Proposed Changes

### 1. Database Schema (Supabase)
#### [NEW] Table: `chat_sessions`
- `id` (UUID)
- `pdf_id` (Reference to Book)
- `title` (Auto-generated summary)
- `created_at`

#### [NEW] Table: `chat_messages`
- `session_id` (FK)
- `role` (user/assistant)
- `content` (Text)
- `sources` (JSONB - for storing the source nodes permanently)

### 2. Backend (FastAPI)
#### [NEW] `app/routers/chat.py`
- `GET /sessions`: List user's chats.
- `GET /sessions/{id}`: Load full history.
- `POST /sessions`: Create new thread.
- **Update Query Endpoint:** When a query is answered, *asynchronously* save the User Request + AI Response to Supabase.

### 3. Frontend (React)
#### [MODIFY] `ChatInterface.tsx`
- Load history on mount.
- "Sidebar" to switch between sessions (Future task, for now just persistence of current).
- Optimistic UI updates (Show message immediately, save in background).

## Verification Plan
1.  **Persistence Test:** Reload page -> Chat history reappears.
2.  **Speed Test:** Measure impact of DB write on latency (Should be near-zero using `BackgroundTasks`).
