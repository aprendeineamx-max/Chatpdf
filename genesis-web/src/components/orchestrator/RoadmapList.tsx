import React from 'react';
import { Bot } from 'lucide-react';
import { Task } from '../../types/orchestrator';

interface RoadmapListProps {
    tasks: Task[];
}

export function RoadmapList({ tasks }: RoadmapListProps) {
    return (
        <div className="space-y-3">
            {tasks.length === 0 && <div className="text-gray-600 text-xs text-center py-4">No active tasks in this plan.</div>}
            {tasks.map(task => (
                <div key={task.id} className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
                    <div className="flex justify-between items-start mb-1">
                        <span className="font-medium text-sm text-gray-200">{task.title}</span>
                        <span className={`text-[10px] px-1.5 py-0.5 rounded ${task.status === 'DONE' ? 'bg-green-900/50 text-green-400' : 'bg-yellow-900/50 text-yellow-400'}`}>{task.status}</span>
                    </div>
                    <div className="text-xs text-gray-500 flex items-center gap-1">
                        <Bot className="w-3 h-3" /> {task.assigned_agent}
                    </div>
                </div>
            ))}
        </div>
    );
}
