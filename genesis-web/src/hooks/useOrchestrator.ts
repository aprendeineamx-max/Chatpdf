import { useState, useEffect, useRef } from 'react';
import { RepoJob, Message, Task, FileNode, Session } from '../types/orchestrator';

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export function useOrchestrator() {
    // --- State ---
    const [tasks, setTasks] = useState<Task[]>([]);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [isPolling, setIsPolling] = useState(false);

    // Session State
    const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
    const [sessions, setSessions] = useState<Session[]>([]);
    const [showHistory, setShowHistory] = useState(true);

    // [DEFINITIVE FIX] Ref to hold the LATEST session ID for the interval callback
    const sessionIdRef = useRef<string | null>(null);

    // System State
    const [systemMode, setSystemMode] = useState<"LOCAL" | "CLOUD">("LOCAL");
    const [selectedModel, setSelectedModel] = useState("Meta-Llama-3.3-70B-Instruct");
    const [selectedProvider, setSelectedProvider] = useState<string>("sambanova");
    const [ragMode, setRagMode] = useState<string>("injection"); // NEW: "injection" or "semantic"

    // Context / Knowledge State
    const [activeTab, setActiveTab] = useState<'roadmap' | 'knowledge'>('roadmap');
    const [repos, setRepos] = useState<RepoJob[]>([]);

    // File Explorer State
    const [expandedRepo, setExpandedRepo] = useState<string | null>(null);
    const [repoFiles, setRepoFiles] = useState<FileNode[]>([]);
    const [selectedFile, setSelectedFile] = useState<{ name: string, content: string } | null>(null);
    const [isLoadingFiles, setIsLoadingFiles] = useState(false);

    // Ingest State
    const [ingestUrl, setIngestUrl] = useState('');
    const [ingestScope, setIngestScope] = useState<'global' | 'session'>('global');
    const [showIngestModal, setShowIngestModal] = useState(false);

    // Editor State
    const [isEditing, setIsEditing] = useState(false);
    const [editorContent, setEditorContent] = useState("");
    const [isSaving, setIsSaving] = useState(false);
    const [isLoadingContent, setIsLoadingContent] = useState(false);

    // --- Effects ---

    // [DEFINITIVE FIX] Keep ref in sync with state
    useEffect(() => {
        sessionIdRef.current = currentSessionId;
        // Also reload data when session changes
        loadDataWithRef(true);
    }, [currentSessionId]);

    // Polling Effect - runs ONCE, interval uses ref
    useEffect(() => {
        loadSessions();
        loadDataWithRef();

        const interval = setInterval(() => {
            loadDataWithRef(true);
        }, 5000);

        setIsPolling(true);
        return () => clearInterval(interval);
    }, []); // Empty dependency - interval reads from ref

    // Sync Editor with Selected File
    useEffect(() => {
        if (selectedFile) {
            setEditorContent(selectedFile.content);
            setIsEditing(false);
        }
    }, [selectedFile]);

    // --- API Handlers ---

    async function loadSessions() {
        try {
            const res = await fetch(`${API_URL}/api/v1/sessions`);
            if (res.ok) setSessions(await res.json());
        } catch (e) { console.error("Failed to load sessions", e); }
    }

    async function handleNewChat() {
        setMessages([]);
        setCurrentSessionId(null);
        setTasks([]);
        setRepos([]); // [FIX] Clear knowledge panel for new chat
        loadSessions();
    }

    async function handleSelectSession(sessionId: string) {
        setCurrentSessionId(sessionId);
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/api/v1/sessions/${sessionId}`);
            if (res.ok) {
                setMessages(await res.json());
            }
        } catch (e) {
            console.error("Failed to load session history", e);
        } finally {
            setLoading(false);
        }
        if (window.innerWidth < 1024) setShowHistory(false);
    }

    async function handleCloneSession(sessionId: string, e: React.MouseEvent) {
        e.stopPropagation();
        try {
            const res = await fetch(`${API_URL}/api/v1/sessions/${sessionId}/clone`, { method: 'POST' });
            if (res.ok) {
                const data = await res.json();
                await loadSessions();
                handleSelectSession(data.session_id);
            }
        } catch (e) { console.error("Failed to clone session", e); }
    }

    async function handleDeleteSession(sessionId: string, e: React.MouseEvent) {
        e.stopPropagation();
        if (!confirm("Are you sure you want to delete this chat?")) return;
        try {
            await fetch(`${API_URL}/api/v1/sessions/${sessionId}`, { method: 'DELETE' });
            if (currentSessionId === sessionId) handleNewChat();
            loadSessions();
        } catch (e) { console.error("Failed to delete session", e); }
    }

    // [DEFINITIVE FIX] This function reads from the REF, not state
    // Guaranteed to always use the latest session ID
    async function loadDataWithRef(silent = false) {
        if (!silent) setLoading(true);
        const targetSessionId = sessionIdRef.current; // Read from REF!

        try {
            const [tasksRes, reposRes] = await Promise.all([
                fetch(`${API_URL}/api/v1/orchestrator/tasks?session_id=${targetSessionId || ''}`),
                fetch(`${API_URL}/api/v1/ingest/list?session_id=${targetSessionId || ''}`)
            ]);

            if (tasksRes.ok) setTasks(await tasksRes.json());
            if (reposRes.ok) setRepos(await reposRes.json());
        } catch (error) {
            console.error('Connection Error:', error);
        } finally {
            if (!silent) setLoading(false);
        }
    }

    // Keep old loadData for other usages that might pass explicit ID
    async function loadData(silent = false, overrideSessionId: string | null = null) {
        if (!silent) setLoading(true);
        const targetSessionId = overrideSessionId !== null ? overrideSessionId : currentSessionId;

        try {
            const [tasksRes, reposRes] = await Promise.all([
                fetch(`${API_URL}/api/v1/orchestrator/tasks?session_id=${targetSessionId || ''}`),
                fetch(`${API_URL}/api/v1/ingest/list?session_id=${targetSessionId || ''}`)
            ]);

            if (tasksRes.ok) setTasks(await tasksRes.json());
            if (reposRes.ok) setRepos(await reposRes.json());
        } catch (error) {
            console.error('Connection Error:', error);
        } finally {
            if (!silent) setLoading(false);
        }
    }

    const [activePdfUrl, setActivePdfUrl] = useState<string | null>(null);
    const [pdfPage, setPdfPage] = useState<number>(1);

    // ... (existing state) ...

    async function sendMessage() {
        if (!input.trim()) return;

        const userMsg: Message = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        const currentInput = input;
        setInput('');
        setLoading(true);

        try {
            const res = await fetch(`${API_URL}/api/v1/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query_text: currentInput,
                    pdf_id: "all",
                    mode: systemMode === 'CLOUD' ? 'swarm' : 'standard',
                    session_id: currentSessionId,
                    model: selectedModel,
                    provider: selectedProvider,
                    repo_context: expandedRepo,
                    rag_mode: ragMode
                }),
            });

            const data = await res.json();

            if (data.session_id && data.session_id !== currentSessionId) {
                setCurrentSessionId(data.session_id);
                loadSessions();
            }

            const finalProvider = data.metadata?.provider || selectedProvider;
            const finalModel = data.metadata?.model || selectedModel;
            const ragModeUsed = data.rag_mode_used || ragMode;

            // [NEW] PDF SYNC LOGIC
            // Look for priority context marker in the answer or sources to determine page
            // Or look for specific "page X" mentions in the AI answer if structured
            // Simple RegEx on the answer for now: "PÁGINA (\d+)" inside context blocks or explicit AI mention
            // Better: The backend injects "⚠️ CONTEXTO PRIORITARIO: PÁGINA {requested_page} ⚠️" into context
            // But frontend receives the ANSWER. The answer might mention "En la página 79...".
            // Let's use a regex on the answer to auto-scroll if AI explicitly cites a page number.
            const pageMatch = data.answer?.match(/página\s+(\d+)/i);
            if (pageMatch && pageMatch[1]) {
                setPdfPage(parseInt(pageMatch[1]));
            }

            const ragIndicator = ragModeUsed === "semantic" ? " 🔍" :
                ragModeUsed === "injection (fallback)" ? " 💉⚡" : " 💉";

            const botMsg: Message = {
                role: 'assistant',
                content: data.answer || "I processed that but have no specific answer.",
                sources: data.sources,
                model: finalModel + (finalProvider && finalProvider !== "unknown" ? ` @ ${finalProvider}` : "") + ragIndicator
            };
            setMessages(prev => [...prev, botMsg]);

            if (data.tasks) loadData(true);

        } catch (error: any) {
            console.error("Chat Error:", error);
            const msg = error.message || "Unknown Error";
            setMessages(prev => [...prev, { role: 'system', content: `Error: ${msg}` }]);
        } finally { setLoading(false); }
    }


    // --- File Logic ---
    async function fetchFiles(repoName: string, path: string) {
        setIsLoadingFiles(true);
        try {
            const cleanName = repoName.replace("REPO: ", "");
            const res = await fetch(`${API_URL}/api/v1/ingest/files?repo_name=${cleanName}&path=${encodeURIComponent(path)}`);
            if (res.ok) setRepoFiles(await res.json());
        } catch (e) { console.error("File Fetch Error:", e); }
        finally { setIsLoadingFiles(false); }
    }

    async function fetchContent(repoName: string, path: string) {
        const cleanName = repoName.replace("REPO: ", "");
        setIsLoadingContent(true);
        // Open modal immediately with empty content to show loading state
        setSelectedFile({ name: path.split('/').pop() || 'File', content: "" });

        try {
            const res = await fetch(`${API_URL}/api/v1/ingest/content?repo_name=${cleanName}&path=${encodeURIComponent(path)}`);
            if (res.ok) {
                const data = await res.json();
                // Update with actual content
                setSelectedFile(prev => prev ? { ...prev, content: data.content } : null);
            }
        } catch (e) {
            console.error(e);
            // Close modal on error or show error state? For now, close and alert.
            setSelectedFile(null);
            // In a better world, we'd use a toast.
            // Using alert to not break existing pattern, but minimizing "blocking".
        } finally {
            setIsLoadingContent(false);
        }
    }

    async function saveCurrentFile(content: string) {
        if (!selectedFile || !expandedRepo) return;
        try {
            const cleanName = expandedRepo.replace("REPO: ", "");
            const res = await fetch(`${API_URL}/api/v1/ingest/content`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    repo_name: cleanName,
                    path: selectedFile.name,
                    content: content
                })
            });
            if (res.ok) {
                setSelectedFile(prev => prev ? ({ ...prev, content: content }) : null);
            } else { throw new Error("Save returned " + res.status); }
        } catch (e) { alert("Failed to save file."); console.error(e); throw e; }
    }

    async function handleIngestSubmit() {
        const url = ingestUrl.trim();
        if (!url) return;
        setShowIngestModal(false);
        setIngestUrl('');
        setActiveTab('knowledge');
        setMessages(prev => [...prev, { role: 'system', content: `👁️ INGESTION INITIATED: ${url}` }]);

        try {
            const res = await fetch(`${API_URL}/api/v1/ingest/repo`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url, scope: ingestScope, session_id: currentSessionId })
            });

            if (res.ok) {
                const data = await res.json();
                setMessages(prev => [...prev, { role: 'system', content: `✅ INGESTION QUEUED.` }]);

                // [FIX] Adopt session ID if we were in a new/null session
                let effectiveSessionId = currentSessionId;
                if (data.session_id && data.session_id !== currentSessionId) {
                    setCurrentSessionId(data.session_id);
                    effectiveSessionId = data.session_id;
                    loadSessions(); // Refresh session list
                }

                loadData(true, effectiveSessionId);
            } else {
                throw new Error("Ingestion failed");
            }
        } catch (e: any) {
            setMessages(prev => [...prev, { role: 'system', content: `❌ INGESTION FAILED: ${e.message}` }]);
        }
    }

    async function handleIngestPDF(pageOffset: number = 0, enableOcr: boolean = false) {
        const url = ingestUrl.trim();
        if (!url) return;
        setShowIngestModal(false);
        setIngestUrl('');
        setActiveTab('knowledge');
        const ocrInfo = enableOcr ? ' (OCR enabled)' : '';
        const offsetInfo = pageOffset !== 0 ? ` (offset: ${pageOffset})` : '';
        setMessages(prev => [...prev, { role: 'system', content: `📄 PDF INGESTION INITIATED: ${url}${ocrInfo}${offsetInfo}` }]);

        try {
            const res = await fetch(`${API_URL}/api/v1/ingest/pdf`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url,
                    scope: ingestScope,
                    session_id: currentSessionId,
                    rag_mode: ragMode,
                    page_offset: pageOffset,   // NEW: Pass page offset
                    enable_ocr: enableOcr      // NEW: Pass OCR flag
                })
            });

            if (res.ok) {
                const data = await res.json();
                setMessages(prev => [...prev, { role: 'system', content: `✅ PDF INGESTION QUEUED.` }]);

                // Adopt session ID if needed (same pattern as repos)
                let effectiveSessionId = currentSessionId;
                if (data.session_id && data.session_id !== currentSessionId) {
                    setCurrentSessionId(data.session_id);
                    effectiveSessionId = data.session_id;
                    loadSessions();
                }

                // [NEW] Set Active PDF
                if (data.file_url) {
                    setActivePdfUrl(data.file_url);
                }

                loadData(true, effectiveSessionId);
            } else {
                throw new Error("PDF Ingestion failed");
            }
        } catch (e: any) {
            setMessages(prev => [...prev, { role: 'system', content: `❌ PDF INGESTION FAILED: ${e.message}` }]);
        }
    }

    return {
        // State
        tasks, messages, input, setInput, loading, isPolling,
        currentSessionId, sessions, showHistory, setShowHistory,
        systemMode, setSystemMode, selectedModel, setSelectedModel, selectedProvider, setSelectedProvider,
        ragMode, setRagMode, // NEW: RAG Mode
        activeTab, setActiveTab, repos,
        expandedRepo, setExpandedRepo, repoFiles, selectedFile, setSelectedFile, isLoadingFiles,
        ingestUrl, setIngestUrl, ingestScope, setIngestScope, showIngestModal, setShowIngestModal,

        // [NEW] PDF State
        activePdfUrl, setActivePdfUrl, pdfPage, setPdfPage,

        // Editor State
        isEditing, setIsEditing, editorContent, setEditorContent, isSaving,

        // Actions
        sendMessage, handleNewChat, handleSelectSession, handleCloneSession, handleDeleteSession,
        fetchFiles, fetchContent, saveCurrentFile, handleIngestSubmit, handleIngestPDF,
        isLoadingContent // Exported
    };
}
