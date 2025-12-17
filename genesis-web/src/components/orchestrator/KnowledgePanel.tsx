import React from 'react';
import { RepoJob, Task, FileNode } from '../../types/orchestrator';
import { RoadmapList } from './RoadmapList';
import { RepoBrowser } from './RepoBrowser';

interface KnowledgePanelProps {
    activeTab: 'roadmap' | 'knowledge';
    setActiveTab: (tab: 'roadmap' | 'knowledge') => void;
    tasks: Task[];
    repos: RepoJob[];
    expandedRepo: string | null;
    setExpandedRepo: (repo: string | null) => void;
    repoFiles: FileNode[];
    isLoadingFiles: boolean;
    fetchFiles: (repoName: string, path: string) => void;
    fetchContent: (repoName: string, path: string) => void;
    setShowIngestModal: (show: boolean) => void;
}

export function KnowledgePanel({
    activeTab,
    setActiveTab,
    tasks,
    repos,
    expandedRepo,
    setExpandedRepo,
    repoFiles,
    isLoadingFiles,
    fetchFiles,
    fetchContent,
    setShowIngestModal
}: KnowledgePanelProps) {
    return (
        <div className="w-80 border-l border-gray-800 flex flex-col bg-[#111115]">
            <div className="flex border-b border-gray-800">
                <button onClick={() => setActiveTab('roadmap')} className={`flex-1 py-3 text-xs font-bold ${activeTab === 'roadmap' ? 'text-purple-400 border-b-2 border-purple-500' : 'text-gray-500'}`}>TASKS</button>
                <button onClick={() => setActiveTab('knowledge')} className={`flex-1 py-3 text-xs font-bold ${activeTab === 'knowledge' ? 'text-purple-400 border-b-2 border-purple-500' : 'text-gray-500'}`}>KNOWLEDGE</button>
            </div>

            <div className="flex-1 overflow-y-auto p-4">
                {activeTab === 'roadmap' ? (
                    <RoadmapList tasks={tasks} />
                ) : (
                    <RepoBrowser
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
        </div>
    );
}
