import React from 'react';
import { RefreshCcw, MessageSquare, Copy, Trash2, Layout } from 'lucide-react';

interface SidebarHistoryProps {
    showHistory: boolean;
    sessions: { id: string, title: string, created_at: string }[];
    currentSessionId: string | null;
    handleNewChat: () => void;
    handleSelectSession: (id: string) => void;
    handleCloneSession: (id: string, e: React.MouseEvent) => void;
    handleDeleteSession: (id: string, e: React.MouseEvent) => void;
}

export function SidebarHistory({
    showHistory,
    sessions,
    currentSessionId,
    handleNewChat,
    handleSelectSession,
    handleCloneSession,
    handleDeleteSession
}: SidebarHistoryProps) {

    return (
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
    );
}
