import React, { useState } from 'react';
import { Github, FileText, Settings } from 'lucide-react';

interface IngestModalProps {
    showIngestModal: boolean;
    setShowIngestModal: (show: boolean) => void;
    ingestUrl: string;
    setIngestUrl: (url: string) => void;
    ingestScope: 'global' | 'session';
    setIngestScope: (scope: 'global' | 'session') => void;
    handleIngestSubmit: () => void;
    handleIngestPDF?: (pageOffset?: number, enableOcr?: boolean) => void; // Updated handler
}

type SourceType = 'repo' | 'pdf';

export function IngestModal({
    showIngestModal,
    setShowIngestModal,
    ingestUrl,
    setIngestUrl,
    ingestScope,
    setIngestScope,
    handleIngestSubmit,
    handleIngestPDF
}: IngestModalProps) {
    const [sourceType, setSourceType] = useState<SourceType>('repo');
    const [pageOffset, setPageOffset] = useState<number>(0);    // NEW: Page offset
    const [enableOcr, setEnableOcr] = useState<boolean>(false);  // NEW: OCR toggle
    const [showAdvanced, setShowAdvanced] = useState<boolean>(false); // NEW: Advanced options

    if (!showIngestModal) return null;

    const handleSubmit = () => {
        if (sourceType === 'pdf' && handleIngestPDF) {
            handleIngestPDF(pageOffset, enableOcr);
        } else {
            handleIngestSubmit();
        }
    };

    return (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
            <div className="bg-[#1a1a20] border border-gray-700 rounded-xl shadow-2xl w-full max-w-lg p-6">
                <h3 className="font-bold text-gray-200 mb-4">Ingest Knowledge Source</h3>

                {/* Source Type Tabs */}
                <div className="flex gap-2 mb-4">
                    <button
                        onClick={() => setSourceType('repo')}
                        className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-lg border transition-all ${sourceType === 'repo'
                            ? 'bg-purple-900/40 border-purple-500 text-purple-300'
                            : 'bg-[#0f0f13] border-gray-700 text-gray-400 hover:border-gray-600'
                            }`}
                    >
                        <Github size={18} />
                        <span className="font-medium">GitHub Repo</span>
                    </button>
                    <button
                        onClick={() => setSourceType('pdf')}
                        className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-lg border transition-all ${sourceType === 'pdf'
                            ? 'bg-red-900/40 border-red-500 text-red-300'
                            : 'bg-[#0f0f13] border-gray-700 text-gray-400 hover:border-gray-600'
                            }`}
                    >
                        <FileText size={18} />
                        <span className="font-medium">PDF URL</span>
                    </button>
                </div>

                {/* Input Field */}
                <input
                    type="text"
                    className="w-full bg-[#0f0f13] border border-gray-600 rounded px-4 py-2 text-white mb-2"
                    placeholder={sourceType === 'repo' ? "https://github.com/user/repo" : "https://example.com/document.pdf"}
                    value={ingestUrl}
                    onChange={e => setIngestUrl(e.target.value)}
                />

                {/* Hint Text */}
                <p className="text-xs text-gray-500 mb-4">
                    {sourceType === 'repo'
                        ? "Paste a public GitHub repository URL"
                        : "Paste a direct PDF link, Google Drive, or Dropbox URL"}
                </p>

                {/* NEW: Advanced Options for PDF (Offset + OCR) */}
                {sourceType === 'pdf' && (
                    <div className="mb-4">
                        <button
                            onClick={() => setShowAdvanced(!showAdvanced)}
                            className="flex items-center gap-2 text-sm text-gray-400 hover:text-gray-300 mb-2"
                        >
                            <Settings size={14} />
                            <span>{showAdvanced ? 'Hide' : 'Show'} Advanced Options</span>
                        </button>

                        {showAdvanced && (
                            <div className="bg-[#0f0f13] border border-gray-700 rounded-lg p-3 space-y-3">
                                {/* Page Offset */}
                                <div className="flex items-center gap-3">
                                    <label className="text-sm text-gray-400 w-24">Page Offset:</label>
                                    <input
                                        type="number"
                                        className="w-20 bg-[#1a1a20] border border-gray-600 rounded px-2 py-1 text-white text-center"
                                        value={pageOffset}
                                        onChange={e => setPageOffset(parseInt(e.target.value) || 0)}
                                    />
                                    <span className="text-xs text-gray-500">
                                        Adjust if page numbers don't match
                                    </span>
                                </div>

                                {/* OCR Toggle */}
                                <label className="flex items-center gap-3 cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={enableOcr}
                                        onChange={e => setEnableOcr(e.target.checked)}
                                        className="w-4 h-4 accent-purple-500"
                                    />
                                    <span className="text-sm text-gray-400">🔍 Enable OCR</span>
                                    <span className="text-xs text-gray-500">
                                        (for scanned PDFs)
                                    </span>
                                </label>
                            </div>
                        )}
                    </div>
                )}

                {/* Scope Selector */}
                <div className="flex gap-4 mb-6">
                    <label className={`flex-1 cursor-pointer p-3 rounded border ${ingestScope === 'global' ? 'bg-purple-900/40 border-purple-500' : 'bg-[#0f0f13] border-gray-700 hover:border-gray-600'}`}>
                        <input type="radio" className="hidden" name="scope" checked={ingestScope === 'global'} onChange={() => setIngestScope('global')} />
                        <div className="font-bold text-sm text-gray-200 mb-1">🌍 Global Knowledge</div>
                        <div className="text-[10px] text-gray-400">Available to ALL chats and agents.</div>
                    </label>

                    <label className={`flex-1 cursor-pointer p-3 rounded border ${ingestScope === 'session' ? 'bg-blue-900/40 border-blue-500' : 'bg-[#0f0f13] border-gray-700 hover:border-gray-600'}`}>
                        <input type="radio" className="hidden" name="scope" checked={ingestScope === 'session'} onChange={() => setIngestScope('session')} />
                        <div className="font-bold text-sm text-gray-200 mb-1">🔒 Chat Specific</div>
                        <div className="text-[10px] text-gray-400">Only visible in THIS conversation.</div>
                    </label>
                </div>

                <div className="flex justify-end gap-2">
                    <button onClick={() => setShowIngestModal(false)} className="px-4 py-2 text-gray-400">Cancel</button>
                    <button
                        onClick={handleSubmit}
                        className={`px-4 py-2 text-white rounded ${sourceType === 'repo' ? 'bg-purple-600 hover:bg-purple-700' : 'bg-red-600 hover:bg-red-700'}`}
                    >
                        Start Ingestion
                    </button>
                </div>
            </div>
        </div>
    );
}
