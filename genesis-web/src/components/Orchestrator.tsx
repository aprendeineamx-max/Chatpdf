
import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { Send, CheckCircle2, Circle, Bot, User, BrainCircuit } from 'lucide-react';

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

    useEffect(() => {
        fetchTasks();
        fetchHistory();

        // Real-time Check
        const taskSub = supabase.channel('orch-tasks')
            .on('postgres_changes', { event: '*', schema: 'public', table: 'orchestrator_tasks' }, fetchTasks)
            .subscribe();

        const chatSub = supabase.channel('orch-chat')
            .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'chat_messages' },
                (payload) => {
                    setMessages(prev => [...prev, payload.new as Message]);
                })
            .subscribe();

        return () => {
            supabase.removeChannel(taskSub);
            supabase.removeChannel(chatSub);
        }
    }, []);

    async function fetchTasks() {
        const { data } = await supabase.from('orchestrator_tasks').select('*').order('created_at', { ascending: true });
        if (data) setTasks(data);
    }

    async function fetchHistory() {
        // Fetch last 50 messages from a "Orchestrator" session (we need to filter, but for now just all recent)
        // Ideally we filter by session_id, but let's assume one main session for now or just fetch all
        const { data } = await supabase.from('chat_messages').select('*').order('created_at', { ascending: true }).limit(50);
        if (data) setMessages(data);
    }

    const sendMessage = async () => {
        if (!input.trim()) return;
        setLoading(true);

        const userMsg = { role: 'user', content: input };

        // Optimistic update
        // setMessages(prev => [...prev, { ...userMsg, id: 'temp', created_at: new Date().toISOString() } as Message]);

        // 1. Save User Message
        const { error } = await supabase.from('chat_messages').insert(userMsg);

        if (error) {
            console.error("Chat Error:", error);
            alert(`Failed to send: ${error.message} (Likely RLS Permissions)`);
            setLoading(false);
            return;
        }

        // 2. Clear Input
        setInput('');

        // TODO: Backend Trigger (Orchestrator Engine)
        // For now, we manually insert a dummy response via Supabase if no backend is listening? 
        // Or wait for the backend poller.

        setLoading(false);
    };

    return (
        <div className="flex h-full bg-[#0f0f13]">
            {/* Left: Chat Area */}
            <div className="flex-1 flex flex-col border-r border-gray-800">
                <div className="h-16 border-b border-gray-800 flex items-center px-6 bg-[#16161a]">
                    <BrainCircuit className="w-5 h-5 text-purple-400 mr-2" />
                    <h2 className="font-bold text-gray-200">Supreme Architect Chat</h2>
                </div>

                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    {messages.map((msg, i) => (
                        <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
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
                            No history found. Start planning the future.
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
                            Roadmap empty. Discuss with Architect to generate tasks.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
