import { useState, useEffect } from 'react';
import { Plugin } from '../../core/plugins/types';
import { X, ZoomIn, ZoomOut, Maximize } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// --- The Component ---
const ImageViewerModal = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [imgSrc, setImgSrc] = useState<string>("");
    const [scale, setScale] = useState(1);

    useEffect(() => {
        const handler = (e: any) => {
            setImgSrc(e.detail.src);
            setIsOpen(true);
            setScale(1);
        };
        // Listen to Global Event Bus (registry.events or window)
        // For simplicity in MVP, we adhere to window event or registry event
        window.addEventListener('CORTEX_OPEN_IMAGE', handler);
        return () => window.removeEventListener('CORTEX_OPEN_IMAGE', handler);
    }, []);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[200] flex items-center justify-center pointer-events-auto bg-slate-950/80 backdrop-blur-md">
            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="relative max-w-6xl max-h-[90vh] p-2 bg-slate-900/50 rounded-2xl border border-slate-700 shadow-2xl overflow-hidden flex flex-col"
            >
                {/* Toolbar */}
                <div className="absolute top-4 right-4 z-10 flex gap-2">
                    <button onClick={() => setScale(s => s + 0.2)} className="p-2 bg-slate-800/80 rounded-full hover:bg-slate-700 text-white backdrop-blur"><ZoomIn size={20} /></button>
                    <button onClick={() => setScale(s => Math.max(0.5, s - 0.2))} className="p-2 bg-slate-800/80 rounded-full hover:bg-slate-700 text-white backdrop-blur"><ZoomOut size={20} /></button>
                    <button onClick={() => setIsOpen(false)} className="p-2 bg-red-500/80 rounded-full hover:bg-red-600 text-white backdrop-blur transition-colors"><X size={20} /></button>
                </div>

                {/* Image Area */}
                <div className="flex-1 overflow-auto flex items-center justify-center p-8 cursor-move">
                    <motion.img
                        src={imgSrc}
                        alt="Preview"
                        animate={{ scale }}
                        className="max-w-full max-h-[85vh] object-contain rounded-lg shadow-lg"
                        drag
                        dragConstraints={{ left: -500, right: 500, top: -500, bottom: 500 }}
                    />
                </div>

                <div className="absolute bottom-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-slate-900/60 rounded-full text-xs text-slate-400 backdrop-blur border border-slate-800">
                    Cortex Vision v1.0 • Native Viewer
                </div>
            </motion.div>
        </div>
    );
};

// --- The Plugin Definition ---
export const ImageViewerPlugin: Plugin = {
    manifest: {
        id: 'cortex.image-viewer',
        name: 'Cortex Vision',
        version: '1.0',
        description: 'Native Glassmorphism Image Viewer'
    },
    init: (ctx) => {
        // Register to the global overlay slot so it's always available
        ctx.registerSlot("global-overlay", ImageViewerModal);

        // Hijack global image clicks (Optional but requested "Native" feel)
        document.addEventListener('click', (e: any) => {
            if (e.target.tagName === 'IMG' && e.target.closest('.prose')) {
                // Only hijack images inside the chat content (prose)
                e.preventDefault();
                e.stopPropagation();
                window.dispatchEvent(new CustomEvent('CORTEX_OPEN_IMAGE', { detail: { src: e.target.src } }));
            }
        });
    }
};
