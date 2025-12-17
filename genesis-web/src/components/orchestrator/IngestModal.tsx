import React from 'react';

interface IngestModalProps {
    showIngestModal: boolean;
    setShowIngestModal: (show: boolean) => void;
    ingestUrl: string;
    setIngestUrl: (url: string) => void;
    ingestScope: 'global' | 'session';
    setIngestScope: (scope: 'global' | 'session') => void;
    handleIngestSubmit: () => void;
}

export function IngestModal({
    showIngestModal,
    setShowIngestModal,
    ingestUrl,
    setIngestUrl,
    ingestScope,
    setIngestScope,
    handleIngestSubmit
}: IngestModalProps) {
    if (!showIngestModal) return null;

    return (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
            <div className="bg-[#1a1a20] border border-gray-700 rounded-xl shadow-2xl w-full max-w-lg p-6">
                <h3 className="font-bold text-gray-200 mb-4">Ingest Repository</h3>
                <input
                    type="text"
                    className="w-full bg-[#0f0f13] border border-gray-600 rounded px-4 py-2 text-white mb-4"
                    placeholder="https://github.com/..."
                    value={ingestUrl}
                    onChange={e => setIngestUrl(e.target.value)}
                />

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
                    <button onClick={handleIngestSubmit} className="px-4 py-2 bg-purple-600 text-white rounded">Start</button>
                </div>
            </div>
        </div>
    );
}
