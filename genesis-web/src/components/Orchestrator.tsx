import { useState, useEffect } from 'react';

// Subcomponents
import { OrchestratorHeader } from './orchestrator/OrchestratorHeader';
import { SidebarHistory } from './orchestrator/SidebarHistory';
import { ChatArea } from './orchestrator/ChatArea';
import { KnowledgePanel } from './orchestrator/KnowledgePanel';
import { IngestModal } from './orchestrator/IngestModal';
import { FileEditorModal } from './orchestrator/FileEditorModal';

// Type Definitions (Local for now, typically move to types.ts)
interface RepoJob {
    id: string;
    name: string;
    path: string;
    status: string;
    error?: string;
}

interface Message {
    role: 'user' | 'assistant' | 'system';
    content: string;
    id?: string | number;
    created_at?: string;
    sources?: string[];
    model?: string;
}

interface FileNode {
    name: string;
    path: string;
    type: 'file' | 'dir';
    children?: FileNode[];
}

interface Task {
    id: string;
    title: string;
    status: 'PENDING' | 'IN_PROGRESS' | 'DONE';
    assigned_agent: string;
}

// API URL
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export function Orchestrator() {
    // --- State ---
    const [tasks, setTasks] = useState<Task[]>([]);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [isPolling, setIsPolling] = useState(false);

    // Session State
    const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
    const [sessions, setSessions] = useState<{ id: string, title: string, created_at: string }[]>([]);
    const [showHistory, setShowHistory] = useState(true);

    // System State
    const [systemMode, setSystemMode] = useState<"LOCAL" | "CLOUD">("LOCAL");

    // Context / Knowledge State
    const [activeTab, setActiveTab] = useState<'roadmap' | 'knowledge'>('roadmap');
    const [repos, setRepos] = useState<RepoJob[]>([]);

    // File Explorer State
    const [expandedRepo, setExpandedRepo] = useState<string | null>(null);
    const [repoFiles, setRepoFiles] = useState<FileNode[]>([]);
    const [selectedFile, setSelectedFile] = useState<{ name: string, content: string } | null>(null);
    const [isLoadingFiles, setIsLoadingFiles] = useState(false);
    const [selectedModel, setSelectedModel] = useState("Meta-Llama-3.3-70B-Instruct");
    const [selectedProvider, setSelectedProvider] = useState<string>("Sambanova");

    // Editor State
    const [isEditing, setIsEditing] = useState(false);
    const [editorContent, setEditorContent] = useState("");
    const [isSaving, setIsSaving] = useState(false);

    // Ingest Modal State
    const [showIngestModal, setShowIngestModal] = useState(false);
    const [ingestUrl, setIngestUrl] = useState('');
    const [ingestScope, setIngestScope] = useState<'global' | 'session'>('global');

    // --- Effects ---

    // Initial Load & Polling
    useEffect(() => {
        loadSessions();
        loadData();
        fetchSystemStatus();

        const interval = setInterval(() => {
            loadData(true);
        }, 5000);

        setIsPolling(true);
        return () => clearInterval(interval);
    }, []);

    // Editor Sync
    useEffect(() => {
        if (selectedFile) {
            setEditorContent(selectedFile.content);
            setIsEditing(false);
        }
    }, [selectedFile]);

    // --- API Handlers ---

    async function loadSessions() {
        try {
            const res = await fetch(`${API_URL}/api/v1/sessions`);
            if (res.ok) setSessions(await res.json());
        } catch (e) { console.error("Failed to load sessions", e); }
    }

    async function handleNewChat() {
        setMessages([]);
        setCurrentSessionId(null);
        setTasks([]); // [FIX] Clear tasks immediately
        loadSessions();
    }

    async function handleSelectSession(sessionId: string) {
        setCurrentSessionId(sessionId);
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/api/v1/sessions/${sessionId}`);
            if (res.ok) {
                setMessages(await res.json());
            }
        } catch (e) {
            console.error("Failed to load session history", e);
        } finally {
            setLoading(false);
        }
        if (window.innerWidth < 1024) setShowHistory(false);
        // Force reload data for this session
        setTimeout(() => loadData(true), 100);
    }

    async function handleCloneSession(sessionId: string, e: React.MouseEvent) {
        e.stopPropagation();
        try {
            const res = await fetch(`${API_URL}/api/v1/sessions/${sessionId}/clone`, { method: 'POST' });
            if (res.ok) {
                const data = await res.json();
                await loadSessions();
                handleSelectSession(data.session_id);
            }
        } catch (e) { console.error("Failed to clone session", e); }
    }

    async function handleDeleteSession(sessionId: string, e: React.MouseEvent) {
        e.stopPropagation();
        if (!confirm("Are you sure you want to delete this chat?")) return;
        try {
            await fetch(`${API_URL}/api/v1/sessions/${sessionId}`, { method: 'DELETE' });
            if (currentSessionId === sessionId) handleNewChat();
            loadSessions();
        } catch (e) { console.error("Failed to delete session", e); }
    }

    async function loadData(silent = false) {
        if (!silent) setLoading(true);
        try {
            // [FIX] Scoped Fetch
            const [tasksRes, reposRes] = await Promise.all([
                fetch(`${API_URL}/api/v1/orchestrator/tasks?session_id=${currentSessionId || ''}`),
                fetch(`${API_URL}/api/v1/ingest/list?session_id=${currentSessionId || ''}`)
            ]);

            if (tasksRes.ok) setTasks(await tasksRes.json());
            if (reposRes.ok) setRepos(await reposRes.json());

        } catch (error) {
            console.error('Connection Error:', error);
        } finally {
            if (!silent) setLoading(false);
        }
    }

    async function fetchSystemStatus() {
        try { await fetch(`${API_URL}/health`); } catch (e) { console.error("Health check failed", e); }
    }

    // --- File Logic ---
    async function fetchFiles(repoName: string, path: string) {
        setIsLoadingFiles(true);
        try {
            const cleanName = repoName.replace("REPO: ", "");
            const res = await fetch(`${API_URL}/api/v1/ingest/files?repo_name=${cleanName}&path=${encodeURIComponent(path)}`);
            if (res.ok) setRepoFiles(await res.json());
        } catch (e) { console.error("File Fetch Error:", e); }
        finally { setIsLoadingFiles(false); }
    }

    async function fetchContent(repoName: string, path: string) {
        const cleanName = repoName.replace("REPO: ", "");
        try {
            const res = await fetch(`${API_URL}/api/v1/ingest/content?repo_name=${cleanName}&path=${encodeURIComponent(path)}`);
            if (res.ok) {
                const data = await res.json();
                setSelectedFile({ name: path.split('/').pop() || 'File', content: data.content });
            }
        } catch (e) { console.error(e); alert("Failed to load file content."); }
    }

    async function saveCurrentFile() {
        if (!selectedFile || !expandedRepo) return;
        setIsSaving(true);
        try {
            const cleanName = expandedRepo.replace("REPO: ", "");
            const res = await fetch(`${API_URL}/api/v1/ingest/content`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    repo_name: cleanName,
                    path: selectedFile.name,
                    content: editorContent
                })
            });
            if (res.ok) {
                setSelectedFile(prev => prev ? ({ ...prev, content: editorContent }) : null);
                setIsEditing(false);
            } else { throw new Error("Save returned " + res.status); }
        } catch (e) {
            alert("Failed to save file.");
            console.error(e);
        } finally { setIsSaving(false); }
    }

    // --- Interaction Logic ---
    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMsg: Message = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const res = await fetch(`${API_URL}/api/v1/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query_text: userMsg.content,
                    pdf_id: "all",
                    mode: systemMode === 'CLOUD' ? 'swarm' : 'standard',
                    session_id: currentSessionId,
                    model: selectedModel,
                    provider: selectedProvider,
                    repo_context: expandedRepo
                }),
            });

            const data = await res.json();

            if (data.session_id && data.session_id !== currentSessionId) {
                setCurrentSessionId(data.session_id);
                loadSessions();
            }

            const finalProvider = data.metadata?.provider || selectedProvider;
            const finalModel = data.metadata?.model || selectedModel;

            const botMsg: Message = {
                role: 'assistant',
                content: data.answer || "I processed that but have no specific answer.",
                sources: data.sources,
                model: finalModel + (finalProvider && finalProvider !== "unknown" ? ` @ ${finalProvider}` : "")
            };
            setMessages(prev => [...prev, botMsg]);

            if (data.tasks) loadData(true);

        } catch (error: any) {
            console.error("Chat Error:", error);
            const msg = error.message || "Unknown Error";
            setMessages(prev => [...prev, { role: 'system', content: `Error: ${msg}` }]);
        } finally { setLoading(false); }
    };

    const handleIngestSubmit = async () => {
        const url = ingestUrl.trim();
        if (!url) return;

        setShowIngestModal(false);
        setIngestUrl('');
        setActiveTab('knowledge');

        setMessages(prev => [...prev, {
            id: 'sys-' + Date.now(),
            role: 'system',
            content: `👁️ INGESTION INITIATED: ${url}`,
            created_at: new Date().toISOString()
        }]);

        try {
            const res = await fetch(`${API_URL}/api/v1/ingest/repo`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: url,
                    scope: ingestScope,
                    session_id: currentSessionId
                })
            });

            if (res.ok) {
                setMessages(prev => [...prev, {
                    id: 'sys-done-' + Date.now(),
                    role: 'system',
                    content: `✅ INGESTION QUEUED. The Architect is analyzing...`,
                    created_at: new Date().toISOString()
                }]);
                loadData(true);
            } else {
                const errData = await res.json().catch(() => ({ detail: "Unknown Error" }));
                const detailStr = typeof errData.detail === 'object' ? JSON.stringify(errData.detail) : (errData.detail || `Server Error ${res.status}`);
                throw new Error(detailStr);
            }

        } catch (e: any) {
            console.error("Ingestion Error:", e);
            let msg = "Unknown Error";
            if (e instanceof Error) msg = e.message;
            setMessages(prev => [...prev, {
                id: 'sys-err-' + Date.now(),
                role: 'system',
                content: `❌ INGESTION FAILED: ${msg}`,
                created_at: new Date().toISOString()
            }]);
        }
    };

    return (
        <div className="flex flex-col h-full bg-[#111115] text-white relative overflow-hidden">

            <OrchestratorHeader
                showHistory={showHistory}
                setShowHistory={setShowHistory}
                isPolling={isPolling}
                handleNewChat={handleNewChat}
                selectedProvider={selectedProvider}
                setSelectedProvider={setSelectedProvider}
                selectedModel={selectedModel}
                setSelectedModel={setSelectedModel}
                systemMode={systemMode}
                setSystemMode={setSystemMode}
            />

            {/* Main Content Area */}
            <div className="flex-1 flex overflow-hidden">
                <SidebarHistory
                    showHistory={showHistory}
                    sessions={sessions}
                    currentSessionId={currentSessionId}
                    handleNewChat={handleNewChat}
                    handleSelectSession={handleSelectSession}
                    handleCloneSession={handleCloneSession}
                    handleDeleteSession={handleDeleteSession}
                />

                <ChatArea
                    messages={messages}
                    input={input}
                    setInput={setInput}
                    sendMessage={sendMessage}
                    loading={loading}
                    activeTab={activeTab}
                />

                <KnowledgePanel
                    activeTab={activeTab}
                    setActiveTab={setActiveTab}
                    tasks={tasks}
                    repos={repos}
                    expandedRepo={expandedRepo}
                    setExpandedRepo={setExpandedRepo}
                    repoFiles={repoFiles}
                    isLoadingFiles={isLoadingFiles}
                    fetchFiles={fetchFiles}
                    fetchContent={fetchContent}
                    setShowIngestModal={setShowIngestModal}
                />
            </div>

            {/* Modals */}
            <IngestModal
                showIngestModal={showIngestModal}
                setShowIngestModal={setShowIngestModal}
                ingestUrl={ingestUrl}
                setIngestUrl={setIngestUrl}
                ingestScope={ingestScope}
                setIngestScope={setIngestScope}
                handleIngestSubmit={handleIngestSubmit}
            />

            <FileEditorModal
                selectedFile={selectedFile}
                editorContent={editorContent}
                isEditing={isEditing}
                isSaving={isSaving}
                setEditorContent={setEditorContent}
                setIsEditing={setIsEditing}
                setSelectedFile={setSelectedFile}
                saveCurrentFile={saveCurrentFile}
            />
        </div>
    );
}
