import { useState, useEffect } from 'react';
import { Plugin } from '../../core/plugins/types';
import { Folder, FileText, CheckCircle, Smartphone, Cloud, X as CloseIcon } from 'lucide-react';
import { motion } from 'framer-motion';

const DriveSelectorModal = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [step, setStep] = useState<'auth' | 'picker' | 'ingest'>('auth');
    const [selectedFiles, setSelectedFiles] = useState<string[]>([]);

    // Listen for toggle
    useEffect(() => {
        const handler = () => { setIsOpen(true); setStep('auth'); };
        window.addEventListener('CORTEX_OPEN_DRIVE', handler);
        return () => window.removeEventListener('CORTEX_OPEN_DRIVE', handler);
    }, []);

    const mockFiles = [
        { id: '1', name: 'Financial_Report_Q3.pdf', type: 'pdf' },
        { id: '2', name: 'Project_Alpha_Specs.gdoc', type: 'doc' },
        { id: '3', name: 'Invoice_Template.xls', type: 'sheet' },
        { id: '4', name: 'Meeting_Notes_Dec.txt', type: 'txt' },
    ];

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/80 backdrop-blur-sm">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-[600px] bg-[#1e1e1e] rounded-xl shadow-2xl overflow-hidden border border-slate-700 flex flex-col"
            >
                {/* Header */}
                <div className="bg-[#2d2d2d] p-4 flex justify-between items-center border-b border-slate-700">
                    <div className="flex items-center gap-2 text-slate-200 font-medium">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/1/12/Google_Drive_icon_%282020%29.svg" className="w-6 h-6" alt="Drive" />
                        <span>Google Drive Import</span>
                    </div>
                    <button onClick={() => setIsOpen(false)} className="text-slate-400 hover:text-white"><CloseIcon size={20} /></button>
                </div>

                {/* Body */}
                <div className="p-8 min-h-[300px] flex flex-col items-center justify-center">

                    {step === 'auth' && (
                        <div className="text-center space-y-4">
                            <h3 className="text-xl text-white font-semibold">Connect your Account</h3>
                            <p className="text-slate-400 text-sm max-w-xs mx-auto">Access your Documents, Sheets, and PDFs directly for AI Analysis.</p>
                            <button
                                onClick={() => setStep('picker')}
                                className="px-6 py-3 bg-white text-slate-900 rounded-full font-medium flex items-center gap-2 mx-auto hover:bg-slate-200 transition-colors"
                            >
                                <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg" className="w-5 h-5" />
                                Sign in with Google
                            </button>
                        </div>
                    )}

                    {step === 'picker' && (
                        <div className="w-full h-full flex flex-col">
                            <div className="flex items-center gap-2 text-sm text-slate-400 mb-4">
                                <span className="hover:text-white cursor-pointer">My Drive</span>
                                <span>/</span>
                                <span className="text-white">Cortex Imports</span>
                            </div>
                            <div className="grid grid-cols-1 gap-2 w-full">
                                {mockFiles.map(file => (
                                    <div
                                        key={file.id}
                                        onClick={() => setSelectedFiles(prev => prev.includes(file.id) ? prev.filter(x => x !== file.id) : [...prev, file.id])}
                                        className={`p-3 rounded border flex items-center justify-between cursor-pointer transition-all ${selectedFiles.includes(file.id)
                                            ? 'bg-blue-900/30 border-blue-500/50'
                                            : 'bg-slate-800/50 border-slate-700 hover:bg-slate-800'
                                            }`}
                                    >
                                        <div className="flex items-center gap-3">
                                            {file.type === 'pdf' ? <FileText className="text-red-400" size={20} /> :
                                                file.type === 'doc' ? <FileText className="text-blue-400" size={20} /> :
                                                    <FileText className="text-green-400" size={20} />}
                                            <span className="text-slate-200 text-sm">{file.name}</span>
                                        </div>
                                        {selectedFiles.includes(file.id) && <CheckCircle className="text-blue-400" size={18} />}
                                    </div>
                                ))}
                            </div>
                            <div className="mt-6 flex justify-end gap-2">
                                <button onClick={() => setStep('auth')} className="text-slate-400 text-sm hover:text-white px-3">Back</button>
                                <button
                                    disabled={selectedFiles.length === 0}
                                    onClick={() => setStep('ingest')}
                                    className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium disabled:opacity-50 hover:bg-blue-500"
                                >
                                    Select {selectedFiles.length > 0 ? `(${selectedFiles.length})` : ''}
                                </button>
                            </div>
                        </div>
                    )}

                    {step === 'ingest' && (
                        <div className="text-center space-y-4">
                            <Cloud className="w-16 h-16 text-blue-500 animate-pulse mx-auto" />
                            <h3 className="text-xl text-white font-semibold">Importing to Cortex...</h3>
                            <div className="w-64 h-2 bg-slate-800 rounded-full mx-auto overflow-hidden">
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: '100%' }}
                                    transition={{ duration: 2 }}
                                    onAnimationComplete={() => {
                                        setIsOpen(false);
                                        // Trigger a notification or something
                                        alert("Files imported (Simulation)");
                                    }}
                                    className="h-full bg-blue-500"
                                />
                            </div>
                            <p className="text-slate-500 text-xs">Processing vector embeddings...</p>
                        </div>
                    )}

                </div>
            </motion.div>
        </div>
    );
};

const DriveTrigger = () => {
    return (
        <button
            onClick={() => window.dispatchEvent(new Event('CORTEX_OPEN_DRIVE'))}
            className="w-full text-left p-3 rounded-lg flex items-center gap-3 text-slate-400 hover:bg-slate-900 hover:text-white transition-colors text-sm"
        >
            <Cloud size={16} className="shrink-0" />
            <span className="truncate">Google Drive</span>
        </button>
    );
};

export const GoogleDrivePlugin: Plugin = {
    manifest: {
        id: 'cortex.drive',
        name: 'Google Drive Sync',
        version: '0.1-beta',
        description: 'Import from Drive'
    },
    init: (ctx) => {
        ctx.registerSlot("global-overlay", DriveSelectorModal);
        ctx.registerSlot("sidebar-item", DriveTrigger);
    }
};
