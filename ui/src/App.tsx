import ChatInterface from './components/ChatInterface';
import { PluginProvider } from './core/plugins/PluginProvider';
import { registry } from './core/plugins/registry';
import { ImageViewerPlugin } from './plugins/image-viewer';
import { NotesPlugin } from './plugins/notes';
import { CalculatorPlugin } from './plugins/calculator';
import { GoogleDrivePlugin } from './plugins/google-drive';

// --- REGISTER PLUGINS ---
registry.register(ImageViewerPlugin);
registry.register(NotesPlugin);
registry.register(CalculatorPlugin);
registry.register(GoogleDrivePlugin);

function App() {
  return (
    <PluginProvider>
      <div className="w-full h-full">
        <ChatInterface />
      </div>
    </PluginProvider>
  );
}

export default App;
