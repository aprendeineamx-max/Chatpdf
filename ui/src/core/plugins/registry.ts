import { Plugin, PluginContext } from './types';

class PluginRegistry {
    private plugins: Map<string, Plugin> = new Map();
    private slots: Map<string, React.ComponentType<any>[]> = new Map();
    public events = new EventTarget();

    register(plugin: Plugin) {
        if (this.plugins.has(plugin.manifest.id)) {
            console.warn(`Plugin ${plugin.manifest.id} already registered.`);
            return;
        }

        console.log(`[Cortex] Loading Plugin: ${plugin.manifest.name} v${plugin.manifest.version}`);

        const context: PluginContext = {
            registerSlot: (name, component) => {
                if (!this.slots.has(name)) {
                    this.slots.set(name, []);
                }
                this.slots.get(name)?.push(component);
            },
            events: this.events
        };

        try {
            plugin.init(context);
            this.plugins.set(plugin.manifest.id, plugin);
        } catch (e) {
            console.error(`[Cortex] Failed to load plugin ${plugin.manifest.id}:`, e);
        }
    }

    getSlots(slotName: string) {
        return this.slots.get(slotName) || [];
    }

    getPlugins() {
        return Array.from(this.plugins.values());
    }
}

export const registry = new PluginRegistry();
