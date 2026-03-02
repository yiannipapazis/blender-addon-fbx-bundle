# FBX Bundle Exporter

A simplified and modern take on the original FBX Bundle addon, designed for streamlined batch exporting from Blender.

## Features

*   **Simplified Batch Exporting**: Export multiple bundles of objects to FBX, DAE, glTF and OBJ.
*   **Flexible Bundling**: Group objects for export based on:
    *   Parent
    *   Collection
    *   Collection Instance
    *   Scene
*   **Automatic Pivot Placement**: The pivot point of each bundle is automatically determined by the bundling method.
*   **Multi-platform Support**: Export with presets for popular platforms like Unity and Unreal Engine.
*   **Streamlined UI**: A clean and simple interface to get your assets out of Blender quickly.

## Installation

1.  Download the `FBXBundleExporter.zip` file from the latest release.
2.  In Blender, go to `Edit > Preferences > Add-ons`.
3.  Click `Install...` and select the downloaded `.zip` file.
4.  Enable the "FBX Bundle" addon.

## How to Use

1.  Select the objects you want to export in the 3D View.
2.  Press the `N` key to open the Sidebar and look for the "FBX Bundle" tab.
3.  **Set Output Path**: Choose the folder where you want to save your files.
4.  **Select Target Platform**: Pick the platform you are exporting for (e.g., Unity, Unreal).
5.  **Choose "Bundle by" method**:
    *   **Parent**: Creates a bundle for each top-level parent of the selected objects. The parent's origin becomes the pivot point.
    *   **Collection**: Creates a bundle for each collection the selected objects belong to. The pivot will be at the world origin (0,0,0).
    *   **Collection Instance**: Creates a bundle for each collection instance. The pivot will be at the collection instance's origin.
    *   **Scene**: Exports all selected objects into a single file, pivoted at the world origin (0,0,0).
6.  Click the **Export** button. Your bundled files will appear in the specified output path.
