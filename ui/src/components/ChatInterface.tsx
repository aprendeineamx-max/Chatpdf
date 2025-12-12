import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, FileText, Loader2, BookOpen } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import ControlPanel from './ControlPanel';
import Sidebar from './Sidebar';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    sources?: { page: number; text: string; score: number }[];
}

export default function ChatInterface() {
    const [query, setQuery] = useState('');
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [swarmMode, setSwarmMode] = useState(false);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [isSidebarOpen, setIsSidebarOpen] = useState(true); // Default open

    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleNewChat = () => {
        setSessionId(null);
        setMessages([]);
        setQuery('');
    };

    const handleSelectSession = async (id: string) => {
        setIsLoading(true);
        setSessionId(id);
        try {
            const res = await fetch(`http://127.0.0.1:8000/api/v1/sessions/${id}`);
            const data = await res.json();
            // Map backend messages to UI messages
            const loaded: Message[] = data.map((m: any) => ({
                id: m.id || Math.random().toString(),
                role: m.role,
                content: m.content,
                sources: typeof m.sources === 'string' ? JSON.parse(m.sources) : m.sources
            }));
            setMessages(loaded);
        } catch (e) {
            console.error(e);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSend = async () => {
        if (!query.trim()) return;

        const userMsg: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: query
        };
        setMessages(prev => [...prev, userMsg]);
        setQuery('');
        setIsLoading(true);

        try {
            // NOTE: Using localhost:8000 directly. 
            const response = await fetch('http://127.0.0.1:8000/api/v1/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query_text: userMsg.content,
                    pdf_id: "all",
                    mode: swarmMode ? "swarm" : "standard",
                    session_id: sessionId
                })
            });

            const data = await response.json();

            if (data.session_id) {
                setSessionId(data.session_id);
            }

            const botMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.answer || "Lo siento, no pude entender eso.",
                sources: data.sources
            };

            setMessages(prev => [...prev, botMsg]);
        } catch (error) {
            console.error(error);
            const errorMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: "Error: Could not connect to Cortex API."
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-screen bg-cortex-bg text-cortex-text font-sans selection:bg-cortex-accent selection:text-white">

            <Sidebar
                isOpen={isSidebarOpen}
                setIsOpen={setIsSidebarOpen}
                currentSessionId={sessionId}
                onSelectSession={handleSelectSession}
                onNewChat={handleNewChat}
            />

            <div className={clsx("flex flex-col h-full transition-all duration-300", isSidebarOpen ? "ml-72" : "ml-0")}>
                {/* Header */}
                <header className="p-4 border-b border-cortex-panel flex items-center justify-between bg-cortex-bg/80 backdrop-blur-md sticky top-0 z-30 pl-16">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-500 to-cyan-400 flex items-center justify-center">
                            <FileText className="text-white w-5 h-5" />
                        </div>
                        <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-cyan-300">
                            PDF Cortex
                        </h1>
                    </div>
                    <div className="text-xs text-slate-400 font-mono">
                        System v1.4 (Infinite Memory)
                    </div>
                </header>

                {/* Control Panel */}
                <ControlPanel swarmMode={swarmMode} setSwarmMode={setSwarmMode} />

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-8">
                    <AnimatePresence>
                        {messages.length === 0 && (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="h-full flex flex-col items-center justify-center text-slate-500 gap-4"
                            >
                                <Bot className="w-16 h-16 text-slate-700" />
                                <p>Listo para analizar tus documentos.</p>
                            </motion.div>
                        )}

                        {messages.map((msg) => (
                            <motion.div
                                key={msg.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className={clsx(
                                    "flex gap-4 max-w-4xl mx-auto",
                                    msg.role === 'user' ? "justify-end" : "justify-start"
                                )}
                            >
                                {msg.role === 'assistant' && (
                                    <div className="w-8 h-8 rounded-full bg-cortex-panel flex items-center justify-center shrink-0 border border-slate-700 mt-1">
                                        <Bot className="w-4 h-4 text-cyan-400" />
                                    </div>
                                )}

                                <div className={clsx("flex flex-col gap-2 max-w-[85%]", msg.role === 'user' && "items-end")}>
                                    <div
                                        className={clsx(
                                            "p-4 rounded-2xl shadow-lg prose prose-invert max-w-none text-sm leading-relaxed",
                                            msg.role === 'user'
                                                ? "bg-cortex-accent text-white rounded-br-none"
                                                : "bg-cortex-panel border border-slate-700 rounded-bl-none"
                                        )}
                                    >
                                        {msg.role === 'user' ? (
                                            <p>{msg.content}</p>
                                        ) : (
                                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                {msg.content}
                                            </ReactMarkdown>
                                        )}
                                    </div>

                                    {/* Sources Section */}
                                    {msg.role === 'assistant' && msg.sources && msg.sources.length > 0 && (
                                        <motion.div
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            transition={{ delay: 0.2 }}
                                            className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-1 w-full"
                                        >
                                            <div className="md:col-span-2 flex items-center gap-1 text-xs text-slate-500 uppercase tracking-widest font-semibold mb-1">
                                                <BookOpen className="w-3 h-3" /> Fuentes del Documento
                                            </div>
                                            {msg.sources.map((src, idx) => (
                                                <div key={idx} className="bg-slate-900/50 border border-slate-800 p-3 rounded-lg text-xs text-slate-400 hover:border-slate-700 transition-colors">
                                                    <div className="flex justify-between items-center mb-1">
                                                        <span className="font-medium text-cyan-500">Página {src.page}</span>
                                                        <span className="text-[10px] bg-slate-800 px-1 rounded text-slate-500">{(src.score * 100).toFixed(0)}% Match</span>
                                                    </div>
                                                    <p className="line-clamp-2 italic">"{src.text}"</p>
                                                </div>
                                            ))}
                                        </motion.div>
                                    )}
                                </div>

                                {msg.role === 'user' && (
                                    <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center shrink-0 mt-1">
                                        <User className="w-4 h-4 text-slate-300" />
                                    </div>
                                )}
                            </motion.div>
                        ))}

                        {isLoading && (
                            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-4 max-w-4xl mx-auto justify-start">
                                <div className="w-8 h-8 rounded-full bg-cortex-panel flex items-center justify-center shrink-0 border border-slate-700">
                                    <Bot className="w-4 h-4 text-cyan-400" />
                                </div>
                                <div className="bg-cortex-panel p-4 rounded-2xl rounded-bl-none border border-slate-700 flex items-center gap-2">
                                    <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
                                    <span className="text-sm text-slate-400">Analizando el libro...</span>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                    <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <div className="p-4 border-t border-cortex-panel bg-cortex-bg/95 backdrop-blur">
                    <div className="max-w-4xl mx-auto relative group">
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                            placeholder="Pregunta algo sobre el libro..."
                            className="w-full bg-cortex-panel border border-slate-700 rounded-xl py-4 pl-4 pr-12 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-cortex-accent/50 transition-all font-medium"
                        />
                        <button
                            onClick={handleSend}
                            disabled={!query.trim() || isLoading}
                            className="absolute right-2 top-2 p-2 bg-cortex-accent hover:bg-blue-600 disabled:opacity-50 disabled:hover:bg-cortex-accent rounded-lg transition-colors text-white"
                        >
                            <Send className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
