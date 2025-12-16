import { StrictMode, Component, ErrorInfo, ReactNode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App'

class ErrorTrap extends Component<{ children: ReactNode }, { hasError: boolean, error: Error | null }> {
    constructor(props: { children: ReactNode }) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error: Error) {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error("Uncaught Error:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div style={{ padding: 20, background: '#222', color: '#f88', height: '100vh', fontFamily: 'monospace' }}>
                    <h1>💥 CRITICAL SYSTEM FAILURE</h1>
                    <h3>The Architect encountered a fatal runtime error.</h3>
                    <pre style={{ background: '#000', padding: 10, overflow: 'auto' }}>
                        {this.state.error?.toString()}
                    </pre>
                    <button onClick={() => window.location.reload()} style={{ padding: 10, marginTop: 20, cursor: 'pointer' }}>
                        Attempt System Restart
                    </button>
                </div>
            );
        }
        return this.props.children;
    }
}

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <ErrorTrap>
            <App />
        </ErrorTrap>
    </StrictMode>,
)
