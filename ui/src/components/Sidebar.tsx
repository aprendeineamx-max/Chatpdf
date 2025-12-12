import { useEffect, useState } from 'react';
import { MessageSquare, Clock, Plus, ChevronLeft, ChevronRight } from 'lucide-react';
import clsx from 'clsx';
import { motion, AnimatePresence } from 'framer-motion';

interface Session {
    id: string;
    title: string;
    created_at: string;
}

interface SidebarProps {
    currentSessionId: string | null;
    onSelectSession: (id: string) => void;
    onNewChat: () => void;
    isOpen: boolean;
    setIsOpen: (val: boolean) => void;
}

export default function Sidebar({ currentSessionId, onSelectSession, onNewChat, isOpen, setIsOpen }: SidebarProps) {
    const [sessions, setSessions] = useState<Session[]>([]);

    useEffect(() => {
        // Load sessions on mount and keep polling or refresh logic (simplified for now)
        fetchSessions();
    }, [currentSessionId]); // Refresh list if current session changes (e.g. new title)

    const fetchSessions = async () => {
        try {
            const res = await fetch('http://127.0.0.1:8000/api/v1/sessions');
            if (res.ok) {
                const data = await res.json();
                setSessions(data);
            }
        } catch (e) {
            console.error("Failed to load sessions", e);
        }
    };

    return (
        <>
            {/* Toggle Button (Mobile/Desktop) */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="fixed left-4 top-4 z-50 p-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-400 hover:text-white hover:border-cyan-500 transition-all"
            >
                {isOpen ? <ChevronLeft size={20} /> : <ChevronRight size={20} />}
            </button>

            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ x: -300, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        exit={{ x: -300, opacity: 0 }}
                        className="fixed left-0 top-0 h-full w-72 bg-slate-950 border-r border-slate-800 z-40 flex flex-col pt-16 shadow-2xl"
                    >
                        {/* New Chat Button */}
                        <div className="p-4">
                            <button
                                onClick={onNewChat}
                                className="w-full flex items-center gap-2 justify-center p-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white rounded-xl font-medium transition-all shadow-lg hover:shadow-cyan-500/20"
                            >
                                <Plus size={18} />
                                Nuevo Chat
                            </button>
                        </div>

                        {/* Session List */}
                        <div className="flex-1 overflow-y-auto px-2 space-y-1">
                            <div className="px-4 py-2 text-xs font-semibold text-slate-500 uppercase tracking-widest">
                                Historial
                            </div>

                            {sessions.map((session) => (
                                <button
                                    key={session.id}
                                    onClick={() => onSelectSession(session.id)}
                                    className={clsx(
                                        "w-full text-left p-3 rounded-lg flex items-center gap-3 transition-colors text-sm",
                                        currentSessionId === session.id
                                            ? "bg-slate-800 text-cyan-400 border border-slate-700"
                                            : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
                                    )}
                                >
                                    <MessageSquare size={16} className="shrink-0" />
                                    <span className="truncate">{session.title}</span>
                                </button>
                            ))}
                        </div>

                        {/* Footer */}
                        <div className="p-4 border-t border-slate-900 text-[10px] text-slate-600 text-center">
                            Hydra Infinite Memory <br /> Local Storage Active
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
