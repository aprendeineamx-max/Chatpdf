import { useState, useEffect } from 'react';
import { Plugin } from '../../core/plugins/types';
import { Calculator as CalcIcon, X, Minus, Delete } from 'lucide-react';
import { motion } from 'framer-motion';

const CalculatorWidget = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [display, setDisplay] = useState('0');
    const [isMinimized, setIsMinimized] = useState(false);

    // Listen for toggle event
    useEffect(() => {
        const handler = () => setIsOpen(prev => !prev);
        window.addEventListener('CORTEX_TOGGLE_CALCULATOR', handler);
        return () => window.removeEventListener('CORTEX_TOGGLE_CALCULATOR', handler);
    }, []);

    const handleBtn = (val: string) => {
        if (val === 'C') {
            setDisplay('0');
        } else if (val === '=') {
            try {
                // Safe eval alternative usually preferred, but for simple calc eval is okay-ish in client side sandbox, 
                // strictly limiting chars for safety is better.
                // Using Function constructor for slightly better safety than direct eval? No, same.
                // Let's just use strict regex validation.
                if (/^[0-9+\-*/.() ]+$/.test(display)) {
                    // eslint-disable-next-line
                    setDisplay(String(eval(display)).slice(0, 10));
                }
            } catch {
                setDisplay('Error');
            }
        } else {
            setDisplay(prev => prev === '0' ? val : prev + val);
        }
    };

    if (!isOpen) return null;

    return (
        <motion.div
            drag={!isMinimized}
            dragMomentum={false}
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1, height: isMinimized ? 'auto' : 'auto' }}
            className="fixed bottom-20 left-20 z-50 w-64 bg-slate-900 shadow-2xl border border-slate-700 rounded-2xl overflow-hidden backdrop-blur-md"
        >
            {/* Header */}
            <div className="bg-slate-800 p-2 flex justify-between items-center cursor-move select-none">
                <div className="flex items-center gap-2 text-cyan-400 font-bold text-xs uppercase tracking-wider">
                    <CalcIcon size={14} /> Calculator Pro
                </div>
                <div className="flex gap-1">
                    <button onClick={() => setIsMinimized(!isMinimized)} className="p-1 hover:bg-slate-700 rounded text-slate-400"><Minus size={14} /></button>
                    <button onClick={() => setIsOpen(false)} className="p-1 hover:bg-red-500/20 hover:text-red-400 rounded text-slate-400"><X size={14} /></button>
                </div>
            </div>

            {/* Content */}
            {!isMinimized && (
                <div className="p-4">
                    <div className="bg-slate-950 p-3 rounded-lg mb-3 text-right text-2xl font-mono text-cyan-50 shadow-inner">
                        {display}
                    </div>
                    <div className="grid grid-cols-4 gap-2">
                        {['7', '8', '9', '/', '4', '5', '6', '*', '1', '2', '3', '-', 'C', '0', '=', '+'].map(btn => (
                            <button
                                key={btn}
                                onClick={() => handleBtn(btn)}
                                className={`p-3 rounded-lg font-bold transition-all ${btn === '=' ? 'bg-cyan-600 text-white hover:bg-cyan-500' :
                                    btn === 'C' ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30' :
                                        ['/', '*', '-', '+'].includes(btn) ? 'bg-slate-700 text-cyan-400 hover:bg-slate-600' :
                                            'bg-slate-800 text-slate-200 hover:bg-slate-700'
                                    }`}
                            >
                                {btn}
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </motion.div>
    );
};

const CalculatorTrigger = () => {
    return (
        <button
            onClick={() => window.dispatchEvent(new Event('CORTEX_TOGGLE_CALCULATOR'))}
            className="w-full text-left p-3 rounded-lg flex items-center gap-3 text-slate-400 hover:bg-slate-900 hover:text-cyan-400 transition-colors text-sm"
        >
            <CalcIcon size={16} className="shrink-0" />
            <span className="truncate">Calculadora</span>
        </button>
    );
};

export const CalculatorPlugin: Plugin = {
    manifest: {
        id: 'cortex.calculator',
        name: 'Calculator Pro',
        version: '1.0',
        description: 'Floating Calculator'
    },
    init: (ctx) => {
        ctx.registerSlot("global-overlay", CalculatorWidget);
        ctx.registerSlot("sidebar-item", CalculatorTrigger);
    }
};
