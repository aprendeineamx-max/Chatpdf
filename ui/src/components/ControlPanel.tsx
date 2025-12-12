import { Zap, Shield, Layers } from 'lucide-react';
import clsx from 'clsx';
import { motion } from 'framer-motion';

interface ControlPanelProps {
    swarmMode: boolean;
    setSwarmMode: (value: boolean) => void;
}

export default function ControlPanel({ swarmMode, setSwarmMode }: ControlPanelProps) {
    return (
        <div className="bg-slate-900 border-b border-slate-800 p-2 flex justify-center sticky top-[65px] z-20 backdrop-blur-sm bg-opacity-80">
            <div className="bg-slate-950 rounded-full border border-slate-800 p-1 flex gap-1 shadow-xl">
                {/* Standard Mode Button */}
                <button
                    onClick={() => setSwarmMode(false)}
                    className={clsx(
                        "flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-medium transition-all duration-300",
                        !swarmMode
                            ? "bg-slate-800 text-cyan-400 border border-slate-700 shadow-inner"
                            : "text-slate-500 hover:text-slate-300 hover:bg-slate-900"
                    )}
                >
                    <Shield className="w-3 h-3" />
                    <span>Hydra Standard</span>
                </button>

                {/* Swarm Mode Button */}
                <button
                    onClick={() => setSwarmMode(true)}
                    className={clsx(
                        "flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-medium transition-all duration-300 relative overflow-hidden",
                        swarmMode
                            ? "bg-purple-900/30 text-purple-400 border border-purple-500/50 shadow-[0_0_15px_rgba(168,85,247,0.3)]"
                            : "text-slate-500 hover:text-slate-300 hover:bg-slate-900"
                    )}
                >
                    <Zap className={clsx("w-3 h-3", swarmMode && "fill-purple-400 animate-pulse")} />
                    <span>Hydra Swarm</span>

                    {swarmMode && (
                        <motion.div
                            layoutId="active-glow"
                            className="absolute inset-0 bg-purple-500/10"
                        />
                    )}
                </button>

                {/* Info Text */}
                <div className="flex items-center px-3 border-l border-slate-800 ml-1">
                    <Layers className="w-3 h-3 text-slate-600 mr-2" />
                    <span className="text-[10px] text-slate-500">
                        {swarmMode ? "3 Parallel Keys Active" : "1 Key (Rotational)"}
                    </span>
                </div>
            </div>
        </div>
    );
}
