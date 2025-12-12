# Implementation Plan - Phase 5: Cortex Plugin System

## Goal
Create a modular, extensible "WordPress-style" plugin architecture for the UI, starting with a native **Image Viewer**.

## Philosophy
"Everything is a Plugin." Features should be removable, upgradeable, and independent.

## Architecture

### 1. The Core (`ui/src/core/plugins`)
*   **`PluginRegistry`**: A central store (Singleton) that holds all active plugins.
*   **`usePlugins`**: A React Hook to access plugin slot functionality (e.g., `renderSlot("sidebar-item")`).
*   **`PluginProvider`**: Context provider to wrap the application.

### 2. The First Plugin (`ui/src/plugins/image-viewer`)
*   **Manifest**: Defines the plugin (ID: `cortex.image-viewer`, Version: `1.0`).
*   **Component**: `ImageViewerModal` - A glassmorphism-styled lightbox.
*   **Action**: Listens for `OPEN_IMAGE` events globally.

### 3. Integration
*   **`App.tsx`**: Will now wrap the app in `PluginProvider`.
*   **`ControlPanel`**: (Optional) Add a "Plugins" tab to toggle them (Future).

## Steps
1.  **Refactor**: Create `ui/src/core` and `ui/src/plugins`.
2.  **Core Logic**: Implement the Registry and Provider.
3.  **Develop Plugin**: Create the Image Viewer functionality.
4.  **Register**: "Install" the plugin by default in `main.tsx`.
5.  **Trigger**: Add a test image or button to verify the "Native Viewing" experience.

## "WordPress-Style"
We will create a specific `plugins.ts` file that acts like `wp-config.php`/`functions.php` where plugins are imported and activated.
