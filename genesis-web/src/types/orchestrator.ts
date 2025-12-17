// Domain Types

export interface RepoJob {
    id: string;
    name: string;
    path: string;
    status: string;
    error?: string;
}

export interface Message {
    role: 'user' | 'assistant' | 'system';
    content: string;
    id?: string | number;
    created_at?: string;
    sources?: string[];
    model?: string;
}

export interface FileNode {
    name: string;
    path: string;
    type: 'file' | 'dir';
    children?: FileNode[];
}

export interface Task {
    id: string;
    title: string;
    status: 'PENDING' | 'IN_PROGRESS' | 'DONE';
    assigned_agent: string;
}

export interface Session {
    id: string;
    title: string;
    created_at: string;
}
