import React from 'react';
import { FileCode, Save, RefreshCcw, X } from 'lucide-react';

interface FileEditorModalProps {
    selectedFile: { name: string, content: string } | null;
    editorContent: string;
    isEditing: boolean;
    isSaving: boolean;
    setEditorContent: (content: string) => void;
    setIsEditing: (isEditing: boolean) => void;
    setSelectedFile: (file: { name: string, content: string } | null) => void;
    saveCurrentFile: () => void;
}

export function FileEditorModal({
    selectedFile,
    editorContent,
    isEditing,
    isSaving,
    setEditorContent,
    setIsEditing,
    setSelectedFile,
    saveCurrentFile
}: FileEditorModalProps) {
    if (!selectedFile) return null;

    return (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4">
            <div className="bg-[#101014] border border-gray-700 rounded-lg shadow-2xl w-full max-w-4xl h-[85vh] flex flex-col">
                {/* Toolbar */}
                <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700 bg-[#16161a]">
                    <div className="flex items-center gap-2">
                        <FileCode className="w-4 h-4 text-blue-400" />
                        <span className="font-mono text-sm font-bold">{selectedFile.name}</span>
                        {isEditing && <span className="text-xs text-yellow-500 italic">(Unsaved Changes)</span>}
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={saveCurrentFile}
                            disabled={!isEditing || isSaving}
                            className={`flex items-center gap-1 px-3 py-1.5 rounded text-xs font-bold transition-colors ${!isEditing ? 'text-gray-500 cursor-not-allowed' : 'bg-green-600 hover:bg-green-500 text-white'}`}
                        >
                            {isSaving ? <RefreshCcw className="w-3 h-3 animate-spin" /> : <Save className="w-3 h-3" />}
                            Save
                        </button>
                        <button
                            onClick={() => setSelectedFile(null)}
                            className="p-1.5 hover:bg-gray-700 rounded text-gray-400"
                        >
                            <X className="w-4 h-4" />
                        </button>
                    </div>
                </div>
                {/* Editor */}
                <div className="flex-1 relative">
                    <textarea
                        className="w-full h-full bg-[#0a0a0c] text-gray-300 font-mono text-xs p-4 focus:outline-none resize-none leading-relaxed"
                        value={editorContent}
                        onChange={(e) => {
                            setEditorContent(e.target.value);
                            setIsEditing(true);
                            if (selectedFile) {
                                setSelectedFile({ ...selectedFile, content: e.target.value });
                            }
                        }}
                    />
                </div>
            </div>
        </div>
    );
}
