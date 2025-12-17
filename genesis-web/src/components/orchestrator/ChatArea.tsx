import { useEffect, useRef } from 'react';
import { User, Bot, Brain, Send } from 'lucide-react';

interface Message {
    role: 'user' | 'assistant' | 'system';
    content: string;
    id?: string | number;
    created_at?: string;
    sources?: string[];
    model?: string;
}

interface ChatAreaProps {
    messages: Message[];
    input: string;
    setInput: (val: string) => void;
    sendMessage: () => void;
    loading: boolean;
    activeTab: 'roadmap' | 'knowledge';
}

export function ChatArea({
    messages,
    input,
    setInput,
    sendMessage,
    loading,
    activeTab
}: ChatAreaProps) {
    // Internal Auto-Scroll
    const messagesEndRef = useRef<HTMLDivElement>(null);
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    return (
        <div className={`flex-1 flex flex-col min-w-0 border-r border-gray-800 ${activeTab === 'roadmap' ? 'flex' : 'hidden md:flex'}`}>
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
                                    {msg.role === 'user' ? "USER" : (msg.model || "IA")}
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
    );
}
