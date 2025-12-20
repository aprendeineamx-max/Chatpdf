
import { useState, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut, RotateCw, AlertTriangle } from 'lucide-react';

// Setup worker (Vite compatible)
import pdfWorker from 'pdfjs-dist/build/pdf.worker.min?url';
pdfjs.GlobalWorkerOptions.workerSrc = pdfWorker;

interface PDFViewerProps {
    pdfUrl: string | null;
    currentPage: number;
    onPageChange: (page: number) => void;
}

export function PDFViewer({ pdfUrl, currentPage, onPageChange }: PDFViewerProps) {
    const [numPages, setNumPages] = useState<number>(0);
    const [scale, setScale] = useState(1.0);
    const [inputPage, setInputPage] = useState<string>(currentPage.toString());

    // [FIX] Blob Loading State
    const [resolvedUrl, setResolvedUrl] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState<boolean>(false);

    useEffect(() => {
        setInputPage(currentPage.toString());
    }, [currentPage]);

    // [FIX] Robust Blob Fetching
    // This bypasses CORS issues by fetching the file via the main thread (where we have access)
    // and passing a Blob URL to the Worker.
    useEffect(() => {
        if (!pdfUrl) {
            setResolvedUrl(null);
            return;
        }

        let active = true;
        setLoading(true);
        setError(null);
        setResolvedUrl(null); // Reset to show loading

        async function fetchPdf() {
            try {
                console.log("📥 [PDFViewer] Fetching PDF:", pdfUrl);
                const res = await fetch(pdfUrl!);
                if (!res.ok) throw new Error(`Failed to fetch: ${res.status} ${res.statusText}`);

                const blob = await res.blob();
                if (!active) return;

                const objectUrl = URL.createObjectURL(blob);
                console.log("✅ [PDFViewer] Created Blob URL:", objectUrl);
                setResolvedUrl(objectUrl);
            } catch (err: any) {
                if (!active) return;
                console.error("❌ [PDFViewer] Error:", err);
                setError(err.message);
            } finally {
                if (active) setLoading(false);
            }
        }

        fetchPdf();

        return () => {
            active = false;
            if (resolvedUrl) URL.revokeObjectURL(resolvedUrl);
        };
    }, [pdfUrl]);

    function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
        setNumPages(numPages);
        setError(null);
    }

    function onDocumentLoadError(err: Error) {
        console.error("❌ [PDFViewer] Library Error:", err);
        setError(`PDF Library Error: ${err.message}`);
    }

    function handlePageSubmit(e: React.FormEvent) {
        e.preventDefault();
        const page = parseInt(inputPage);
        if (page >= 1 && page <= numPages) {
            onPageChange(page);
        } else {
            setInputPage(currentPage.toString()); // Reset on invalid
        }
    }

    if (!pdfUrl) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-gray-500 bg-[#0f0f12]">
                <div className="text-6xl mb-4">📄</div>
                <p>No document selected</p>
                <p className="text-xs text-gray-600 mt-2">Select a PDF from Knowledge or Ingest one.</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full bg-[#525659] relative"> {/* Google Drive grey background */}
            {/* Floating Top Toolbar */}
            <div className="bg-[#2b2c31] text-white flex items-center justify-between px-4 py-2 shadow-md z-10">
                <div className="flex items-center gap-4 bg-[#1e1f24] rounded-full px-2 py-1 shadow-inner">
                    <span className="text-xs font-bold px-2 text-purple-300 truncate max-w-[150px]" title={pdfUrl}>
                        {pdfUrl.split('/').pop()?.split('?')[0] || 'Document'}
                    </span>
                </div>

                <div className="flex items-center gap-2 bg-[#1e1f24] rounded-full px-3 py-1 shadow-inner">
                    <button onClick={() => onPageChange(Math.max(1, currentPage - 1))} disabled={currentPage <= 1} className="p-1 hover:bg-gray-700 rounded-full disabled:opacity-30 transition-colors">
                        <ChevronLeft className="w-5 h-5" />
                    </button>

                    <form onSubmit={handlePageSubmit} className="flex items-center">
                        <input
                            type="text"
                            className="w-10 bg-transparent text-center text-sm font-mono focus:outline-none border-b border-transparent focus:border-purple-500 transition-all"
                            value={inputPage}
                            onChange={(e) => setInputPage(e.target.value)}
                            onBlur={() => setInputPage(currentPage.toString())}
                        />
                        <span className="text-xs text-gray-500 select-none">/ {numPages || '-'}</span>
                    </form>

                    <button onClick={() => onPageChange(Math.min(numPages, currentPage + 1))} disabled={currentPage >= numPages} className="p-1 hover:bg-gray-700 rounded-full disabled:opacity-30 transition-colors">
                        <ChevronRight className="w-5 h-5" />
                    </button>
                </div>

                <div className="flex items-center gap-2 bg-[#1e1f24] rounded-full px-3 py-1 shadow-inner">
                    <button onClick={() => setScale(s => Math.max(0.5, s - 0.1))} className="p-1 hover:bg-gray-700 rounded-full">
                        <ZoomOut className="w-4 h-4" />
                    </button>
                    <span className="text-xs font-mono w-10 text-center text-gray-400">{Math.round(scale * 100)}%</span>
                    <button onClick={() => setScale(s => Math.min(2.5, s + 0.1))} className="p-1 hover:bg-gray-700 rounded-full">
                        <ZoomIn className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {/* Document Area */}
            <div className="flex-1 overflow-auto flex justify-center p-8 relative">
                {loading && (
                    <div className="absolute inset-0 flex items-center justify-center bg-black/50 z-20">
                        <div className="text-white animate-pulse">Downloading PDF...</div>
                    </div>
                )}

                {error && (
                    <div className="absolute inset-0 flex flex-col items-center justify-center bg-[#1a1a20] z-20 text-red-400 p-8 text-center">
                        <AlertTriangle className="w-12 h-12 mb-4" />
                        <p className="font-bold mb-2">Failed to load PDF</p>
                        <p className="text-sm font-mono bg-black/30 p-2 rounded">{error}</p>
                        <button
                            onClick={() => window.open(pdfUrl, '_blank')}
                            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                        >
                            Open External
                        </button>
                    </div>
                )}

                {resolvedUrl && !error && (
                    <Document
                        file={resolvedUrl}
                        onLoadSuccess={onDocumentLoadSuccess}
                        onLoadError={onDocumentLoadError}
                        className="shadow-[0_0_30px_rgba(0,0,0,0.5)]"
                        loading={<div className="text-white animate-pulse">Parsing PDF...</div>}
                    >
                        <Page
                            pageNumber={currentPage}
                            scale={scale}
                            renderTextLayer={false}
                            renderAnnotationLayer={false}
                            className="bg-white"
                            loading={""}
                        />
                    </Document>
                )}
            </div>
        </div>
    );
}
