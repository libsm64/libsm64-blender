import bpy

class Main_PT_Panel(bpy.types.Panel):
    bl_idname = "LIBSM64_PT_main_panel"
    bl_label = "libsm64"
    bl_category = "libsm64"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator('view3d.libsm64_insert_mario', text='Insert Mario')