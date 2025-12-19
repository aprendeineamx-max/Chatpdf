// Components
import { OrchestratorHeader } from './orchestrator/OrchestratorHeader';
import { SidebarHistory } from './orchestrator/SidebarHistory';
import { ChatArea } from './orchestrator/ChatArea';
import { KnowledgePanel } from './orchestrator/KnowledgePanel';
import { IngestModal } from './orchestrator/IngestModal';
import { PDFViewer } from './orchestrator/PDFViewer';
import { X } from 'lucide-react';
import { FileEditorModal } from './orchestrator/FileEditorModal';

// Hooks
import { useOrchestrator } from '../hooks/useOrchestrator';

export function Orchestrator() {
    const {
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

        // Actions (Editor)
        isEditing, editorContent, isSaving, setEditorContent, setIsEditing, isLoadingContent,

        handleNewChat, handleSelectSession, handleCloneSession, handleDeleteSession,
        sendMessage, fetchFiles, fetchContent, saveCurrentFile, handleIngestSubmit, handleIngestPDF
    } = useOrchestrator();

    return (
        <div className="flex flex-col h-full bg-[#111115] text-white relative overflow-hidden">

            <OrchestratorHeader
                showHistory={showHistory}
                setShowHistory={setShowHistory}
                isPolling={isPolling}
                handleNewChat={handleNewChat}
                selectedProvider={selectedProvider}
                setSelectedProvider={setSelectedProvider}
                selectedModel={selectedModel}
                setSelectedModel={setSelectedModel}
                systemMode={systemMode}
                setSystemMode={setSystemMode}
                ragMode={ragMode}
                setRagMode={setRagMode}
            />

            <div className="flex-1 flex overflow-hidden">
                <SidebarHistory
                    showHistory={showHistory}
                    sessions={sessions}
                    currentSessionId={currentSessionId}
                    handleNewChat={handleNewChat}
                    handleSelectSession={handleSelectSession}
                    handleCloneSession={handleCloneSession}
                    handleDeleteSession={handleDeleteSession}
                />

                <ChatArea
                    messages={messages}
                    input={input}
                    setInput={setInput}
                    sendMessage={sendMessage}
                    loading={loading}
                    activeTab={activeTab}
                />

                {activePdfUrl ? (
                    <div className="w-1/2 flex flex-col border-l border-gray-800">
                        {/* Close/Toggle Button Layer could go here */}
                        <div className="flex-1 overflow-hidden relative">
                            <button
                                onClick={() => setActivePdfUrl(null)}
                                className="absolute top-4 right-4 z-50 bg-red-600 hover:bg-red-700 text-white p-2 rounded-full shadow-lg transition-transform hover:scale-110"
                                title="Close PDF View"
                            >
                                <X className="w-5 h-5" />
                            </button>
                            <PDFViewer
                                pdfUrl={activePdfUrl}
                                currentPage={pdfPage}
                                onPageChange={setPdfPage}
                            />
                        </div>
                    </div>
                ) : (
                    <KnowledgePanel
                        activeTab={activeTab}
                        setActiveTab={setActiveTab}
                        tasks={tasks}
                        repos={repos}
                        expandedRepo={expandedRepo}
                        setExpandedRepo={setExpandedRepo}
                        repoFiles={repoFiles}
                        isLoadingFiles={isLoadingFiles}
                        fetchFiles={fetchFiles}
                        fetchContent={fetchContent}
                        setShowIngestModal={setShowIngestModal}
                    />
                )}
            </div>

            <IngestModal
                showIngestModal={showIngestModal}
                setShowIngestModal={setShowIngestModal}
                ingestUrl={ingestUrl}
                setIngestUrl={setIngestUrl}
                ingestScope={ingestScope}
                setIngestScope={setIngestScope}
                handleIngestSubmit={handleIngestSubmit}
                handleIngestPDF={handleIngestPDF}
            />

            <FileEditorModal
                selectedFile={selectedFile}
                editorContent={editorContent}
                isEditing={isEditing}
                isSaving={isSaving}
                isLoading={isLoadingContent}
                setEditorContent={setEditorContent}
                setIsEditing={setIsEditing}
                setSelectedFile={setSelectedFile}
                saveCurrentFile={() => saveCurrentFile(editorContent)}
            />
        </div>
    );
}
