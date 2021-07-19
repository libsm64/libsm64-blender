bl_info = {
    "name" : "libsm64-blender",
    "author" : "libsm64",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "View3D",
    "warning" : "",
    "category" : "Generic"
}

import bpy
from . mario import insert_mario

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

class InsertMario_OT_Operator(bpy.types.Operator):
    bl_idname = "view3d.libsm64_insert_mario"
    bl_label = "Insert Mario"
    bl_description = "Inserts a Mario into the scene"

    def execute(self, context):
        insert_mario(bpy.context.scene.cursor.location)
        return {'FINISHED'}

register, unregister = bpy.utils.register_classes_factory((
    Main_PT_Panel,
    InsertMario_OT_Operator
))
