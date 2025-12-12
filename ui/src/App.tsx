import { useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import { PluginProvider } from './core/plugins/PluginProvider';
import { registry } from './core/plugins/registry';
import ImageViewerPlugin from './plugins/image-viewer';
import NotesPlugin from './plugins/notes';
import CalculatorPlugin from './plugins/calculator';
import GoogleDrivePlugin from './plugins/google-drive';

function App() {
  useEffect(() => {
    // Register Core Plugins
    registry.register(new ImageViewerPlugin());
    registry.register(new NotesPlugin());
    registry.register(new CalculatorPlugin());
    registry.register(new GoogleDrivePlugin());
  }, []);

  return (
    <PluginProvider>
      <div className="w-full h-full">
        <ChatInterface />
      </div>
    </PluginProvider>
  );
}

export default App;
