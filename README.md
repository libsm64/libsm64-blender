# libsm64-blender - Blender client for LibSM64

This add-on integrates [libsm64](https://github.com/libsm64/libsm64) into Blender and provides various additional integrations with [Fast64](https://bitbucket.org/kurethedead/fast64/).
Practically, this means if you're making levels with Fast64 in Blender, you can use this add-on to drop a controller-playable Mario into your scene to run around and test your terrain layout.

**Warning:** This plugin hasn't been battle-tested for very long, save often and use at your own risk!

If you find a way to crash it, please post an issue or otherwise let me know!

![Example map](https://github.com/libsm64/libsm64-blender/raw/master/docs/example.gif)
###### Example map by [Agent-11](https://github.com/agent-11)

### Installation

Only Windows and linux are currently supported, no MacOS support yet unfortunately.

Download the latest release zip [from here](https://github.com/libsm64/libsm64-blender/releases). In Blender, go to Edit -> Preferences -> Add-Ons and click the "Install" button to install the plugin from the zip file. Find the libsm64-blender addon in the addon list and enable it. If it does not show up, go to Edit -> Preferences -> Save&Load and make sure 'Auto Run Python Scripts' is enabled.

### Usage
Before opening Blender make sure you have an XInput controller connected if you want to control Mario with a controller. Alternatively you can use the keyboard to control him. With the add-on enabled there should be a LibSM64 tab in the properties sidebar. Browse to an unmodified SM64 US z64 ROM, and then click the "Insert Mario" button to insert a controllable Mario at the 3D cursor location. To stop the simulation just delete the "LibSM64 Mario" object from the scene.

*Note:* The SM64 US ROM must be the one with the SHA1 checksum of `9bef1128717f958171a4afac3ed78ee2bb4e86ce`.

### Current Features
- Insert playable Mario into Blender scene
- Fast64 terrain type and collision surface type support

### Near-term Features
- Water boxes support
- Toggles to give wing/metal/vanish cap

### Far-term Features
- Moving platform support
- Camera integration
- Linking against custom decomp builds (modified controls/Mario model/etc)
