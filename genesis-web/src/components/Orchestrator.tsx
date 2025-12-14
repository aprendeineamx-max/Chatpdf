
import { useState, useEffect } from 'react';
import { Send, CheckCircle2, Circle, Bot, User, BrainCircuit, WifiOff, Wifi, Cloud, Database, RefreshCcw, Save, ArrowUpCircle, ArrowDownCircle } from 'lucide-react';

// Use the API URL from environment or default to local backend
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

interface Task {
    id: string;
    title: string;
    status: 'PENDING' | 'IN_PROGRESS' | 'DONE';
    assigned_agent: string;
}

interface Message {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    created_at: string;
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

    async function loadData(silent = false) {
        try {
            await Promise.all([fetchTasks(), fetchHistory()]);
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
                setTasks(data);
            }
        } catch (e) { /* ignore poll error */ }
    }

    async function fetchHistory() {
        try {
            const res = await fetch(`${API_URL}/api/v1/orchestrator/chat`);
            if (res.ok) {
                const data = await res.json();
                setMessages(data);
            }
        } catch (e) { /* ignore poll error */ }
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
        const res = await fetch(`${API_URL}/api/v1/system/backup`, { method: 'POST' });
        const data = await res.json();
        alert(`Backup saved to: ${data.path}`);
        setShowMenu(false);
    };

    // --- CHAT ---

    const sendMessage = async () => {
        if (!input.trim()) return;
        setLoading(true);

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
            // Revert optimistic? For now keep it so they can copy-paste.
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex h-full bg-[#0f0f13]">
            {/* Left: Chat Area */}
            <div className="flex-1 flex flex-col border-r border-gray-800">
                <div className="h-16 border-b border-gray-800 flex items-center justify-between px-6 bg-[#16161a]">
                    <div className="flex items-center">
                        <BrainCircuit className="w-5 h-5 text-purple-400 mr-2" />
                        <h2 className="font-bold text-gray-200">Supreme Architect</h2>
                        <span className="ml-2 px-2 py-0.5 text-xs bg-gray-800 text-gray-400 rounded border border-gray-700">
                            {systemMode}
                        </span>
                    </div>

                    {/* System Menu */}
                    <div className="flex items-center gap-4">

                        <div className="relative">
                            <button
                                onClick={() => setShowMenu(!showMenu)}
                                className="p-2 hover:bg-gray-800 rounded-lg text-gray-400 transition-colors"
                                title="System Settings"
                            >
                                <RefreshCcw className="w-4 h-4" />
                            </button>

                            {showMenu && (
                                <div className="absolute right-0 top-full mt-2 w-48 bg-[#1a1a20] border border-gray-700 rounded-lg shadow-xl z-50 p-1">
                                    <div className="text-xs font-bold text-gray-500 px-3 py-2 uppercase">Neural Link</div>
                                    <button onClick={switchMode} className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 rounded flex items-center gap-2">
                                        {systemMode === 'LOCAL' ? <Cloud className="w-3 h-3" /> : <Database className="w-3 h-3" />}
                                        Switch to {systemMode === 'LOCAL' ? 'Cloud' : 'Local'}
                                    </button>
                                    <div className="h-px bg-gray-700 my-1 api-separator"></div>
                                    <button onClick={() => triggerSync("PULL")} className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 rounded flex items-center gap-2">
                                        <ArrowDownCircle className="w-3 h-3 text-blue-400" />
                                        Pull from Cloud
                                    </button>
                                    <button onClick={() => triggerSync("PUSH")} className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 rounded flex items-center gap-2">
                                        <ArrowUpCircle className="w-3 h-3 text-green-400" />
                                        Push to Cloud
                                    </button>
                                    <div className="h-px bg-gray-700 my-1"></div>
                                    <button onClick={triggerBackup} className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 rounded flex items-center gap-2">
                                        <Save className="w-3 h-3 text-yellow-500" />
                                        Backup Local DB
                                    </button>
                                </div>
                            )}
                        </div>

                        {/* Status Indicator */}
                        <div className="flex items-center gap-2 text-xs text-gray-500 border-l border-gray-800 pl-4">
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

                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    {messages.map((msg, i) => (
                        <div key={msg.id || i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[80%] p-4 rounded-xl ${msg.role === 'user'
                                ? 'bg-purple-900/20 text-purple-100 border border-purple-500/30'
                                : 'bg-gray-800/50 text-gray-200 border border-gray-700'
                                }`}>
                                <div className="flex items-center gap-2 mb-1 text-xs opacity-50 uppercase tracking-widest font-bold">
                                    {msg.role === 'user' ? <User className="w-3 h-3" /> : <Bot className="w-3 h-3" />}
                                    {msg.role}
                                </div>
                                <div className="whitespace-pre-wrap">{msg.content}</div>
                            </div>
                        </div>
                    ))}
                    {messages.length === 0 && (
                        <div className="text-center text-gray-600 mt-20">
                            No history found. Connection established.
                        </div>
                    )}
                </div>

                <div className="p-4 bg-[#16161a] border-t border-gray-800">
                    <div className="flex gap-2">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                            className="flex-1 bg-[#0f0f13] border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-purple-500"
                            placeholder="Instruct the Supreme Architect..."
                        />
                        <button
                            onClick={sendMessage}
                            disabled={loading}
                            className="bg-purple-600 hover:bg-purple-500 text-white p-2 rounded-lg transition-colors"
                        >
                            <Send className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Right: Roadmap / Tasks */}
            <div className="w-80 flex flex-col bg-[#111115]">
                <div className="h-16 border-b border-gray-800 flex items-center px-6 bg-[#16161a]">
                    <h2 className="font-bold text-gray-200">Active Roadmap</h2>
                </div>
                <div className="flex-1 overflow-y-auto p-4 space-y-3">
                    {tasks.map(task => (
                        <div key={task.id} className="bg-[#1a1a20] p-3 rounded-lg border border-gray-800 flex items-start gap-3 hover:border-purple-500/30 transition-all">
                            {task.status === 'DONE' ? (
                                <CheckCircle2 className="w-5 h-5 text-emerald-500 mt-0.5" />
                            ) : task.status === 'IN_PROGRESS' ? (
                                <div className="w-5 h-5 rounded-full border-2 border-yellow-500 border-t-transparent animate-spin mt-0.5" />
                            ) : (
                                <Circle className="w-5 h-5 text-gray-600 mt-0.5" />
                            )}
                            <div>
                                <div className="text-sm font-medium text-gray-200">{task.title}</div>
                                <div className="text-xs text-gray-500 mt-1 flex items-center gap-1">
                                    <span className="bg-gray-800 px-1 rounded">{task.assigned_agent}</span>
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
                </div>
            </div>
        </div>
    );
}
