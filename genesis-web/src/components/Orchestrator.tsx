
import { useState, useEffect, useRef } from 'react';
import { Send, CheckCircle2, Circle, Bot, User, BrainCircuit, WifiOff, Wifi, Cloud, Database, RefreshCcw, Save, ArrowUp, ArrowDown, X, FileCode, Folder, ArrowLeft, Layout, ArrowRight, MessageSquare, Copy, Trash2, Brain } from 'lucide-react'; // [FIX] Added Brain
import Editor from '@monaco-editor/react';
import { AtomicContext, AtomicArtifact } from '../types';

// Helper to determine language
function getLanguageFromPath(path: string): string {
    if (path.endsWith('.ts') || path.endsWith('.tsx')) return 'typescript';
    if (path.endsWith('.js') || path.endsWith('.jsx')) return 'javascript';
    if (path.endsWith('.py')) return 'python';
    if (path.endsWith('.json')) return 'json';
    if (path.endsWith('.html')) return 'html';
    if (path.endsWith('.css')) return 'css';
    if (path.endsWith('.md')) return 'markdown';
    if (path.endsWith('.sql')) return 'sql';
    if (path.endsWith('.yaml') || path.endsWith('.yml')) return 'yaml';
    return 'plaintext';
}

// Use the API URL from environment or default to local backend
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

interface RepoJob {
    id: string;
    name: string;
    path: string;
    status: string; // 'CLONING', 'ANALYZING', 'SAVING', 'COMPLETED', 'FAILED'
    timestamp?: string;
    error?: string;
}

