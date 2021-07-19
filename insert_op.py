import bpy
import time
from mathutils import Vector
from typing import cast, Dict
from . mario import SM64Mario, SM64_GEO_MAX_TRIANGLES, SM64_SCALE_FACTOR, update_mesh_data
from . input_reader import sample_input_reader, start_input_reader

# https://wiki.blender.org/wiki/Reference/Release_Notes/2.80/Python_API/Mesh_API

mario: SM64Mario = None

def create_material(mat: bpy.types.Material):
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    nodes.clear()
    tex_node = nodes.new(type='ShaderNodeTexImage')
    tex_node.image = bpy.data.images.get("libsm64_mario_texture")
    color_node = nodes.new(type='ShaderNodeVertexColor')
    diffuse0_node = nodes.new(type='ShaderNodeBsdfDiffuse')
    diffuse1_node = nodes.new(type='ShaderNodeBsdfDiffuse')
    mix_node = nodes.new(type='ShaderNodeMixShader')
    out_node = nodes.new(type='ShaderNodeOutputMaterial')

    links = mat.node_tree.links
    links.new(tex_node.outputs[0], diffuse0_node.inputs[0])
    links.new(tex_node.outputs[1], mix_node.inputs[0])
    links.new(diffuse0_node.outputs[0], mix_node.inputs[2])
    links.new(color_node.outputs[0], diffuse1_node.inputs[0])
    links.new(diffuse1_node.outputs[0], mix_node.inputs[1])
    links.new(mix_node.outputs[0], out_node.inputs[0])

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

    mat = bpy.data.materials.new(name="libsm64_mario_material")
    create_material(mat)

    mesh.from_pydata(verts, edges, faces)
    mesh.uv_layers.active = mesh.uv_layers.new(name="uv0")
    mesh.materials.append(mat)

def cur_view():
    for a in bpy.context.window.screen.areas:
        if a.type == 'VIEW_3D':
            return a

def tick_mario():
    global events

    start_time = time.perf_counter()

    if 'mario' in cast(Dict[str, bpy.types.Mesh], bpy.data.meshes):
        mesh = cast(Dict[str, bpy.types.Mesh], bpy.data.meshes)['mario']
    else:
        mesh = bpy.data.meshes.new('mario')
        mesh.vertex_colors.new()
        init_mesh_data(mesh)
        new_object = bpy.data.objects.new('mario_object', mesh)
        bpy.context.scene.collection.objects.link(new_object)

    sample_input_reader(mario.mario_inputs)

    view3d = cur_view()
    r3d = view3d.spaces[0].region_3d

    look_dir = r3d.view_rotation @ Vector((0.0, 0.0, -1.0))
    mario.mario_inputs.camLookX = look_dir.x
    mario.mario_inputs.camLookZ = -look_dir.y

    mario.tick()

    bpy.context.scene.cursor.location = (
        mario.mario_state.posX / SM64_SCALE_FACTOR,
        -mario.mario_state.posZ / SM64_SCALE_FACTOR,
        mario.mario_state.posY / SM64_SCALE_FACTOR,
    )

    for region in (r for r in view3d.regions if r.type == 'WINDOW'):
        context_override = {'screen': bpy.context.screen, 'area': view3d, 'region': region}
        bpy.ops.view3d.view_center_cursor(context_override)

    update_mesh_data(mario, mesh)

    return 1 / 30 - (time.perf_counter() - start_time)


class InsertMario_OT_Operator(bpy.types.Operator):
    bl_idname = "view3d.libsm64_insert_mario"
    bl_label = "Insert Mario"
    bl_description = "Inserts a Mario into the scene"

    def execute(self, context):
        global mario
        global thread

        if mario != None:
            return {'FINISHED'}

        start_input_reader()
        mario = SM64Mario(bpy.context.scene.cursor.location)
        bpy.app.timers.register(tick_mario)

        return {'FINISHED'}
