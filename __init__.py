bl_info = {
    "name" : "libsm64-blender",
    "author" : "libsm64",
    "description" : "Add a playble Mario to your Blender Scene",
    "blender" : (2, 80, 0),
    "version" : (1, 0, 5),
    "location" : "View3D",
    "warning" : "",
    "category" : "Generic"
}

import bpy
import platform
from . mario import insert_mario

class LibSm64Properties(bpy.types.PropertyGroup):
    rom_path : bpy.props.StringProperty(
        name="Path",
        description="Path to an unmodified US SM64 ROM",
        subtype='FILE_PATH',
        default=('c:\\sm64.us.z64' if platform.system() == 'Windows' else '~/sm64.us.z64')
    )
    camera_follow : bpy.props.BoolProperty (
        name="Follow Mario with 3D cursor + camera",
        default=True
    )
    camera_vert_shift : bpy.props.FloatProperty (
        name='Camera Vertical Offset', 
        description='Camera Offset from Mario Origin.', 
        default=(1.0), 
        soft_min =-10.0, 
        soft_max=10.0, 
        step=10, 
        precision=3, 
        subtype='DISTANCE', 
        unit='LENGTH', 
    )
    # FIXME: I couldn't figure out how to pass a FloatVectorProperty into the script, so this is disbled for now. 
    # The below lines (40 to 51) would replace the camera_vert_shift above, if properly implemented.
    # camera_vector_test : bpy.props.FloatVectorProperty (
    #     name='Mario Cam Offset', 
    #     description='Camera Offset from Mario Origin.', 
    #     default=(0.0, 0.0, 1.0), 
    #     soft_min =-10.0, 
    #     soft_max=10.0, 
    #     step=10, 
    #     precision=3,
    #     subtype='XYZ', 
    #     unit='LENGTH', 
    #     size=3
    # )
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
        # col.prop(scene.libsm64, "camera_vector_test") #FIXME
        col.prop(scene.libsm64, "camera_follow")
        col.prop(scene.libsm64, "camera_vert_shift")
        col.operator(InsertMario_OT_Operator.bl_idname, text='Insert Mario')
        col.operator(ControlMario_OT_Operator.bl_idname, text='Control Mario with keyboard')
        col.label(text="WASD + JKL to move. ESC to stop.")

class InsertMario_OT_Operator(bpy.types.Operator):
    bl_idname = "view3d.libsm64_insert_mario"
    bl_label = "Insert Mario"
    bl_description = "Inserts a Mario into the scene"

    def execute(self, context):
        scene = context.scene
        err = insert_mario(scene.libsm64.rom_path, scene.libsm64.mario_scale, scene.libsm64.camera_follow, scene.libsm64.camera_vert_shift)
        if err != None:
            self.report({"ERROR"}, err)
        return {'FINISHED'}


class ControlMario_OT_Operator(bpy.types.Operator):
    bl_idname = "view3d.libsm64_control_mario"
    bl_label = "Control with keyboard"
    bl_description = "Control Mario with keyboard"

    def invoke(self, context, event):
        global config
        config["keyboard_control"] = True
        if 'LibSM64 Mario' not in bpy.data.objects:
            return self.report({"ERROR"}, 'Insert Mario first.')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if not config["keyboard_control"]:
            return {'FINISHED'}
        if event.type == 'ESC':
            config["keyboard_control"] = False
            return {'FINISHED'}

        process_input(event)

        return {'RUNNING_MODAL'}

config = {
    'keyboard_control': False
}

input_value = {
    'UP': False,
    'DOWN': False,
    'LEFT': False,
    'RIGHT': False,
    'A': False,
    'B': False,
    'C': False,
}

input_config = {
    'UP': 'W',
    'DOWN': 'S',
    'LEFT': 'A',
    'RIGHT': 'D',
    'A': 'J',
    'B': 'K',
    'C': 'L',
}

def process_input(event):
    for k, v in input_config.items():
        if event.type == v:
            if event.value == 'PRESS':
                input_value[k] = True
            else:
                input_value[k] = False


register_classes, unregister_classes = bpy.utils.register_classes_factory((
    LibSm64Properties,
    Main_PT_Panel,
    InsertMario_OT_Operator,
    ControlMario_OT_Operator
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
