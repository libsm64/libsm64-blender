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

class LibSm64Properties(bpy.types.PropertyGroup):
    rom_path : bpy.props.StringProperty(
        name="Path",
        description="Path to an unmodified US SM64 ROM", 
        subtype='FILE_PATH',
        default=('c:\\sm64.us.z64' if platform.system() == 'Windows' else '~/sm64.us.z64')
    )
    mario_scale : bpy.props.FloatProperty(
        name="Blender to SM64 Scale",
        default=100
    )

class Main_PT_Panel(bpy.types.Panel):
    bl_idname = "LIBSM64_PT_main_panel"
    bl_label = "Insert Mario"
    bl_category = "LibSM64"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        col = layout.column()
        prop_split(col, scene.libsm64, "mario_scale", "Blender to SM64 Scale")
        col.label(text="SM64 US ROM (Unmodified, 8 MB, z64)")
        col.prop(scene.libsm64, "rom_path")
        col.operator(InsertMario_OT_Operator.bl_idname, text='Insert Mario')

class InsertMario_OT_Operator(bpy.types.Operator):
    bl_idname = "view3d.libsm64_insert_mario"
    bl_label = "Insert Mario"
    bl_description = "Inserts a Mario into the scene"

    def execute(self, context):
        scene = context.scene
        insert_mario(scene.libsm64.rom_path, scene.libsm64.mario_scale, bpy.context.scene.cursor.location)
        return {'FINISHED'}

register_classes, unregister_classes = bpy.utils.register_classes_factory((
    LibSm64Properties,
    Main_PT_Panel,
    InsertMario_OT_Operator
))

def register():
    register_classes()
    bpy.types.Scene.libsm64 = bpy.props.PointerProperty(type=LibSm64Properties)

def unregister():
    unregister_classes()
    del bpy.types.Scene.libsm64

def prop_split(layout, data, field, name):
    split = layout.split(factor = 0.5)
    split.label(text = name)
    split.prop(data, field, text = '')
