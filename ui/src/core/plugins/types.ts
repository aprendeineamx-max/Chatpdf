import { ReactNode } from 'react';

export interface PluginManifest {
    id: string;
    name: string;
    version: string;
    description?: string;
}

export interface Plugin {
    manifest: PluginManifest;
    init: (context: PluginContext) => void;
    components?: Record<string, React.ComponentType<any>>;
}

export interface PluginContext {
    registerSlot: (slotName: string, component: React.ComponentType<any>) => void;
    events: EventTarget;
}

export type SlotRenderer = (slotName: string, props?: any) => ReactNode[];
