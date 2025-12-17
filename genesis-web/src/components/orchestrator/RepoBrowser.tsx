import React from 'react';
import { Cloud, ArrowDown, ArrowRight, Database, RefreshCcw, Folder, FileCode } from 'lucide-react';
import { RepoJob, FileNode } from '../../types/orchestrator';

interface RepoBrowserProps {
    repos: RepoJob[];
    expandedRepo: string | null;
    setExpandedRepo: (repo: string | null) => void;
    repoFiles: FileNode[];
    isLoadingFiles: boolean;
    fetchFiles: (repoName: string, path: string) => void;
    fetchContent: (repoName: string, path: string) => void;
    setShowIngestModal: (show: boolean) => void;
}

export function RepoBrowser({
    repos,
    expandedRepo,
    setExpandedRepo,
    repoFiles,
    isLoadingFiles,
    fetchFiles,
    fetchContent,
    setShowIngestModal
}: RepoBrowserProps) {
    return (
        <div>
            <div className="mb-4">
                <button onClick={() => setShowIngestModal(true)} className="w-full py-2 bg-gray-800 hover:bg-gray-700 border border-gray-600 rounded flex items-center justify-center gap-2 text-xs font-bold text-gray-300">
                    <Cloud className="w-3 h-3" /> Ingest Repo
                </button>
            </div>
            <div className="space-y-2">
                {repos.map(repo => (
                    <div key={repo.id} className="border border-gray-700 rounded-lg overflow-hidden">
                        <div
                            className="p-2 bg-gray-800/50 flex items-center gap-2 cursor-pointer hover:bg-gray-800"
                            onClick={() => {
                                if (expandedRepo === repo.name) {
                                    setExpandedRepo(null);
                                } else {
                                    setExpandedRepo(repo.name);
                                    fetchFiles(repo.name, "");
                                }
                            }}
                        >
                            {expandedRepo === repo.name ? <ArrowDown className="w-3 h-3 text-purple-400" /> : <ArrowRight className="w-3 h-3 text-gray-500" />}
                            <Database className="w-3 h-3 text-blue-400" />
                            <span className="text-xs font-bold truncate flex-1">{repo.name.replace("REPO: ", "")}</span>
                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    fetchFiles(repo.name, "");
                                }}
                                className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
                                title="Refresh Files"
                            >
                                <RefreshCcw className="w-3 h-3" />
                            </button>
                        </div>
                        {expandedRepo === repo.name && (
                            <div className="p-2 bg-[#0a0a0c] border-t border-gray-700">
                                {isLoadingFiles ? (
                                    <div className="text-xs text-gray-500 animate-pulse">Loading file tree...</div>
                                ) : (
                                    <div className="space-y-1 pl-2">
                                        {repoFiles.map((file, idx) => (
                                            <div
                                                key={idx}
                                                className="flex items-center gap-2 text-xs text-gray-400 hover:text-white cursor-pointer"
                                                onClick={() => {
                                                    if (file.type === 'file') fetchContent(repo.name, file.path);
                                                    else fetchFiles(repo.name, file.path);
                                                }}
                                            >
                                                {file.type === 'dir' ? <Folder className="w-3 h-3 text-yellow-600" /> : <FileCode className="w-3 h-3 text-blue-500" />}
                                                {file.name}
                                            </div>
                                        ))}
                                        {repoFiles.length === 0 && <div className="text-xs text-gray-600 italic">Empty directory</div>}
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}
