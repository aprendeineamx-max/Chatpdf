import React from 'react';

// Components
import { OrchestratorHeader } from './orchestrator/OrchestratorHeader';
import { SidebarHistory } from './orchestrator/SidebarHistory';
import { ChatArea } from './orchestrator/ChatArea';
import { KnowledgePanel } from './orchestrator/KnowledgePanel';
import { IngestModal } from './orchestrator/IngestModal';
import { FileEditorModal } from './orchestrator/FileEditorModal';

// Hooks
import { useOrchestrator } from '../hooks/useOrchestrator';

export function Orchestrator() {
    const {
        // State
        tasks, messages, input, setInput, loading, isPolling,
        currentSessionId, sessions, showHistory, setShowHistory,
    );
}
