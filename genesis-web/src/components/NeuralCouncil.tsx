
import { useState } from 'react';
import { HiveMessage } from '../types';
import { Users, Send, Bot, Terminal, Shield } from 'lucide-react';

export function NeuralCouncil() {
    const [topic, setTopic] = useState('');
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [messages, setMessages] = useState<HiveMessage[]>([]);
    const [isDebating, setIsDebating] = useState(false);

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    async function startCouncil() {
        if (!topic.trim()) return;
        setIsDebating(true);
        setMessages([]);

        try {
            // 1. Start Session
            const res = await fetch(`${API_URL}/api/hive/council`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic })
            });
            const data = await res.json();
            setSessionId(data.session_id);

            // 2. Poll for initial user message
            pollMessages(data.session_id);

            // 3. Start Polling Loop (Mock Stream)
            let pollCount = 0;
            const interval = setInterval(async () => {
                pollCount++;
                await pollMessages(data.session_id);
                if (pollCount > 5) {
                    clearInterval(interval);
                    setIsDebating(false);
                }
            }, 2000);

        } catch (e) {
            console.error(e);
            setIsDebating(false);
        }
    }

    async function pollMessages(sid: string) {
        const res = await fetch(`${API_URL}/api/hive/council/${sid}/poll`);
        const data = await res.json();
        setMessages(prev => {
            // Simple dedup based on ID
            const existingIds = new Set(prev.map(m => m.id));
            const newMsgs = data.messages.filter((m: HiveMessage) => !existingIds.has(m.id));
            if (newMsgs.length > 0) return [...prev, ...newMsgs];
            return prev;
        });
    }

    const getAgentIcon = (name: string) => {
        switch (name) {
            case 'Architect': return <Bot className="w-5 h-5 text-blue-400" />;
            case 'Coder': return <Terminal className="w-5 h-5 text-green-400" />;
            case 'QA': return <Shield className="w-5 h-5 text-red-400" />;
            default: return <Users className="w-5 h-5 text-gray-400" />;
        }
    };

    const getAgentColor = (name: string) => {
        switch (name) {
            case 'Architect': return 'border-blue-500/30 bg-blue-900/10 text-blue-200';
            case 'Coder': return 'border-green-500/30 bg-green-900/10 text-green-200';
            case 'QA': return 'border-red-500/30 bg-red-900/10 text-red-200';
            default: return 'border-gray-700 bg-gray-800 text-gray-300';
        }
    }

    return (
        <div className="flex-1 flex flex-col bg-[#0f0f13] h-full overflow-hidden">

            {/* Header */}
            <div className="p-6 border-b border-gray-800 bg-[#16161a] flex justify-between items-center">
                <h2 className="text-xl font-bold bg-gradient-to-r from-amber-200 to-yellow-500 bg-clip-text text-transparent flex items-center gap-2">
                    <Users className="w-6 h-6 text-amber-400" />
                    Hive Mind: Neural Council
                </h2>
                <div className="text-xs font-mono text-gray-500">
                    <span className="text-blue-400">Architect</span> • <span className="text-green-400">Coder</span> • <span className="text-red-400">QA</span>
                </div>
            </div>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.length === 0 && !isDebating ? (
                    <div className="flex flex-col items-center justify-center h-full text-gray-600 opacity-50">
                        <Users className="w-16 h-16 mb-4" />
                        <p>The Council is waiting for a topic.</p>
                    </div>
                ) : (
                    messages.map((msg) => (
                        <div key={msg.id} className={`flex gap-4 ${msg.agent_name === 'USER' ? 'flex-row-reverse' : ''}`}>
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center bg-[#202026] border border-gray-700 shrink-0`}>
                                {getAgentIcon(msg.agent_name)}
                            </div>
                            <div className={`max-w-[80%] rounded-xl p-4 border ${getAgentColor(msg.agent_name)}`}>
                                <div className="text-xs font-bold opacity-50 mb-1">{msg.agent_name}</div>
                                <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
                            </div>
                        </div>
                    ))
                )}
                {isDebating && (
                    <div className="flex items-center gap-2 text-gray-500 text-xs animate-pulse p-4">
                        <Bot className="w-4 h-4" />
                        The Council is deliberating...
                    </div>
                )}
            </div>

            {/* Input */}
            <div className="p-4 border-t border-gray-800 bg-[#131316]">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        placeholder="Propose a topic for the Council (e.g., 'Refactor the login system')"
                        className="flex-1 bg-[#0f0f13] border border-gray-700 rounded-lg px-4 py-2 text-gray-200 focus:outline-none focus:border-amber-500 transition-colors"
                        onKeyDown={(e) => e.key === 'Enter' && startCouncil()}
                    />
                    <button
                        onClick={startCouncil}
                        disabled={isDebating}
                        className="bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white px-4 py-2 rounded-lg font-bold flex items-center gap-2 transition-all">
                        <Send className="w-4 h-4" />
                        Summon
                    </button>
                </div>
            </div>
        </div>
    );
}
