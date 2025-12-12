
import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';
import { GenesisOptimization } from '../types';
import { ShieldCheck, AlertTriangle, CheckCircle, XCircle, Code, Play } from 'lucide-react';

export function SelfHealingGalaxy() {
    const [optimizations, setOptimizations] = useState<GenesisOptimization[]>([]);

    useEffect(() => {
        fetchOptimizations();

        // Subscribe to new proposals
        const channel = supabase
            .channel('schema-db-changes-optim')
            .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'genesis_optimizations' }, (payload) => {
                console.log('New Optimization Proposal:', payload);
                fetchOptimizations();
            })
            .subscribe();

        return () => { supabase.removeChannel(channel); };
    }, []);

    async function fetchOptimizations() {
        const { data } = await supabase
            .from('genesis_optimizations')
            .select('*')
            .order('created_at', { ascending: false });
        if (data) setOptimizations(data);
    }

    return (
        <div className="flex-1 bg-[#0f0f13] p-8 overflow-y-auto">
            <h2 className="text-2xl font-bold bg-gradient-to-r from-emerald-400 to-teal-500 bg-clip-text text-transparent mb-6 flex items-center gap-2">
                <ShieldCheck className="w-8 h-8 text-emerald-400" />
                Autopoietic Singularity: Self-Healing
            </h2>

            <div className="grid grid-cols-1 gap-6">
                {optimizations.length === 0 ? (
                    <div className="text-gray-500 text-center py-20 border border-gray-800 rounded-xl border-dashed">
                        <ShieldCheck className="w-16 h-16 mx-auto mb-4 opacity-20" />
                        <p>System Nominal. No Anomalies Detected.</p>
                        <p className="text-xs mt-2">Genesis Loop is monitoring...</p>
                    </div>
                ) : (
                    optimizations.map((opt) => (
                        <div key={opt.id} className="bg-[#1a1a20] border border-gray-800 rounded-xl overflow-hidden hover:border-emerald-500/50 transition-all">
                            <div className="p-4 border-b border-gray-800 flex justify-between items-start">
                                <div className="flex items-center gap-3">
                                    <div className="bg-red-900/20 p-2 rounded-lg">
                                        <AlertTriangle className="w-5 h-5 text-red-400" />
                                    </div>
                                    <div>
                                        <h3 className="font-mono text-sm text-gray-300">{opt.target_artifact}</h3>
                                        <p className="text-xs text-red-300 mt-0.5">{opt.issue_detected}</p>
                                    </div>
                                </div>
                                <div className={`px-2 py-1 rounded text-xs font-bold ${opt.status === 'PENDING' ? 'bg-yellow-900/30 text-yellow-500 border border-yellow-700/50' :
                                        opt.status === 'APPLIED' ? 'bg-emerald-900/30 text-emerald-500 border border-emerald-700/50' :
                                            'bg-red-900/30 text-red-500'
                                    }`}>
                                    {opt.status}
                                </div>
                            </div>

                            <div className="bg-black/50 p-4 font-mono text-xs overflow-x-auto">
                                <div className="flex items-center gap-2 text-gray-500 mb-2">
                                    <Code className="w-3 h-3" />
                                    <span>Proposed Fix:</span>
                                </div>
                                <pre className="text-gray-300">
                                    {opt.proposed_fix.split('\n').map((line, i) => (
                                        <div key={i} className={`${line.startsWith('+') ? 'text-green-400 bg-green-900/10' : line.startsWith('-') ? 'text-red-400 bg-red-900/10' : ''}`}>
                                            {line}
                                        </div>
                                    ))}
                                </pre>
                            </div>

                            {opt.status === 'PENDING' && (
                                <div className="p-3 bg-[#131316] flex justify-end gap-3">
                                    <button className="flex items-center gap-2 px-3 py-1.5 rounded bg-red-900/20 text-red-400 text-xs hover:bg-red-900/40 transition-colors">
                                        <XCircle className="w-4 h-4" /> Reject
                                    </button>
                                    <button className="flex items-center gap-2 px-3 py-1.5 rounded bg-emerald-600 text-white text-xs hover:bg-emerald-500 transition-colors shadow-[0_0_10px_rgba(16,185,129,0.3)]">
                                        <Play className="w-4 h-4" /> Apply Fix
                                    </button>
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
