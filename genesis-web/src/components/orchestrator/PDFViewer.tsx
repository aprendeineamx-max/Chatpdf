
import { useState, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut } from 'lucide-react';

// Setup worker (required for react-pdf)
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

interface PDFViewerProps {
    pdfUrl: string | null;
    currentPage: number;
    onPageChange: (page: number) => void;
}

export function PDFViewer({ pdfUrl, currentPage, onPageChange }: PDFViewerProps) {
    const [numPages, setNumPages] = useState<number>(0);
    const [scale, setScale] = useState(1.0);

    function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
        setNumPages(numPages);
    }

    if (!pdfUrl) {
        return (
            <div className="flex items-center justify-center h-full text-gray-500">
                No PDF Document Loaded
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full bg-[#1a1a20] border-l border-gray-800">
            {/* Toolbar */}
            <div className="h-10 bg-[#131316] border-b border-gray-800 flex items-center justify-between px-4">
                <div className="flex items-center gap-2">
                    <button onClick={() => onPageChange(Math.max(1, currentPage - 1))} disabled={currentPage <= 1} className="p-1 hover:bg-gray-700 rounded disabled:opacity-50">
                        <ChevronLeft className="w-4 h-4" />
                    </button>
                    <span className="text-xs font-mono text-gray-400">
                        Page {currentPage} of {numPages}
                    </span>
                    <button onClick={() => onPageChange(Math.min(numPages, currentPage + 1))} disabled={currentPage >= numPages} className="p-1 hover:bg-gray-700 rounded disabled:opacity-50">
                        <ChevronRight className="w-4 h-4" />
                    </button>
                </div>
                <div className="flex items-center gap-2">
                    <button onClick={() => setScale(s => Math.max(0.5, s - 0.1))} className="p-1 hover:bg-gray-700 rounded">
                        <ZoomOut className="w-4 h-4" />
                    </button>
                    <span className="text-xs font-mono text-gray-400">{Math.round(scale * 100)}%</span>
                    <button onClick={() => setScale(s => Math.min(2.5, s + 0.1))} className="p-1 hover:bg-gray-700 rounded">
                        <ZoomIn className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {/* Document Area */}
            <div className="flex-1 overflow-auto flex justify-center p-4 bg-gray-900/50">
                <Document
                    file={pdfUrl}
                    onLoadSuccess={onDocumentLoadSuccess}
                    className="shadow-2xl"
                >
                    <Page
                        pageNumber={currentPage}
                        scale={scale}
                        renderTextLayer={false}
                        renderAnnotationLayer={false}
                        className="border border-gray-700"
                    />
                </Document>
            </div>
        </div>
    );
}
