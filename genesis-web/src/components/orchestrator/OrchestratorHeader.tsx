import React from 'react';
import { Layout, BrainCircuit, Wifi, WifiOff, RefreshCcw, ArrowDown } from 'lucide-react';

interface OrchestratorHeaderProps {
    showHistory: boolean;
    setShowHistory: (show: boolean) => void;
    isPolling: boolean;
    handleNewChat: () => void;
    selectedProvider: string;
    setSelectedProvider: (provider: string) => void;
    selectedModel: string;
    setSelectedModel: (model: string) => void;
    systemMode: "LOCAL" | "CLOUD";
    setSystemMode: (mode: "LOCAL" | "CLOUD") => void;
    // NEW: RAG Mode
    ragMode: string;
    setRagMode: (mode: string) => void;
}

export function OrchestratorHeader({
    showHistory,
    setShowHistory,
    isPolling,
    handleNewChat,
    selectedProvider,
    setSelectedProvider,
    selectedModel,
    setSelectedModel,
    systemMode,
    setSystemMode,
    ragMode,
    setRagMode
}: OrchestratorHeaderProps) {
    return (
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

                {/* Provider Selector */}
                <div className="relative group">
                    <select
                        value={selectedProvider}
                        onChange={(e) => setSelectedProvider(e.target.value)}
                        className="bg-[#0a0a0c] border border-gray-700 text-xs rounded px-2 py-1 outline-none text-gray-300 hover:border-indigo-500 transition-colors cursor-pointer appearance-none pr-6"
                    >
                        <option value="sambanova">🚀 Sambanova (Auto)</option>
                        <option value="sambanova_primary">🚀 Sambanova (Key 1)</option>
                        <option value="sambanova_secondary">🚀 Sambanova (Key 2)</option>
                        <option value="groq">🏎️ Groq (Llama)</option>
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

                {/* NEW: RAG Mode Selector */}
                <div className="relative group">
                    <select
                        value={ragMode}
                        onChange={(e) => setRagMode(e.target.value)}
                        className="bg-[#0a0a0c] border border-gray-700 text-xs rounded px-2 py-1 outline-none text-gray-300 hover:border-purple-500 transition-colors cursor-pointer appearance-none pr-6"
                        title="RAG Mode: How PDF content is retrieved"
                    >
                        <option value="injection">💉 Injection</option>
                        <option value="semantic">🔍 Semantic RAG</option>
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
    );
}
