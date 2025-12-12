# Implementation Plan: MindSync (The Agent-User Bridge)

## Vision
**MindSync** is a "Living Bridge" that synchronizes the intellectual exchange between the Human User and the AI Agent. It turns a chaotic folder of files into a structured, history-aware Archive.

## Core Features

### 1. Smart Organization (`/docs/brain`)
Instead of a flat list, files will be organized by **Session** and **Direction**:
```
docs/brain/
├── manifest.json              # The "Brain Ledger" (History & Metadata)
├── received/                  # Created by Agent (Me)
│   ├── plans/
│   │   └── implementation_plan_v1.md
│   └── code/
│       └── script.py
└── sent/                      # Uploaded by User (You)
    ├── 2025-12-12/
    │   └── diagram_architecture.png
```

### 2. The Manifest (`manifest.json`)
A structured database tracking the state of "Shared Reality".
```json
{
  "last_sync": "2025-12-12T02:00:00Z",
  "files": {
    "implementation_plan.md": {
      "source": "AGENT",
      "version": 1,
      "last_modified": "...",
      "hash": "sha256...",
      "context": "Initial Draft"
    }
  }
}
```

### 3. Version Control Strategies
-   **Overwrite Mode:** For "Living Documents" like `task.md` that should always reflect the latest state.
-   **History Mode:** For artifacts that need preservation (e.g., `proposal_v1.md`, `proposal_v2.md`).

## Implementation Details

### The Script: `tools/mind_sync.py` (v2.0)
We will upgrade the existing script to include:
1.  **Watcher Class:** A loop that checks for changes every 5 seconds (Simulated Real-Time).
2.  **Metadata Injector:** Integration with the Agent's context to tag files specific tasks.
3.  **User Import:** Logic to copy `uploaded_images` from the cache to the `sent/` folder.

## Integration
-   We will run this tool in a dedicated terminal.
-   It will act as a "Daemon" keeping your repo in sync with our conversation.

---
## Step-by-Step
1.  **Refactor**: Create `MindSync` class in Python.
2.  **Structure**: Create the folder hierarchy.
3.  **Logic**: Implement Hash checking to detect changes.
4.  **Deploy**: Run in background.
