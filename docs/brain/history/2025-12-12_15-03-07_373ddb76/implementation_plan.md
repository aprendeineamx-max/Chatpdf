# Implementation Plan - Hydra Swarm & UI Config

## Goal
Implement "Swarm Retrieval" (Parallel Multi-Key Processing) as a configurable option in the UI, allowing the user to switch between "Standard Mode" (Round-Robin) and "Swarm Mode" (Simultaneous Multi-Key).

## User Review Required
> [!IMPORTANT]
> **Swarm Mode Intensity:** Running 3 keys in parallel triples the query speed but also triples the token consumption rate.
> **UI Location:** I propose adding a "Control Panel" toggle above the Chat Interface for easy access.

## Proposed Changes

### Frontend (React/Vite)
#### [NEW] `src/components/ControlPanel.tsx`
- A visual component to toggle "Swarm Mode".
- Displays active "Hydra Heads" (active available keys).
- Passes the mode state to the parent `App` or `ChatInterface`.

#### [MODIFY] `src/App.tsx` or `ChatInterface.tsx`
- Integrate `ControlPanel`.
- Pass the `swarm_mode` boolean flag in the API request body to `POST /query`.

### Backend (FastAPI + Python)
#### [MODIFY] `app/services/rag/engine.py`
- Implement `query_swarm(query_text)` method.
- Use `asyncio.gather` to trigger multiple LLM calls if the query requires deep analysis (splitting the problem) OR just parallelizing chunks.
    *   *Initial Swarm Strategy:* "Consensus Mode". Query the same question to 3 models with different "Temperature" or specialized prompts, then synthesize the answer.
    *   *Alternative Strategy:* Split context. (More complex, requires chunk management).
    *   *Selected Strategy for V1:* **Parallel Context Sharding**. Split retrieved nodes into 3 groups, send each group to a different Key/LLM, then merge results. This allows processing 3x more context.

#### [MODIFY] `app/main.py`
- Update `QueryRequest` model to accept `mode: str = "standard" | "swarm"`.
- Route to `rag_service.query` or `rag_service.query_swarm` based on flag.

## Verification Plan
### Automated Tests
- `test_swarm.py`: A script that fires a swarm request and measures time vs standard request.
### Manual Verification
- Toggle "Swarm Mode" in UI.
- Observe logs to see 3 different keys being used virtually simultaneously.
