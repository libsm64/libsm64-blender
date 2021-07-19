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
from . main_panel import Main_PT_Panel
from . mario_op import InsertMario_OT_Operator

register, unregister = bpy.utils.register_classes_factory((
    Main_PT_Panel,
    InsertMario_OT_Operator
))
