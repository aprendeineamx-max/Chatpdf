
import { useEffect, useState } from 'react';
import { supabase } from './lib/supabase';
import { AtomicContext, AtomicArtifact } from './types';
import { Folder, FileText, Cpu, Activity, Clock, Database, Users } from 'lucide-react';
import { SkillGalaxy } from './components/SkillGalaxy';
import { SelfHealingGalaxy } from './components/SelfHealingGalaxy';
import { NeuralCouncil } from './components/NeuralCouncil';
import { Orchestrator } from './components/Orchestrator';

function App() {
    const [view, setView] = useState<'timeline' | 'skills' | 'self-healing' | 'hive' | 'orchestrator'>('timeline');
    const [contexts, setContexts] = useState<AtomicContext[]>([]);
    const [selectedContext, setSelectedContext] = useState<AtomicContext | null>(null);
    const [artifacts, setArtifacts] = useState<AtomicArtifact[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchContexts();

        const channel = supabase
            .channel('schema-db-changes')
            .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'atomic_contexts' }, (payload) => {
                console.log('New Context:', payload);
                fetchContexts();
            })
            .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'atomic_artifacts' }, () => {
                if (selectedContext) fetchArtifacts(selectedContext.id);
            })
            .subscribe();

        return () => { supabase.removeChannel(channel); };
    }, [selectedContext]);

    async function fetchContexts() {
        const { data, error } = await supabase
            .from('atomic_contexts')
            .select('*')
            .order('timestamp', { ascending: false });

        if (error) console.error('Error fetching contexts:', error);
        else setContexts(data || []);
        setLoading(false);
    }

    async function fetchArtifacts(contextId: string) {
        const { data, error } = await supabase
            .from('atomic_artifacts')
            .select('*')
            .eq('context_id', contextId);

        if (error) console.error('Error fetching artifacts:', error);
        else setArtifacts(data || []);
    }

    const handleSelectContext = (ctx: AtomicContext) => {
        setSelectedContext(ctx);
        fetchArtifacts(ctx.id);
    };

    return (
        <div className="flex h-screen bg-[#0f0f13] text-gray-100 font-sans overflow-hidden">
            {/* Sidebar / Timeline */}
            <div className="w-72 border-r border-gray-800 flex flex-col">
                <div className="p-4 border-b border-gray-800 bg-[#16161a]">
                    <h1 className="text-lg font-bold flex items-center gap-2 bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                        <Cpu className="w-5 h-5 text-cyan-400" />
                        GENESIS ARCHITECT
                    </h1>
                    <div className="flex gap-2 mt-4">
                        <button
                            onClick={() => setView('timeline')}
                            className={`flex-1 text-xs font-bold py-1.5 rounded transition-all ${view === 'timeline' ? 'bg-cyan-900 text-cyan-200' : 'bg-[#202026] text-gray-500 hover:text-gray-300'}`}
                        >
                            TIMELINE
                        </button>
                        <button
                            onClick={() => setView('skills')}
                            className={`flex-1 text-xs font-bold py-1.5 rounded transition-all ${view === 'skills' ? 'bg-purple-900 text-purple-200' : 'bg-[#202026] text-gray-500 hover:text-gray-300'}`}
                        >
                            SKILLS
                        </button>
                        <button
                            onClick={() => setView('self-healing')}
                            className={`flex-1 text-xs font-bold py-1.5 rounded transition-all ${view === 'self-healing' ? 'bg-emerald-900 text-emerald-200' : 'bg-[#202026] text-gray-500 hover:text-gray-300'}`}
                        >
                            HEALING
                        </button>
                        <button
                            onClick={() => setView('hive')}
                            className={`flex-1 text-xs font-bold py-1.5 rounded transition-all ${view === 'hive' ? 'bg-amber-900 text-amber-200' : 'bg-[#202026] text-gray-500 hover:text-gray-300'}`}
                        >
                            HIVE
                        </button>
                        <button
                            onClick={() => setView('orchestrator')}
                            className={`flex-1 text-xs font-bold py-1.5 rounded transition-all ${view === 'orchestrator' ? 'bg-indigo-900 text-indigo-200' : 'bg-[#202026] text-gray-500 hover:text-gray-300'}`}
                        >
                            ARCH
                        </button>
                    </div>
                </div>

                {view === 'timeline' && (
                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-4">Neural Timeline</h2>
                        {loading ? (
                            <div className="text-center text-gray-500 py-10">Syncing Liquid Memory...</div>
                        ) : contexts.map((ctx) => (
                            <div
                                key={ctx.id}
                                onClick={() => handleSelectContext(ctx)}
                                className={`group p-4 rounded-xl border transition-all cursor-pointer relative overflow-hidden ${selectedContext?.id === ctx.id
                                    ? 'bg-blue-900/20 border-blue-500/50 shadow-[0_0_15px_rgba(59,130,246,0.2)]'
                                    : 'bg-[#1a1a20] border-gray-800 hover:border-gray-600 hover:bg-[#202026]'
                                    }`}
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <span className="text-xs font-mono text-cyan-500 bg-cyan-950/30 px-2 py-0.5 rounded border border-cyan-800/50">
                                        ID: {ctx.batch_id}
                                    </span>
                                    <Clock className="w-3 h-3 text-gray-500" />
                                </div>
                                <div className="text-sm font-medium text-gray-300 group-hover:text-white transition-colors">
                                    {ctx.timestamp.replace('_', ' ').split('.')[0]}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col bg-[#0f0f13]">
                {view === 'skills' ? (
                    <SkillGalaxy />
                ) : view === 'self-healing' ? (
                    <SelfHealingGalaxy />
                ) : view === 'hive' ? (
                    <NeuralCouncil />
                ) : view === 'orchestrator' ? (
                    <Orchestrator />
                ) : (
                    selectedContext ? (
                        <div className="flex-1 flex flex-col h-full">
                            {/* Header */}
                            <div className="h-14 border-b border-gray-800 flex items-center justify-between px-6 bg-[#131316]">
                                <div>
                                    <h2 className="text-base font-medium text-white flex items-center gap-2">
                                        <Database className="w-4 h-4 text-purple-400" />
                                        Atomic Context Viewer
                                    </h2>
                                    <div className="text-xs text-gray-500 font-mono mt-1">
                                        {selectedContext.folder_name}
                                    </div>
                                </div>
                                <div className="flex gap-4">
                                    <div className="text-center">
                                        <div className="text-lg font-bold text-white">{artifacts.length}</div>
                                        <div className="text-[10px] text-gray-500 uppercase">Artifacts</div>
                                    </div>
                                </div>
                            </div>

                            {/* Grid */}
                            <div className="flex-1 overflow-y-auto p-6">
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                                    {artifacts.map((art) => (
                                        <div key={art.id} className="bg-[#1a1a20] border border-gray-800 rounded-lg hover:border-gray-600 hover:bg-[#202026] transition-all group overflow-hidden">
                                            {/* Preview Area (Mock) */}
                                            <div className="aspect-video bg-black/40 flex items-center justify-center border-b border-gray-800">
                                                {art.filename.match(/\.(png|jpg|webp)$/i) ? (
                                                    <div className="text-xs text-gray-500 flex flex-col items-center gap-2">
                                                        <Activity className="w-5 h-5 text-gray-600" />
                                                        <span>Preview Unavailable</span>
                                                    </div>
                                                ) : (
                                                    <div className="flex items-center justify-center h-full">
                                                        <FileText className="w-8 h-8 text-gray-700 group-hover:text-gray-500 transition-colors" />
                                                    </div>
                                                )}
                                            </div>

                                            <div className="p-3">
                                                <div className="flex items-center gap-2 mb-1">
                                                    {art.filename.endsWith('.md') ? <FileText className="w-3.5 h-3.5 text-blue-400" /> :
                                                        art.filename.endsWith('.py') ? <Cpu className="w-3.5 h-3.5 text-yellow-400" /> :
                                                            <Folder className="w-3.5 h-3.5 text-gray-400" />}
                                                    <span className="text-sm font-medium text-gray-200 truncate" title={art.filename}>
                                                        {art.filename}
                                                    </span>
                                                </div>
                                                <div className="flex justify-between items-center text-[10px] text-gray-500 mt-2">
                                                    <span className="font-mono bg-gray-800 px-1.5 py-0.5 rounded">{art.file_type}</span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="flex-1 flex items-center justify-center text-gray-500 flex-col gap-4">
                            <Activity className="w-12 h-12 text-gray-800 animate-pulse" />
                            <p className="text-sm">Select a Neural Atom to inspect its cognitive artifacts.</p>
                        </div>
                    )
                )}
            </div>
        </div>
    );
}

export default App;