interface Message {
    role: 'user' | 'assistant' | 'system';
    content: string;
    id?: string | number;
    created_at?: string;
    sources?: string[];
    model?: string; // [NEW] Model Name
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

export function Orchestrator() {
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
    const [showMenu, setShowMenu] = useState(false);

    // Context / Knowledge State
    const [activeTab, setActiveTab] = useState<'roadmap' | 'knowledge'>('roadmap');
    const [repos, setRepos] = useState<RepoJob[]>([]);

    // File Explorer State
    const [expandedRepo, setExpandedRepo] = useState<string | null>(null);
    const [repoFiles, setRepoFiles] = useState<FileNode[]>([]);
    const [currentPath, setCurrentPath] = useState<string>("");
    const [selectedFile, setSelectedFile] = useState<{ name: string, content: string } | null>(null);
    const [isLoadingFiles, setIsLoadingFiles] = useState(false);
    const [selectedModel, setSelectedModel] = useState("Meta-Llama-3.3-70B-Instruct"); // [FIX] Valid Model
    const [selectedProvider, setSelectedProvider] = useState<string>("Sambanova"); // [NEW] Provider State


    // Editor State
    const [isEditing, setIsEditing] = useState(false);
    const [editorContent, setEditorContent] = useState("");
    const [isSaving, setIsSaving] = useState(false);

    // Ingest Modal State
    const [showIngestModal, setShowIngestModal] = useState(false);
    const [ingestUrl, setIngestUrl] = useState('');

    // UI Responsiveness State
    const [isMobilePanelOpen, setIsMobilePanelOpen] = useState(false);

    // Initial Load & Polling (Pulse Mode)
    useEffect(() => {
        loadSessions(); // Load history
        loadData();
        fetchSystemStatus();

        // Polling every 5 seconds for local updates (replacing Realtime)
        const interval = setInterval(() => {
            loadData(true);
        }, 5000);

        setIsPolling(true);

        return () => clearInterval(interval);
    }, []);

    // --- Auto-Scroll ---
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Update editor content when file changes
    useEffect(() => {
        if (selectedFile) {
            setEditorContent(selectedFile.content);
            setIsEditing(false); // Reset to read mode on file switch
        }
    }, [selectedFile]);

    // --- Session Management ---
    async function loadSessions() {
        try {
            const res = await fetch(`${API_URL}/api/v1/sessions`);
            if (res.ok) {
                const data = await res.json();
                setSessions(data);
            }
        } catch (e) { console.error("Failed to load sessions", e); }
    }

    async function handleNewChat() {
        setMessages([]);
        setCurrentSessionId(null);
        loadSessions();
    }

    async function handleSelectSession(sessionId: string) {
        setCurrentSessionId(sessionId);
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/api/v1/sessions/${sessionId}`);
            if (res.ok) {
                const data = await res.json();
                setMessages(data);
            }
        } catch (e) {
            console.error("Failed to load session history", e);
        } finally {
            setLoading(false);
        }
        if (window.innerWidth < 1024) setShowHistory(false);
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

    // --- Data Loaders ---
    async function loadData(silent = false) {
        if (!silent) setLoading(true);
        try {
            const [tasksRes, reposRes] = await Promise.all([
                fetch(`${API_URL}/api/v1/orchestrator/tasks`), // [FIX] Updated endpoint
                fetch(`${API_URL}/api/v1/ingest/list`)        // [FIX] Updated endpoint
            ]);

            if (tasksRes.ok) setTasks(await tasksRes.json());
            if (reposRes.ok) setRepos(await reposRes.json());

        } catch (error) {
            console.error('Connection Error:', error);
            if (!silent) setMessages(prev => [...prev, { role: 'system', content: 'Connection to Genesis Core lost. Retrying...' }]);
        } finally {
            if (!silent) setLoading(false);
        }
    }

    async function fetchSystemStatus() {
        try {
            const res = await fetch(`${API_URL}/health`);
        } catch (e) { console.error("Health check failed", e); }
    }

    // --- File Explorer Logic ---
    async function fetchFiles(repoName: string, path: string) {
        setIsLoadingFiles(true);
        try {
            const cleanName = repoName.replace("REPO: ", "");
            const res = await fetch(`${API_URL}/api/v1/ingest/files?repo_name=${cleanName}&path=${encodeURIComponent(path)}`);
            if (res.ok) {
                const data = await res.json();
                setRepoFiles(data);
                setCurrentPath(path);
            }
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

    // --- System Actions ---
    const switchMode = async () => {
        const newMode = systemMode === "LOCAL" ? "CLOUD" : "LOCAL";
        if (!confirm(`Switch to ${newMode}? Backend will require restart.`)) return;

        await fetch(`${API_URL}/api/v1/system/mode`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: newMode })
        });
        alert(`Switched to ${newMode}. Please restart the Backend Terminal.`);
        setSystemMode(newMode);
        setShowMenu(false);
    };

    const triggerSync = async (direction: "PUSH" | "PULL") => {
        if (!confirm(`${direction} Sync? This acts as a Merge.`)) return;
        await fetch(`${API_URL}/api/v1/system/sync`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ direction, strategy: "MERGE" })
        });
        alert("Sync started in background.");
        setShowMenu(false);
    };

    const triggerBackup = async () => {
        const content = input;
        setInput('');

        try {
            const tempId = 'temp-' + Date.now();
            setMessages(prev => [...prev, {
                id: tempId,
                role: 'user',
                content: content,
                created_at: new Date().toISOString()
            }]);

            await fetch(`${API_URL}/api/v1/orchestrator/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content, role: 'user' })
            });

            await loadData(true);
        } catch (error) {
            console.error("Chat Error:", error);
            alert("Failed to send message to Local Core. Is the backend running?");
        } finally { setLoading(false); }
    };

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
                    provider: selectedProvider, // [NEW] Pass Provider
                    repo_context: expandedRepo
                }),
            });

            const data = await res.json();

            if (data.session_id && data.session_id !== currentSessionId) {
                setCurrentSessionId(data.session_id);
                loadSessions();
            }

            // Extract Metadata if available
            const finalProvider = data.metadata?.provider || selectedProvider;
            const finalModel = data.metadata?.model || selectedModel;

            const botMsg: Message = {
                role: 'assistant',
                content: data.answer || "I processed that but have no specific answer.",
                sources: data.sources,
                model: finalModel + (finalProvider && finalProvider !== "unknown" ? ` @ ${finalProvider}` : "") // [NEW] Show Provider
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
                body: JSON.stringify({ url: url }) // [FIX] Changed repo_url to url
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
                // [FIX] Ensure detail is a string to avoid [object Object]
                const detailStr = typeof errData.detail === 'object' ? JSON.stringify(errData.detail) : (errData.detail || `Server Error ${res.status}`);
                throw new Error(detailStr);
            }

        } catch (e: any) {
            console.error("Ingestion Error:", e);
            let msg = "Unknown Error";

            if (e instanceof Error) msg = e.message;
            else if (typeof e === 'string') msg = e;
            else {
                try { msg = JSON.stringify(e); } catch { msg = String(e); }
                if (msg === "{}") msg = "Check console for details (Error Object)";
            }

            // Try to parse if it looks like JSON
            try {
                const parsed = JSON.parse(msg);
                if (parsed.detail) msg = parsed.detail;
            } catch { }

            alert(`Ingest Failed: ${msg}`);

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
            {/* Header */}
            <header className="h-14 border-b border-gray-800 flex items-center justify-between px-4 bg-[#16161a] shrink-0 z-10">
                <div className="flex items-center gap-3">
                    <button
                        onClick={() => setShowHistory(!showHistory)}
                        className={`p-2 rounded hover:bg-gray-800 transition-colors ${showHistory ? 'text-blue-400' : 'text-gray-400'}`}
                        title="Toggle History"
                    >
                        <Layout className="w-5 h-5" />
                    </button>
                    <div className="flex items-center gap-2">
                        <BrainCircuit className="w-5 h-5 text-indigo-500" />
                        <span className="font-bold tracking-wide text-sm hidden sm:inline">GENESIS ORCHESTRATOR</span>
                    </div>
                    {/* Status Pill */}
                    <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-mono border ${isPolling ? 'bg-emerald-900/30 border-emerald-500/30 text-emerald-400' : 'bg-red-900/30 border-red-500/30 text-red-400'}`}>
                        {isPolling ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
                        {isPolling ? 'ONLINE' : 'OFFLINE'}
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <button
                        onClick={handleNewChat}
                        className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-xs font-medium transition-colors"
                    >
                        <RefreshCcw className="w-3.5 h-3.5" />
                        New Chat
                    </button>

                    {/* Provider Selector [NEW] */}
                    <div className="relative group">
                        <select
                            value={selectedProvider}
                            onChange={(e) => setSelectedProvider(e.target.value)}
                            className="bg-[#0a0a0c] border border-gray-700 text-xs rounded px-2 py-1 outline-none text-gray-300 hover:border-indigo-500 transition-colors cursor-pointer appearance-none pr-6"
                        >
                            <option value="Sambanova">🚀 Sambanova (Fast)</option>
                            <option value="Groq">🏎️ Groq (Llama)</option>
                        </select>
                        <div className="absolute right-2 top-1/2 transform -translate-y-1/2 pointer-events-none opacity-50">
                            <ArrowDown className="w-3 h-3" />
                        </div>
                    </div>

                    {/* Model Selector */}
                    <div className="relative group">
                        <select
                            value={selectedModel}
                            onChange={(e) => setSelectedModel(e.target.value)}
                            className="bg-[#0a0a0c] border border-gray-700 text-xs rounded px-2 py-1 outline-none text-gray-300 hover:border-indigo-500 transition-colors cursor-pointer appearance-none pr-6"
                        >
                            <optgroup label="SambaNova - DeepSeek">
                                <option value="DeepSeek-R1">🧠 DeepSeek R1</option>
                                <option value="DeepSeek-R1-Distill-Llama-70B">🧪 DeepSeek R1 Distill 70B</option>
                                <option value="DeepSeek-V3">🤖 DeepSeek V3</option>
                            </optgroup>
                            <optgroup label="SambaNova - Meta Llama">
                                <option value="Meta-Llama-3.3-70B-Instruct">🦙 Llama 3.3 70B (Latest)</option>
                                <option value="Meta-Llama-3.1-8B-Instruct">⚡ Llama 8B (Fast)</option>
                            </optgroup>
                        </select>
                        <div className="absolute right-2 top-1/2 transform -translate-y-1/2 pointer-events-none opacity-50">
                            <ArrowDown className="w-3 h-3" />
                        </div>
                    </div>

                    {/* System Mode Toggle */}
                    <div className="flex bg-black/40 p-1 rounded-lg border border-gray-800">
                        <button
                            onClick={() => setSystemMode("LOCAL")}
                            className={`px-3 py-1 rounded text-[10px] font-bold transition-all ${systemMode === "LOCAL" ? "bg-indigo-600 text-white shadow-lg" : "text-gray-500 hover:text-gray-300"}`}
                        >
                            LOCAL
                        </button>
                        <button
                            onClick={() => setSystemMode("CLOUD")}
                            className={`px-3 py-1 rounded text-[10px] font-bold transition-all ${systemMode === "CLOUD" ? "bg-purple-600 text-white shadow-lg" : "text-gray-500 hover:text-gray-300"}`}
                        >
                            CLOUD
                        </button>
                    </div>
                </div>
            </header>

            {/* Main Content Area */}
            <div className="flex-1 flex overflow-hidden">

                {/* History Sidebar */}
                <div className={`${showHistory ? 'w-64 border-r' : 'w-0'} border-gray-800 bg-[#131316] transition-all duration-300 flex flex-col overflow-hidden`}>
                    <div className="p-3 border-b border-gray-800">
                        <button
                            onClick={handleNewChat}
                            className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-gray-800 hover:bg-gray-700 text-gray-200 rounded-md text-xs font-medium transition-colors"
                        >
                            <RefreshCcw className="w-4 h-4" />
                            New Conversation
                        </button>
                    </div>
                    <div className="flex-1 overflow-y-auto p-2 space-y-1">
                        {sessions.map(session => (
                            <div
                                key={session.id}
                                onClick={() => handleSelectSession(session.id)}
                                className={`group flex items-center justify-between p-2 rounded-md cursor-pointer text-xs ${currentSessionId === session.id ? 'bg-indigo-900/30 text-indigo-200 border border-indigo-500/30' : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'}`}
                            >
                                <div className="flex items-center gap-2 truncate flex-1">
                                    <MessageSquare className="w-3.5 h-3.5 flex-shrink-0" />
                                    <span className="truncate">{session.title || "Untitled Chat"}</span>
                                </div>
                                <div className="hidden group-hover:flex items-center gap-1">
                                    <button
                                        onClick={(e) => handleCloneSession(session.id, e)}
                                        className="p-1 hover:bg-blue-900/50 rounded text-blue-400"
                                        title="Clone / Fork Chat"
                                    >
                                        <Copy className="w-3 h-3" />
                                    </button>
                                    <button
                                        onClick={(e) => handleDeleteSession(session.id, e)}
                                        className="p-1 hover:bg-red-900/50 rounded text-red-400"
                                        title="Delete Chat"
                                    >
                                        <Trash2 className="w-3 h-3" />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Left: Chat Area (Visible if Active) */}
                <div className={`flex-1 flex flex-col min-w-0 border-r border-gray-800 ${activeTab === 'roadmap' ? 'block' : 'hidden md:block'}`}>
                    {/* Chat Messages */}
                    <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 space-y-4">
                        {messages.map((msg, i) => {
                            // DeepSeek & Reasoning Parsing
                            let content = msg.content;
                            let reasoning = "";
                            if (content.includes("<think>")) {
                                const parts = content.split("</think>");
                                if (parts.length > 1) {
                                    reasoning = parts[0].replace("<think>", "").trim();
                                    content = parts[1].trim();
                                }
                            }

                            return (
                                <div key={msg.id || i} className={`w-full flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                    <div className={`max-w-[90%] sm:max-w-[85%] p-3 rounded-lg text-sm ${msg.role === 'user'
                                        ? 'bg-purple-900/20 text-purple-100 border border-purple-500/30'
                                        : 'bg-gray-800/50 text-gray-200 border border-gray-700'
                                        }`}>
                                        <div className="flex items-center gap-2 mb-1 text-[10px] opacity-50 uppercase tracking-widest font-bold">
                                            {msg.role === 'user' ? <User className="w-3 h-3" /> : <Bot className="w-3 h-3" />}
                                            {msg.role === 'user' ? "USER" : (msg.model || "ASSISTANT")}
                                        </div>

                                        {/* Reasoning Block (DeepSeek) */}
                                        {reasoning && (
                                            <div className="mb-2 group relative inline-block">
                                                <div className="flex items-center gap-1 text-[10px] text-gray-500 bg-gray-900/50 px-2 py-1 rounded cursor-help transition-colors hover:text-purple-400 border border-gray-800 hover:border-purple-900">
                                                    <Brain className="w-3 h-3" />
                                                    View Reasoning
                                                </div>
                                                {/* TooltipOnHover */}
                                                <div className="hidden group-hover:block absolute left-0 top-6 z-50 w-64 md:w-96 bg-[#0f0f13] border border-gray-700 p-3 rounded shadow-2xl text-xs text-gray-400 whitespace-pre-wrap leading-relaxed">
                                                    <div className="text-[9px] font-bold text-gray-600 mb-1 tracking-wider">CHAIN OF THOUGHT</div>
                                                    {reasoning}
                                                </div>
                                            </div>
                                        )}

                                        <div className="whitespace-pre-wrap break-words leading-relaxed">{content}</div>
                                    </div>
                                </div>
                            );
                        })}
                        {messages.length === 0 && <div className="text-center text-gray-600 mt-20">Start a new conversation.</div>}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <div className="p-3 bg-[#16161a] border-t border-gray-800">
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                                className="flex-1 bg-[#0f0f13] border border-gray-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-purple-500"
                                placeholder="Instruct the Supreme Architect..."
                            />
                            <button onClick={sendMessage} disabled={loading} className="bg-purple-600 hover:bg-purple-500 text-white p-2 rounded-lg"><Send className="w-4 h-4" /></button>
                        </div>
                    </div>
                </div>

                {/* Right Panel: Knowledge/Files */}
                <div className="w-80 border-l border-gray-800 flex flex-col bg-[#111115]">
                    <div className="flex border-b border-gray-800">
                        <button onClick={() => setActiveTab('roadmap')} className={`flex-1 py-3 text-xs font-bold ${activeTab === 'roadmap' ? 'text-purple-400 border-b-2 border-purple-500' : 'text-gray-500'}`}>TASKS</button>
                        <button onClick={() => setActiveTab('knowledge')} className={`flex-1 py-3 text-xs font-bold ${activeTab === 'knowledge' ? 'text-purple-400 border-b-2 border-purple-500' : 'text-gray-500'}`}>KNOWLEDGE</button>
                    </div>

                    <div className="flex-1 overflow-y-auto p-4">
                        {activeTab === 'roadmap' ? (
                            <div className="space-y-3">
                                {tasks.map(task => (
                                    <div key={task.id} className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
                                        <div className="flex justify-between items-start mb-1">
                                            <span className="font-medium text-sm text-gray-200">{task.title}</span>
                                            <span className={`text-[10px] px-1.5 py-0.5 rounded ${task.status === 'DONE' ? 'bg-green-900/50 text-green-400' : 'bg-yellow-900/50 text-yellow-400'}`}>{task.status}</span>
                                        </div>
                                        <div className="text-xs text-gray-500 flex items-center gap-1">
                                            <Bot className="w-3 h-3" /> {task.assigned_agent}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div>
                                <div className="mb-4">
                                    <button onClick={() => setShowIngestModal(true)} className="w-full py-2 bg-gray-800 hover:bg-gray-700 border border-gray-600 rounded flex items-center justify-center gap-2 text-xs font-bold text-gray-300">
                                        <Cloud className="w-3 h-3" /> Ingest Repo
                                    </button>
                                </div>
                                <div className="space-y-2">
                                    {repos.map(repo => (
                                        <div key={repo.id} className="border border-gray-700 rounded-lg overflow-hidden">
                                            <div
                                                className="p-2 bg-gray-800/50 flex items-center gap-2 cursor-pointer hover:bg-gray-800"
                                                onClick={() => {
                                                    if (expandedRepo === repo.name) {
                                                        setExpandedRepo(null);
                                                    } else {
                                                        setExpandedRepo(repo.name);
                                                        fetchFiles(repo.name, "");
                                                    }
                                                }}
                                            >
                                                {expandedRepo === repo.name ? <ArrowDown className="w-3 h-3 text-purple-400" /> : <ArrowRight className="w-3 h-3 text-gray-500" />}
                                                <Database className="w-3 h-3 text-blue-400" />
                                                <span className="text-xs font-bold truncate flex-1">{repo.name.replace("REPO: ", "")}</span>
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        fetchFiles(repo.name, "");
                                                    }}
                                                    className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
                                                    title="Refresh Files"
                                                >
                                                    <RefreshCcw className="w-3 h-3" />
                                                </button>
                                            </div>
                                            {expandedRepo === repo.name && (
                                                <div className="p-2 bg-[#0a0a0c] border-t border-gray-700">
                                                    {isLoadingFiles ? (
                                                        <div className="text-xs text-gray-500 animate-pulse">Loading file tree...</div>
                                                    ) : (
                                                        <div className="space-y-1 pl-2">
                                                            {repoFiles.map((file, idx) => (
                                                                <div
                                                                    key={idx}
                                                                    className="flex items-center gap-2 text-xs text-gray-400 hover:text-white cursor-pointer"
                                                                    onClick={() => {
                                                                        if (file.type === 'file') fetchContent(repo.name, file.path);
                                                                        else fetchFiles(repo.name, file.path); // [FIX] Recursive Drill-down
                                                                    }}
                                                                >
                                                                    {file.type === 'dir' ? <Folder className="w-3 h-3 text-yellow-600" /> : <FileCode className="w-3 h-3 text-blue-500" />}
                                                                    {file.name}
                                                                </div>
                                                            ))}
                                                        </div>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Ingest Modal */}
            {showIngestModal && (
                <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
                    <div className="bg-[#1a1a20] border border-gray-700 rounded-xl shadow-2xl w-full max-w-lg p-6">
                        <h3 className="font-bold text-gray-200 mb-4">Ingest Repository</h3>
                        <input
                            type="text"
                            className="w-full bg-[#0f0f13] border border-gray-600 rounded px-4 py-2 text-white mb-4"
                            placeholder="https://github.com/..."
                            value={ingestUrl}
                            onChange={e => setIngestUrl(e.target.value)}
                        />
                        <div className="flex justify-end gap-2">
                            <button onClick={() => setShowIngestModal(false)} className="px-4 py-2 text-gray-400">Cancel</button>
                            <button onClick={handleIngestSubmit} className="px-4 py-2 bg-purple-600 text-white rounded">Start</button>
                        </div>
                    </div>
                </div>
            )}

            {/* File Editor Modal */}
            {selectedFile && (
                <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4">
                    <div className="bg-[#101014] border border-gray-700 rounded-lg shadow-2xl w-full max-w-4xl h-[85vh] flex flex-col">
                        {/* Toolbar */}
                        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700 bg-[#16161a]">
                            <div className="flex items-center gap-2">
                                <FileCode className="w-4 h-4 text-blue-400" />
                                <span className="font-mono text-sm font-bold">{selectedFile.name}</span>
                                {isEditing && <span className="text-xs text-yellow-500 italic">(Unsaved Changes)</span>}
                            </div>
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={saveCurrentFile}
                                    disabled={!isEditing || isSaving}
                                    className={`flex items-center gap-1 px-3 py-1.5 rounded text-xs font-bold transition-colors ${!isEditing ? 'text-gray-500 cursor-not-allowed' : 'bg-green-600 hover:bg-green-500 text-white'}`}
                                >
                                    {isSaving ? <RefreshCcw className="w-3 h-3 animate-spin" /> : <Save className="w-3 h-3" />}
                                    Save
                                </button>
                                <button
                                    onClick={() => setSelectedFile(null)}
                                    className="p-1.5 hover:bg-gray-700 rounded text-gray-400"
                                >
                                    <X className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                        {/* Editor */}
                        <div className="flex-1 relative">
                            <textarea
                                className="w-full h-full bg-[#0a0a0c] text-gray-300 font-mono text-xs p-4 focus:outline-none resize-none leading-relaxed"
                                value={selectedFile.content} // Using defaultVal approach or controlled?
                                // If content updates from backend, we need useEffect. For now, simplistic:
                                onChange={(e) => {
                                    setEditorContent(e.target.value);
                                    setIsEditing(true);
                                    setSelectedFile(prev => prev ? { ...prev, content: e.target.value } : null);
                                }}
                            />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
