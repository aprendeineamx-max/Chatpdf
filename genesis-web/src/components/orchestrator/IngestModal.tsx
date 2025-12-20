import React, { useState } from 'react';
import { Github, FileText, Settings, Upload } from 'lucide-react';

interface IngestModalProps {
    showIngestModal: boolean;
    setShowIngestModal: (show: boolean) => void;
    ingestUrl: string;
    setIngestUrl: (url: string) => void;
    ingestScope: 'global' | 'session';
    setIngestScope: (scope: 'global' | 'session') => void;
    handleIngestSubmit: () => void;
    handleIngestPDF?: (pageOffset?: number, enableOcr?: boolean) => void;
    handleIngestUpload?: (file: File, pageOffset?: number, enableOcr?: boolean) => void; // NEW: Upload handler
}

type SourceType = 'repo' | 'pdf' | 'upload';

export function IngestModal({
    showIngestModal,
    setShowIngestModal,
    ingestUrl,
    setIngestUrl,
    ingestScope,
    setIngestScope,
    handleIngestSubmit,
    handleIngestPDF,
    handleIngestUpload
}: IngestModalProps) {
    const [sourceType, setSourceType] = useState<SourceType>('repo');
    const [pageOffset, setPageOffset] = useState<number>(0);
    const [enableOcr, setEnableOcr] = useState<boolean>(false);
    const [showAdvanced, setShowAdvanced] = useState<boolean>(false);
    const [selectedFile, setSelectedFile] = useState<File | null>(null); // NEW: selected file state

    if (!showIngestModal) return null;

    const handleSubmit = () => {
        if (sourceType === 'pdf' && handleIngestPDF) {
            handleIngestPDF(pageOffset, enableOcr);
        } else if (sourceType === 'upload' && handleIngestUpload && selectedFile) {
            handleIngestUpload(selectedFile, pageOffset, enableOcr);
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
                        className={`flex-1 flex items-center justify-center gap-2 py-2 px-2 rounded-lg border transition-all ${sourceType === 'repo'
                            ? 'bg-purple-900/40 border-purple-500 text-purple-300'
                            : 'bg-[#0f0f13] border-gray-700 text-gray-400 hover:border-gray-600'
                            }`}
                    >
                        <Github size={16} />
                        <span className="font-medium text-sm">Repo</span>
                    </button>
                    <button
                        onClick={() => setSourceType('pdf')}
                        className={`flex-1 flex items-center justify-center gap-2 py-2 px-2 rounded-lg border transition-all ${sourceType === 'pdf'
                            ? 'bg-red-900/40 border-red-500 text-red-300'
                            : 'bg-[#0f0f13] border-gray-700 text-gray-400 hover:border-gray-600'
                            }`}
                    >
                        <FileText size={16} />
                        <span className="font-medium text-sm">PDF URL</span>
                    </button>
                    <button
                        onClick={() => setSourceType('upload')}
                        className={`flex-1 flex items-center justify-center gap-2 py-2 px-2 rounded-lg border transition-all ${sourceType === 'upload'
                            ? 'bg-blue-900/40 border-blue-500 text-blue-300'
                            : 'bg-[#0f0f13] border-gray-700 text-gray-400 hover:border-gray-600'
                            }`}
                    >
                        <Upload size={16} />
                        <span className="font-medium text-sm">Upload</span>
                    </button>
                </div>

                {/* Input Fields based on Source Type */}
                {sourceType === 'upload' ? (
                    <div className="mb-4">
                        <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 flex flex-col items-center justify-center bg-[#0f0f13] hover:border-gray-500 transition-colors relative">
                            <input
                                type="file"
                                accept=".pdf"
                                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                onChange={(e) => {
                                    if (e.target.files && e.target.files[0]) {
                                        setSelectedFile(e.target.files[0]);
                                    }
                                }}
                            />
                            {selectedFile ? (
                                <div className="text-center">
                                    <FileText className="w-8 h-8 text-blue-400 mx-auto mb-2" />
                                    <p className="text-blue-300 font-medium">{selectedFile.name}</p>
                                    <p className="text-gray-500 text-xs">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                                </div>
                            ) : (
                                <div className="text-center text-gray-400">
                                    <Upload className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                    <p className="font-medium">Drop PDF here or click to browse</p>
                                    <p className="text-xs text-gray-500 mt-1">Max 500MB</p>
                                </div>
                            )}
                        </div>
                    </div>
                ) : (
                    <div className="mb-2">
                        <input
                            type="text"
                            className="w-full bg-[#0f0f13] border border-gray-600 rounded px-4 py-2 text-white mb-2"
                            placeholder={sourceType === 'repo' ? "https://github.com/user/repo" : "https://example.com/document.pdf"}
                            value={ingestUrl}
                            onChange={e => setIngestUrl(e.target.value)}
                        />
                        <p className="text-xs text-gray-500 mb-4">
                            {sourceType === 'repo'
                                ? "Paste a public GitHub repository URL"
                                : "Paste a direct PDF link, Google Drive, or Dropbox URL"}
                        </p>
                    </div>
                )}


                {/* NEW: Advanced Options for PDF (Offset + OCR) - For both URL and Upload */}
                {(sourceType === 'pdf' || sourceType === 'upload') && (
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
                        disabled={sourceType === 'upload' && !selectedFile}
                        className={`px-4 py-2 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed ${sourceType === 'repo' ? 'bg-purple-600 hover:bg-purple-700' :
                            sourceType === 'pdf' ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'}`}
                    >
                        {sourceType === 'upload' ? 'Upload PDF' : 'Start Ingestion'}
                    </button>
                </div>
            </div>
        </div>
    );
}
