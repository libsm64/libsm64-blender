import bpy
import threading
from . import inputs
from mathutils import Vector
from typing import cast, Dict
from . interop import SM64Mario, SM64_GEO_MAX_TRIANGLES, SM64_SCALE_FACTOR

# https://wiki.blender.org/wiki/Reference/Release_Notes/2.80/Python_API/Mesh_API

thread: threading.Thread = None #type:ignore
mario: SM64Mario = None #type:ignore
events = []

def worker():
    global events
    while True:
        events.append(inputs.get_gamepad())

def init_mesh_data(mesh: bpy.types.Mesh):
    verts = []
    edges = []
    faces = []

    for i in range(SM64_GEO_MAX_TRIANGLES):
        verts.append((0,0,0))
        verts.append((0,0,0))
        verts.append((0,0,0))
        edges.append((3*i+0, 3*i+1))
        edges.append((3*i+1, 3*i+2))
        edges.append((3*i+2, 3*i+0))
        faces.append((3*i+0, 3*i+1, 3*i+2))

    mesh.from_pydata(verts, edges, faces) #type:ignore

def update_mesh_data(mesh: bpy.types.Mesh):
    vcol = mesh.vertex_colors.active #type:ignore
    for i in range(mario.mario_geo.numTrianglesUsed):
        mesh.vertices[3*i+0].co.x =  mario.mario_geo.position_data[9*i+0] / SM64_SCALE_FACTOR #type:ignore
        mesh.vertices[3*i+0].co.z =  mario.mario_geo.position_data[9*i+1] / SM64_SCALE_FACTOR #type:ignore
        mesh.vertices[3*i+0].co.y = -mario.mario_geo.position_data[9*i+2] / SM64_SCALE_FACTOR #type:ignore
        mesh.vertices[3*i+1].co.x =  mario.mario_geo.position_data[9*i+3] / SM64_SCALE_FACTOR #type:ignore
        mesh.vertices[3*i+1].co.z =  mario.mario_geo.position_data[9*i+4] / SM64_SCALE_FACTOR #type:ignore
        mesh.vertices[3*i+1].co.y = -mario.mario_geo.position_data[9*i+5] / SM64_SCALE_FACTOR #type:ignore
        mesh.vertices[3*i+2].co.x =  mario.mario_geo.position_data[9*i+6] / SM64_SCALE_FACTOR #type:ignore
        mesh.vertices[3*i+2].co.z =  mario.mario_geo.position_data[9*i+7] / SM64_SCALE_FACTOR #type:ignore
        mesh.vertices[3*i+2].co.y = -mario.mario_geo.position_data[9*i+8] / SM64_SCALE_FACTOR #type:ignore

        vcol.data[3*i+0].color = ( #type:ignore
            mario.mario_geo.color_data[9*i+0],
            mario.mario_geo.color_data[9*i+1],
            mario.mario_geo.color_data[9*i+2],
            1.0
        )
        vcol.data[3*i+1].color = ( #type:ignore
            mario.mario_geo.color_data[9*i+3],
            mario.mario_geo.color_data[9*i+4],
            mario.mario_geo.color_data[9*i+5],
            1.0
        )
        vcol.data[3*i+2].color = ( #type:ignore
            mario.mario_geo.color_data[9*i+6],
            mario.mario_geo.color_data[9*i+7],
            mario.mario_geo.color_data[9*i+8],
            1.0
        )
    mesh.update()

def read_axis(val):
    val /= 32768.0
    if val < 0.2 and val > -0.2:
        return 0
    return (val - 0.2) / 0.8 if val > 0.0 else (val + 0.2) / 0.8

def cur_view():
    for a in bpy.context.window.screen.areas: #type:ignore
        if a.type == 'VIEW_3D':
            return a

def tick_mario():
    global events

    if 'mario' in cast(Dict[str, bpy.types.Mesh], bpy.data.meshes):
        mesh = cast(Dict[str, bpy.types.Mesh], bpy.data.meshes)['mario']
    else:
        mesh = bpy.data.meshes.new('mario') #type:ignore
        mesh.vertex_colors.new() #type:ignore
        init_mesh_data(mesh)
        new_object = bpy.data.objects.new('mario_object', mesh) #type:ignore
        bpy.context.scene.collection.objects.link(new_object) #type:ignore

    while len(events) > 0 :
        for event in events[0]:
            if event.code == "ABS_X":
                mario.mario_inputs.stickX = read_axis(float(event.state))
            elif event.code == "ABS_Y":
                mario.mario_inputs.stickY = read_axis(float(event.state))
            elif event.code == "BTN_SOUTH":
                if event.state == 1:
                    mario.mario_inputs.buttonA = True
                else:
                    mario.mario_inputs.buttonA = False
            elif event.code == "BTN_NORTH":
                if event.state == 1:
                    mario.mario_inputs.buttonB = True
                else:
                    mario.mario_inputs.buttonB = False
            elif event.code == "BTN_TL":
                if event.state == 1:
                    mario.mario_inputs.buttonZ = True
                else:
                    mario.mario_inputs.buttonZ = False
            #elif event.code != "SYN_REPORT":
            #    print(event.code + ':' + str(event.state))
        events.pop(0)

    view3d = cur_view()
    r3d = view3d.spaces[0].region_3d #type:ignore

    look_dir = r3d.view_rotation @ Vector((0.0, 0.0, -1.0))
    mario.mario_inputs.camLookX = look_dir.x
    mario.mario_inputs.camLookZ = -look_dir.y

    mario.tick()

    bpy.context.scene.cursor.location = ( #type:ignore
        mario.mario_state.posX / SM64_SCALE_FACTOR,
        -mario.mario_state.posZ / SM64_SCALE_FACTOR,
        mario.mario_state.posY / SM64_SCALE_FACTOR,
    )

    for region in (r for r in view3d.regions if r.type == 'WINDOW'): #type:ignore
        context_override = {'screen': bpy.context.screen, 'area': view3d, 'region': region}
        bpy.ops.view3d.view_center_cursor(context_override) #type:ignore

    update_mesh_data(mesh)

    return 0.03

class InsertMario_OT_Operator(bpy.types.Operator):
    bl_idname = "view3d.libsm64_insert_mario"
    bl_label = "Insert Mario"
    bl_description = "Inserts a Mario into the scene"

    def execute(self, context):
        global mario
        global thread

        if mario != None:
            return {'FINISHED'}

        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()

        mario = SM64Mario(bpy.context.scene.cursor.location)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.app.timers.register(tick_mario)

        return {'FINISHED'}
