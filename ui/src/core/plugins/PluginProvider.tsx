import React, { createContext, useContext, useEffect, useState } from 'react';
import { registry } from './registry';

interface PluginContextValue {
    renderSlot: (name: string, props?: any) => React.ReactNode;
}

const PluginContext = createContext<PluginContextValue | null>(null);

export function PluginProvider({ children }: { children: React.ReactNode }) {
    // Force re-render when registry changes (simplified for MVP)
    const [, setTick] = useState(0);

    return (
        <PluginContext.Provider value={{
            renderSlot: (name, props) => {
                const components = registry.getSlots(name);
                return components.map((Comp, idx) => <Comp key={idx} {...props} />);
            }
        }}>
            {children}
            {/* Global Plugin Mount Point (Overlay Layer) */}
            <div id="cortex-plugin-layer" className="fixed inset-0 pointer-events-none z-[100]">
                {registry.getSlots("global-overlay").map((Comp, idx) => <Comp key={idx} />)}
            </div>
        </PluginContext.Provider>
    );
}

export const usePlugins = () => {
    const ctx = useContext(PluginContext);
    if (!ctx) throw new Error("usePlugins must be used within PluginProvider");
    return ctx;
};
