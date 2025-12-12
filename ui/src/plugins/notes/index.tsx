import { useState, useEffect } from 'react';
import { Plugin } from '../../core/plugins/types';
import { StickyNote, X, Save, Minus } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const NotesWidget = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [content, setContent] = useState('');
    const [isMinimized, setIsMinimized] = useState(false);

    useEffect(() => {
        const saved = localStorage.getItem('cortex_notes_draft');
        if (saved) setContent(saved);

        const toggleHandler = () => setIsOpen(prev => !prev);
        window.addEventListener('CORTEX_TOGGLE_NOTES', toggleHandler);
        return () => window.removeEventListener('CORTEX_TOGGLE_NOTES', toggleHandler);
    }, []);

    const handleSave = () => {
        localStorage.setItem('cortex_notes_draft', content);
    };

    if (!isOpen) return null;

    return (
        <motion.div
            drag={!isMinimized}
            dragMomentum={false}
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1, height: isMinimized ? 'auto' : 'auto' }}
            className="fixed top-20 right-8 z-50 w-72 bg-yellow-50/95 shadow-xl border border-yellow-200/50 rounded-xl overflow-hidden backdrop-blur-sm"
        >
            {/* Header */}
            <div className="bg-yellow-200/80 p-2 flex justify-between items-center cursor-move select-none">
                <div className="flex items-center gap-2 text-yellow-800 font-bold text-xs uppercase tracking-wider">
                    <StickyNote size={14} /> Notas Rápidas
                </div>
                <div className="flex gap-1">
                    <button onClick={() => setIsMinimized(!isMinimized)} className="p-1 hover:bg-yellow-300 rounded text-yellow-800"><Minus size={14} /></button>
                    <button onClick={() => setIsOpen(false)} className="p-1 hover:bg-yellow-400 rounded text-yellow-900"><X size={14} /></button>
                </div>
            </div>

            {/* Content */}
            {!isMinimized && (
                <div className="p-3">
                    <textarea
                        className="w-full h-64 bg-transparent resize-none focus:outline-none text-slate-700 font-mono text-sm leading-relaxed"
                        placeholder="Escribe tus ideas aquí..."
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        onBlur={handleSave}
                    />
                    <div className="flex justify-between items-center mt-2 border-t border-yellow-200/50 pt-2">
                        <span className="text-[10px] text-yellow-600/70">Se guarda localmente</span>
                        <button onClick={handleSave} className="p-1 text-yellow-700 hover:text-yellow-900"><Save size={16} /></button>
                    </div>
                </div>
            )}
        </motion.div>
    );
};

// Toggle Button to be injected into Sidebar
const NotesTrigger = () => {
    return (
        <button
            onClick={() => window.dispatchEvent(new Event('CORTEX_TOGGLE_NOTES'))}
            className="w-full text-left p-3 rounded-lg flex items-center gap-3 text-slate-400 hover:bg-slate-900 hover:text-yellow-400 transition-colors text-sm"
        >
            <StickyNote size={16} className="shrink-0" />
            <span className="truncate">Abrir Notas</span>
        </button>
    );
};

export const NotesPlugin: Plugin = {
    manifest: {
        id: 'cortex.notes',
        name: 'Cortex Notes',
        version: '1.0',
        description: 'Floating Sticky Notes'
    },
    init: (ctx) => {
        ctx.registerSlot("global-overlay", NotesWidget);
        // Inject into Sidebar (We need to update Sidebar to render a slot!! But for now we can rely on ControlPanel or just global overlay)
        // Wait, Sidebar.tsx doesn't have a plugin Slot yet. I should add one.
        // For MVP, I will add a floating trigger or modify Sidebar to render "sidebar-items" slot.
        ctx.registerSlot("sidebar-item", NotesTrigger);
    }
};
