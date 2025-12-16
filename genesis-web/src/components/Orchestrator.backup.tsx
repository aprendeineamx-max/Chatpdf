import { useState, useEffect } from 'react';
import { Send, CheckCircle2, Circle, Bot, User, BrainCircuit, WifiOff, Wifi, Cloud, Database, RefreshCcw, Save, ArrowUp, ArrowDown, X, FileCode, Folder, ArrowLeft, Layout, ArrowRight } from 'lucide-react';
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
        loadData();
        fetchSystemStatus();

        // Polling every 5 seconds for local updates (replacing Realtime)
        const interval = setInterval(() => {
            loadData(true);
        }, 5000);

        setIsPolling(true);

        return () => clearInterval(interval);
    }, []);

    // Update editor content when file changes
    useEffect(() => {
        if (selectedFile) {
            setEditorContent(selectedFile.content);
            setIsEditing(false); // Reset to read mode on file switch
        }
    }, [selectedFile]);

    // Fetch Files for Explorer
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

    // Fetch File Content
    async function fetchContent(repoName: string, path: string) {
        const cleanName = repoName.replace("REPO: ", "");
        try {
            const res = await fetch(`${API_URL}/api/v1/ingest/content?repo_name=${cleanName}&path=${encodeURIComponent(path)}`);
            if (res.ok) {
                const data = await res.json();
                setSelectedFile({ name: path.split('/').pop() || 'File', content: data.content });
            }
        } catch (e) {
            console.error(e);
            alert("Failed to load file content.");
        }
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
                    path: selectedFile.name, // Note: In a real app we need full path here, assuming selectedFile.name or currentPath logic is handled
                    content: editorContent
                })
            });
            if (res.ok) {
                // Update local state to reflect save
                setSelectedFile(prev => prev ? ({ ...prev, content: editorContent }) : null);
                setIsEditing(false);
            } else {
                throw new Error("Save returned " + res.status);
            }
        } catch (e) {
            alert("Failed to save file.");
            console.error(e);
        } finally {
            setIsSaving(false);
        }
    }

    async function loadData(silent = false) {
        try {
            await Promise.all([fetchTasks(), fetchHistory(), fetchRepos()]);
        } catch (e) {
            if (!silent) console.error("Pulse Failed:", e);
            setIsPolling(false);
        }
    }

    async function fetchSystemStatus() {
        try {
            const res = await fetch(`${API_URL}/api/v1/system/status`);
            if (res.ok) {
                const data = await res.json();
                setSystemMode(data.mode);
            }
        } catch (e) { console.error("Status check failed", e); }
    }

    async function fetchTasks() {
        try {
            const res = await fetch(`${API_URL}/api/v1/orchestrator/tasks`);
            if (res.ok) {
                const data = await res.json();
                if (Array.isArray(data)) setTasks(data);
            }
        } catch (e) { /* ignore poll error */ }
    }

    async function fetchHistory() {
        try {
            const res = await fetch(`${API_URL}/api/v1/orchestrator/chat`);
            if (res.ok) {
                const data = await res.json();
                if (Array.isArray(data)) setMessages(data);
            }
        } catch (e) { /* ignore poll error */ }
    }

    async function fetchRepos() {
        try {
            const res = await fetch(`${API_URL}/api/v1/ingest/list`);
            if (res.ok) {
                const data = await res.json();
                if (Array.isArray(data)) setRepos(data);
            }
        } catch (e) { /* ignore */ }
    }

    // --- SYSTEM ACTIONS ---
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
        setInput(''); // Clear immediately

        try {
            // Optimistic update
            const tempId = 'temp-' + Date.now();
            setMessages(prev => [...prev, {
                id: tempId,
                role: 'user',
                content: content,
                created_at: new Date().toISOString()
            }]);

            const res = await fetch(`${API_URL}/api/v1/orchestrator/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content, role: 'user' })
            });

            if (!res.ok) throw new Error("API Error");

            // Reload to get the real ID and any immediate agent response
            await loadData(true);

        } catch (error) {
            console.error("Chat Error:", error);
            alert("Failed to send message to Local Core. Is the backend running?");
        } finally {
            setLoading(false);
        }
    };

    const sendMessage = async () => {
        if (!input.trim() || loading) return;

        const content = input;
        setInput('');
        setLoading(true);

        // Optimistic UI
        const tempId = 'temp-' + Date.now();
        setMessages(prev => [...prev, {
            id: tempId,
            role: 'user',
            content: content,
            created_at: new Date().toISOString()
        }]);

        try {
            const res = await fetch(`${API_URL}/api/v1/orchestrator/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content, role: 'user' })
            });

            if (!res.ok) throw new Error("Failed to send");

            // Refresh to get AI response
            await loadData(true);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
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
                body: JSON.stringify({ repo_url: url })
            });

            if (res.ok) {
                setMessages(prev => [...prev, {
                    id: 'sys-done-' + Date.now(),
                    role: 'system',
                    content: `✅ INGESTION QUEUED. The Architect is analyzing...`,
                    created_at: new Date().toISOString()
                }]);
            } else {
                const errText = await res.text(); // Read failure reason
                throw new Error(errText || "API Failed");
            }

        } catch (e: any) {
            console.error("Ingestion Error:", e);
            let msg = e.message;
            try {
                const json = JSON.parse(msg);
                if (json.detail) msg = json.detail;
            } catch (x) { }

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
        <div className="flex h-full bg-[#0f0f13] relative overflow-hidden">
            {/* INGEST MODAL */}
            {showIngestModal && (
                <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
                    <div className="bg-[#1a1a20] border border-gray-700 rounded-xl shadow-2xl w-full max-w-lg overflow-hidden">
                        <div className="p-4 border-b border-gray-700 flex justify-between items-center bg-[#16161a]">
                            <h3 className="font-bold text-gray-200 flex items-center gap-2">
                                <Cloud className="w-5 h-5 text-purple-400" />
                                Ingest GitHub Repository
                            </h3>
                            <button onClick={() => setShowIngestModal(false)} className="text-gray-500 hover:text-white">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <div className="p-6">
                            <p className="text-sm text-gray-400 mb-4">
                                Enter the full HTTPS URL of the public repository you want the Architect to study.
                            </p>
                            <input
                                type="text"
                                autoFocus
                                placeholder="https://github.com/username/repo"
                                className="w-full bg-[#0f0f13] border border-gray-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-purple-500 mb-4"
                                value={ingestUrl}
                                onChange={(e) => setIngestUrl(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleIngestSubmit()}
                            />
                            <div className="flex justify-end gap-3">
                                <button onClick={() => setShowIngestModal(false)} className="px-4 py-2 text-gray-400 hover:text-white text-sm">Cancel</button>
                                <button onClick={handleIngestSubmit} className="bg-purple-600 hover:bg-purple-500 text-white px-6 py-2 rounded-lg font-medium transition-colors">
                                    Start Ingestion
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Mobile Panel Backdrop */}
            {isMobilePanelOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-30 xl:hidden backdrop-blur-sm"
                    onClick={() => setIsMobilePanelOpen(false)}
                />
            )}

            {/* Left: Chat Area */}
            <div className="flex-1 flex flex-col min-w-0 border-r border-gray-800">
                <div className="h-14 border-b border-gray-800 flex items-center justify-between px-4 sm:px-6 bg-[#16161a]">
                    <div className="flex items-center min-w-0">
                        <BrainCircuit className="w-5 h-5 text-purple-400 mr-2 flex-shrink-0" />
                        <h2 className="font-bold text-gray-200 text-sm truncate">Supreme Architect</h2>
                        <span className="ml-2 px-2 py-0.5 text-[10px] bg-gray-800 text-gray-400 rounded border border-gray-700 flex-shrink-0">
                            {systemMode}
                        </span>
                    </div>

                    {/* System Menu & Mobile Toggle */}
                    <div className="flex items-center gap-3">
                        {/* Mobile Panel Toggle */}
                        <button
                            onClick={() => setIsMobilePanelOpen(!isMobilePanelOpen)}
                            className="p-2 hover:bg-gray-800 rounded-lg text-gray-400 transition-colors xl:hidden"
                        >
                            <Layout className="w-5 h-5" />
                        </button>

                        <div className="relative">
                            <button
                                onClick={() => setShowMenu(!showMenu)}
                                className="p-2 hover:bg-gray-800 rounded-lg text-gray-400 transition-colors"
                                title="System Settings"
                            >
                                <RefreshCcw className="w-4 h-4" />
                            </button>

                            {showMenu && (
                                <div className="absolute right-0 top-full mt-2 w-48 bg-[#1a1a20] border border-gray-700 rounded-lg shadow-xl z-40 p-1">
                                    <div className="text-xs font-bold text-gray-500 px-3 py-2 uppercase">Neural Link</div>
                                    <button onClick={switchMode} className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 rounded flex items-center gap-2">
                                        {systemMode === 'LOCAL' ? <Cloud className="w-3 h-3" /> : <Database className="w-3 h-3" />}
                                        Switch to {systemMode === 'LOCAL' ? 'Cloud' : 'Local'}
                                    </button>
                                    <div className="h-px bg-gray-700 my-1"></div>
                                    <button onClick={() => triggerSync("PULL")} className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 rounded flex items-center gap-2">
                                        <ArrowDown className="w-3 h-3 text-blue-400" />
                                        Pull from Cloud
                                    </button>
                                    <button onClick={() => triggerSync("PUSH")} className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 rounded flex items-center gap-2">
                                        <ArrowUp className="w-3 h-3 text-green-400" />
                                        Push to Cloud
                                    </button>
                                    <div className="h-px bg-gray-700 my-1"></div>
                                    <button onClick={triggerBackup} className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 rounded flex items-center gap-2">
                                        <Save className="w-3 h-3 text-yellow-500" />
                                        Backup Local DB
                                    </button>
                                    <div className="h-px bg-gray-700 my-1"></div>
                                    <button onClick={() => {
                                        setShowMenu(false);
                                        setShowIngestModal(true);
                                    }} className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 rounded flex items-center gap-2 cursor-pointer">
                                        <Cloud className="w-3 h-3 text-purple-400" />
                                        Ingest Repo (Vision)
                                    </button>
                                </div>
                            )}
                        </div>

                        {/* Status Indicator */}
                        <div className="hidden sm:flex items-center gap-2 text-xs text-gray-500 border-l border-gray-800 pl-4">
                            {isPolling ? (
                                <>
                                    <Wifi className="w-3 h-3 text-green-500" />
                                    <span className="hidden sm:inline">ONLINE</span>
                                </>
                            ) : (
                                <>
                                    <WifiOff className="w-3 h-3 text-red-500" />
                                    <span className="hidden sm:inline">OFFLINE</span>
                                </>
                            )}
                        </div>
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 space-y-4">
                    {messages.map((msg, i) => (
                        <div key={msg.id || i} className={`w-full flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[90%] sm:max-w-[85%] p-3 rounded-lg text-sm ${msg.role === 'user'
                                ? 'bg-purple-900/20 text-purple-100 border border-purple-500/30'
                                : 'bg-gray-800/50 text-gray-200 border border-gray-700'
                                }`}>
                                <div className="flex items-center gap-2 mb-1 text-[10px] opacity-50 uppercase tracking-widest font-bold">
                                    {msg.role === 'user' ? <User className="w-3 h-3" /> : <Bot className="w-3 h-3" />}
                                    {msg.role}
                                </div>
                                <div className="whitespace-pre-wrap break-words leading-relaxed">{msg.content}</div>
                            </div>
                        </div>
                    ))}
                    {messages.length === 0 && (
                        <div className="text-center text-gray-600 mt-20">
                            No history found. Connection established.
                        </div>
                    )}
                </div>

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
                        <button
                            onClick={sendMessage}
                            disabled={loading}
                            className="bg-purple-600 hover:bg-purple-500 text-white p-2 rounded-lg transition-colors flex-shrink-0"
                        >
                            <Send className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Right: Roadmap / Knowledge (Responsive) */}
            <div className={`
                fixed inset-y-0 right-0 z-40 w-80 bg-[#111115] border-l border-gray-800 flex flex-col transition-transform duration-300 ease-in-out shadow-2xl
                xl:static xl:w-72 xl:translate-x-0 xl:shadow-none
                ${isMobilePanelOpen ? 'translate-x-0' : 'translate-x-full'}
            `}>
                <div className="h-14 border-b border-gray-800 flex items-center justify-between px-4 bg-[#16161a]">
                    <div className="flex bg-gray-900 rounded-lg p-1 w-full mr-2">
                        <button
                            onClick={() => setActiveTab('roadmap')}
                            className={`flex-1 py-1 text-xs font-bold rounded-md transition-all ${activeTab === 'roadmap' ? 'bg-purple-600 text-white shadow' : 'text-gray-500 hover:text-gray-300'
                                }`}
                        >
                            ROADMAP
                        </button>
                        <button
                            onClick={() => setActiveTab('knowledge')}
                            className={`flex-1 py-1 text-xs font-bold rounded-md transition-all ${activeTab === 'knowledge' ? 'bg-purple-600 text-white shadow' : 'text-gray-500 hover:text-gray-300'
                                }`}
                        >
                            KNOWLEDGE
                        </button>
                    </div>
                    {/* Close Button for Mobile */}
                    <button
                        onClick={() => setIsMobilePanelOpen(false)}
                        className="xl:hidden p-1 text-gray-500 hover:text-white"
                    >
                        <ArrowRight className="w-5 h-5" />
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-4 space-y-3">
                    {activeTab === 'roadmap' ? (
                        <>
                            {tasks.map(task => (
                                <div key={task.id} className="bg-[#1a1a20] p-3 rounded-lg border border-gray-800 flex items-start gap-3 hover:border-purple-500/30 transition-all">
                                    {task.status === 'DONE' ? (
                                        <CheckCircle2 className="w-5 h-5 text-emerald-500 mt-0.5 flex-shrink-0" />
                                    ) : task.status === 'IN_PROGRESS' ? (
                                        <div className="w-5 h-5 rounded-full border-2 border-yellow-500 border-t-transparent animate-spin mt-0.5 flex-shrink-0" />
                                    ) : (
                                        <Circle className="w-5 h-5 text-gray-600 mt-0.5 flex-shrink-0" />
                                    )}
                                    <div className="min-w-0">
                                        <div className="text-sm font-medium text-gray-200 truncate">{task.title}</div>
                                        <div className="text-xs text-gray-500 mt-1 flex items-center gap-1">
                                            <span className="bg-gray-800 px-1 rounded truncate max-w-[100px]">{task.assigned_agent}</span>
                                            {task.status}
                                        </div>
                                    </div>
                                </div>
                            ))}
                            {tasks.length === 0 && (
                                <div className="text-sm text-gray-600 text-center italic mt-10">
                                    Roadmap empty. Wait for Architect assignments.
                                </div>
                            )}
                        </>
                    ) : (
                        <>
                            {repos.map(repo => {
                                let StatusIcon = Database;
                                let statusColor = "text-blue-400";
                                let isSpinning = false;
                                let statusLabel = "READY";

                                if (repo.status === "CLONING" || repo.status === "CLONING_GIT") {
                                    StatusIcon = RefreshCcw;
                                    statusColor = "text-yellow-400";
                                    isSpinning = true;
                                    statusLabel = "CLONING";
                                } else if (repo.status === "ANALYZING" || repo.status === "SAVING") {
                                    StatusIcon = BrainCircuit;
                                    statusColor = "text-purple-400";
                                    isSpinning = true;
                                    statusLabel = "ANALYZING";
                                } else if (repo.status === "FAILED") {
                                    StatusIcon = WifiOff;
                                    statusColor = "text-red-500";
                                    statusLabel = "FAILED";
                                }

                                return (
                                    <div key={repo.id}
                                        onClick={() => {
                                            if (repo.status === "CLONING" || repo.status === "ANALYZING") return;
                                            setExpandedRepo(repo.name);
                                            fetchFiles(repo.name, "");
                                        }}
                                        className="bg-[#1a1a20] p-3 rounded-lg border border-gray-800 hover:border-blue-500/30 transition-all group cursor-pointer relative overflow-hidden"
                                    >
                                        {isSpinning && (
                                            <div className="absolute top-0 left-0 w-full h-0.5 bg-gray-700">
                                                <div className="h-full bg-blue-500 animate-[loading_1s_ease-in-out_infinite]"></div>
                                            </div>
                                        )}

                                        <div className="flex items-center gap-2 mb-2">
                                            <StatusIcon className={`w-4 h-4 ${statusColor} ${isSpinning ? 'animate-spin' : ''} flex-shrink-0`} />
                                            <div className="text-sm font-bold text-gray-200 truncate" title={repo.name}>
                                                {repo.name.replace('REPO: ', '')}
                                            </div>
                                        </div>
                                        <div className="text-xs text-gray-500 flex justify-between items-center">
                                            <span>
                                                {repo.status === 'FAILED'
                                                    ? <span className="text-red-400" title={repo.error}>{repo.error ? 'Error (Hover)' : 'Failed'}</span>
                                                    : (repo.timestamp ? new Date(repo.timestamp).toLocaleDateString() : 'Just now')
                                                }
                                            </span>
                                            <span className={`text-[10px] uppercase font-bold tracking-wider ${statusColor}`}>
                                                {statusLabel}
                                            </span>
                                        </div>
                                    </div>
                                );
                            })}
                            {repos.length === 0 && (
                                <div className="text-sm text-gray-600 text-center italic mt-10">
                                    No repositories ingested yet.
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>

            {/* FILE EXPLORER OVERLAY */}
            {expandedRepo && (
                <div className="absolute inset-0 bg-[#0f0f13] z-50 flex flex-col">
                    {/* Header */}
                    <div className="h-14 border-b border-gray-800 flex items-center justify-between px-4 bg-[#111115]">
                        <div className="flex items-center gap-3">
                            <button
                                onClick={() => {
                                    setExpandedRepo(null);
                                    setCurrentPath("");
                                }}
                                className="p-2 hover:bg-gray-800 rounded-lg text-gray-400 hover:text-white transition-colors"
                            >
                                <ArrowLeft className="w-5 h-5" />
                            </button>
                            <div>
                                <h2 className="font-bold text-gray-200 flex items-center gap-2">
                                    <Database className="w-4 h-4 text-purple-400" />
                                    {expandedRepo.replace("REPO: ", "")}
                                </h2>
                                <div className="text-xs text-gray-500 font-mono">
                                    /{currentPath}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Main Content */}
                    <div className="flex-1 flex overflow-hidden">
                        {/* Sidebar: File Tree */}
                        <div className="w-72 border-r border-gray-800 bg-[#111115] flex flex-col hidden lg:flex">
                            <div className="p-3 border-b border-gray-800 text-xs font-bold text-gray-500 uppercase tracking-wider">
                                Explorer
                            </div>
                            <div className="flex-1 overflow-y-auto p-2">
                                {currentPath !== "" && (
                                    <div
                                        onClick={() => {
                                            const parentPath = currentPath.split('/').slice(0, -1).join('/');
                                            fetchFiles(expandedRepo, parentPath);
                                        }}
                                        className="flex items-center gap-2 px-3 py-2 text-sm text-gray-400 hover:bg-[#1a1a20] hover:text-white rounded cursor-pointer mb-2"
                                    >
                                        <ArrowLeft className="w-3 h-3" />
                                        <span>..</span>
                                    </div>
                                )}
                                {isLoadingFiles ? (
                                    <div className="text-center text-gray-600 py-10 text-xs">Loading structure...</div>
                                ) : repoFiles.map((file, i) => (
                                    <div
                                        key={i}
                                        onClick={() => {
                                            if (file.type === 'dir') {
                                                fetchFiles(expandedRepo, file.path);
                                            } else {
                                                fetchContent(expandedRepo, file.path);
                                            }
                                        }}
                                        className={`flex items-center gap-2 px-3 py-1.5 text-sm rounded cursor-pointer transition-colors ${selectedFile?.name === file.name.split('/').pop() && file.type === 'file'
                                            ? 'bg-blue-900/30 text-blue-200'
                                            : 'text-gray-400 hover:bg-[#1a1a20] hover:text-white'
                                            }`}
                                    >
                                        {file.type === 'dir' ? (
                                            <Folder className="w-3.5 h-3.5 text-yellow-500/80" />
                                        ) : (
                                            <FileCode className="w-3.5 h-3.5 text-blue-400/80" />
                                        )}
                                        <span className="truncate">{file.name}</span>
                                    </div>
                                ))}
                                {repoFiles.length === 0 && !isLoadingFiles && (
                                    <div className="text-center text-gray-600 py-10 text-xs italic">
                                        Empty directory
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Editor View with Toolbar */}
                        <div className="flex-1 bg-[#1e1e1e] flex flex-col overflow-hidden">
                            {selectedFile ? (
                                <>
                                    {/* Tab Bar / Toolbar */}
                                    <div className="h-10 border-b border-[#252526] bg-[#2d2d2d] flex items-center justify-between px-4 select-none">
                                        {/* Tab */}
                                        <div className="flex items-center gap-2 text-xs text-[#cccccc] font-medium bg-[#1e1e1e] h-full px-3 border-t-2 border-blue-500 min-w-[120px]">
                                            <FileCode className="w-3.5 h-3.5 text-blue-400" />
                                            {selectedFile.name}
                                            {isEditing && <span className="w-2 h-2 rounded-full bg-white ml-2" />}
                                        </div>

                                        {/* Toolbar Actions */}
                                        <div className="flex items-center gap-2">
                                            <button
                                                onClick={() => setIsEditing(!isEditing)}
                                                className={`p-1.5 rounded transition-colors ${isEditing ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-700'}`}
                                                title={isEditing ? "View Mode" : "Edit Mode"}
                                            >
                                                {isEditing ? <Database className="w-4 h-4" /> : <RefreshCcw className="w-4 h-4 rotate-45" />}
                                            </button>

                                            {isEditing && (
                                                <button
                                                    onClick={saveCurrentFile}
                                                    disabled={isSaving}
                                                    className="flex items-center gap-2 px-3 py-1 bg-green-600 hover:bg-green-500 text-white text-xs rounded transition-colors disabled:opacity-50"
                                                >
                                                    <Save className="w-3 h-3" />
                                                    {isSaving ? "Saving..." : "Save"}
                                                </button>
                                            )}
                                        </div>
                                    </div>

                                    {/* Monaco Editor */}
                                    <div className="flex-1 overflow-hidden relative">
                                        <div className={`absolute inset-0 ${isEditing ? 'border-2 border-blue-900/30' : ''}`}>
                                            <Editor
                                                height="100%"
                                                language={getLanguageFromPath(selectedFile.name)}
                                                theme="vs-dark"
                                                value={editorContent}
                                                onChange={(val) => setEditorContent(val || "")}
                                                options={{
                                                    readOnly: !isEditing,
                                                    minimap: { enabled: true },
                                                    scrollBeyondLastLine: false,
                                                    fontSize: 14,
                                                    fontFamily: "'JetBrains Mono', 'Fira Code', Consolas, monospace",
                                                    padding: { top: 10 }
                                                }}
                                            />
                                        </div>
                                    </div>
                                </>
                            ) : (
                                <div className="flex-1 flex flex-col items-center justify-center text-[#555] gap-4">
                                    <div className="opacity-20 text-9xl font-sans font-bold">VS</div>
                                    <p className="text-sm">Select a file from the explorer to view code.</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
