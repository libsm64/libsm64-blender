import bpy
from mathutils import Vector
from typing import cast, Dict
from . interop import SM64Mario, SM64_GEO_MAX_TRIANGLES, SM64_SCALE_FACTOR
from . inputs import inputs_initialize, inputs_read

# https://wiki.blender.org/wiki/Reference/Release_Notes/2.80/Python_API/Mesh_API

running_sim = False
mario: SM64Mario = None #type:ignore

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
    val /= 256
    if val < 0.2 and val > -0.2:
        return 0
    return (val - 0.2) / 0.8 if val > 0.0 else (val + 0.2) / 0.8

def cur_view():
    for a in bpy.context.window.screen.areas: #type:ignore
        if a.type == 'VIEW_3D':
            return a

def tick_mario():
    if 'mario' in cast(Dict[str, bpy.types.Mesh], bpy.data.meshes):
        mesh = cast(Dict[str, bpy.types.Mesh], bpy.data.meshes)['mario']
    else:
        mesh = bpy.data.meshes.new('mario') #type:ignore
        mesh.vertex_colors.new() #type:ignore
        init_mesh_data(mesh)
        new_object = bpy.data.objects.new('mario_object', mesh) #type:ignore
        bpy.context.scene.collection.objects.link(new_object) #type:ignore

    inputs = inputs_read()
    mario.mario_inputs.stickX = read_axis(inputs['x_axis'])
    mario.mario_inputs.stickY = read_axis(inputs['y_axis'])

    view3d = cur_view()
    r3d = view3d.spaces[0].region_3d #type:ignore
    look_dir = r3d.view_rotation @ Vector((0.0, 0.0, -1.0))

    mario.mario_inputs.camLookX = look_dir.x
    mario.mario_inputs.camLookZ = -look_dir.y
    mario.mario_inputs.buttonA = inputs['button_a']
    mario.mario_inputs.buttonB = inputs['button_b']
    mario.mario_inputs.buttonZ = inputs['button_z']

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

        if mario != None:
            return {'FINISHED'}

        mario = SM64Mario(bpy.context.scene.cursor.location)
        inputs_initialize()
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.app.timers.register(tick_mario)

        return {'FINISHED'}
