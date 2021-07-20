import bpy
import time
import os
import platform
import ctypes as ct
import mathutils
from typing import cast, List
from . input_reader import sample_input_reader, start_input_reader

SM64_TEXTURE_WIDTH = 64 * 11
SM64_TEXTURE_HEIGHT = 64
SM64_GEO_MAX_TRIANGLES = 1024
SM64_SCALE_FACTOR = 50

class SM64Surface(ct.Structure):
    _fields_ = [
        ('surftype', ct.c_int16),
        ('force', ct.c_int16),
        ('terrain', ct.c_uint16),
        ('v0x', ct.c_int16), ('v0y', ct.c_int16), ('v0z', ct.c_int16),
        ('v1x', ct.c_int16), ('v1y', ct.c_int16), ('v1z', ct.c_int16),
        ('v2x', ct.c_int16), ('v2y', ct.c_int16), ('v2z', ct.c_int16)
    ]

class SM64MarioInputs(ct.Structure):
    _fields_ = [
        ('camLookX', ct.c_float), ('camLookZ', ct.c_float),
        ('stickX', ct.c_float), ('stickY', ct.c_float),
        ('buttonA', ct.c_ubyte), ('buttonB', ct.c_ubyte), ('buttonZ', ct.c_ubyte),
    ]

class SM64MarioState(ct.Structure):
    _fields_ = [
        ('posX', ct.c_float), ('posY', ct.c_float), ('posZ', ct.c_float),
        ('velX', ct.c_float), ('velY', ct.c_float), ('velZ', ct.c_float),
        ('faceAngle', ct.c_float),
        ('health', ct.c_int16),
    ]

class SM64MarioGeometryBuffers(ct.Structure):
    _fields_ = [
        ('position', ct.POINTER(ct.c_float)),
        ('normal', ct.POINTER(ct.c_float)),
        ('color', ct.POINTER(ct.c_float)),
        ('uv', ct.POINTER(ct.c_float)),
        ('numTrianglesUsed', ct.c_uint16)
    ]

    def __init__(self):
        self.position_data = (ct.c_float * (SM64_GEO_MAX_TRIANGLES * 3 * 3))()
        self.position = ct.cast(self.position_data , ct.POINTER(ct.c_float))
        self.normal_data = (ct.c_float * (SM64_GEO_MAX_TRIANGLES * 3 * 3))()
        self.normal = ct.cast(self.normal_data , ct.POINTER(ct.c_float))
        self.color_data = (ct.c_float * (SM64_GEO_MAX_TRIANGLES * 3 * 3))()
        self.color = ct.cast(self.color_data , ct.POINTER(ct.c_float))
        self.uv_data = (ct.c_float * (SM64_GEO_MAX_TRIANGLES * 3 * 2))()
        self.uv = ct.cast(self.uv_data , ct.POINTER(ct.c_float))
        self.numTrianglesUsed = 0

    def __del__(self):
        pass

sm64: ct.CDLL = None

mario_id = -1
mario_inputs = SM64MarioInputs()
mario_state = SM64MarioState()
mario_geo = SM64MarioGeometryBuffers()

def insert_mario(rom_path: str, pos):
    global sm64, mario_id

    if mario_id >= 0:
        return

    if sm64 == None:
        this_path = os.path.dirname(os.path.realpath(__file__))
        dll_name = 'sm64.dll' if platform.system() == 'Windows' else 'libsm64.so'
        dll_path = os.path.join(this_path, 'lib', dll_name)
        sm64 = ct.cdll.LoadLibrary(dll_path)

        sm64.sm64_global_init.argtypes = [ ct.c_char_p, ct.POINTER(ct.c_ubyte), ct.c_char_p ]
        sm64.sm64_static_surfaces_load.argtypes = [ ct.POINTER(SM64Surface), ct.c_uint32 ]
        sm64.sm64_mario_create.argtypes = [ ct.c_int16, ct.c_int16, ct.c_int16 ];
        sm64.sm64_mario_create.restype = ct.c_int32;
        sm64.sm64_mario_tick.argtypes = [ ct.c_uint32, ct.POINTER(SM64MarioInputs), ct.POINTER(SM64MarioState), ct.POINTER(SM64MarioGeometryBuffers) ]

        with open(os.path.expanduser(rom_path), 'rb') as file:
            rom_bytes = bytearray(file.read())
            rom_chars = ct.c_char * len(rom_bytes)
            texture_buff = (ct.c_ubyte * (4 * SM64_TEXTURE_WIDTH * SM64_TEXTURE_HEIGHT))()
            sm64.sm64_global_init(rom_chars.from_buffer(rom_bytes), texture_buff, None)
            initialize_all_data(texture_buff)

    surface_array = get_surface_array_from_scene()

    sm64.sm64_static_surfaces_load(surface_array, len(surface_array))

    mario_id = sm64.sm64_mario_create(
        int(SM64_SCALE_FACTOR * pos.x),
        int(SM64_SCALE_FACTOR * pos.z) + 1,
        -int(SM64_SCALE_FACTOR * pos.y),
    )

    mario_obj = bpy.data.objects.new('LibSM64 Mario', bpy.data.meshes['libsm64_mario_mesh'])
    bpy.context.scene.collection.objects.link(mario_obj)

    start_input_reader()
    bpy.app.timers.register(tick_mario)

def tick_mario():
    global sm64, mario_id, mario_state, mario_geo

    start_time = time.perf_counter()

    if not ('LibSM64 Mario' in bpy.data.objects):
        sm64.sm64_mario_delete(mario_id)
        bpy.app.timers.unregister(tick_mario)
        mario_id = -1
        return 0

    sample_input_reader(mario_inputs)

    for a in bpy.context.window.screen.areas:
        if a.type == 'VIEW_3D':
            view3d = a
            break

    r3d = view3d.spaces[0].region_3d

    look_dir = r3d.view_rotation @ mathutils.Vector((0.0, 0.0, -1.0))
    mario_inputs.camLookX = look_dir.x
    mario_inputs.camLookZ = -look_dir.y

    sm64.sm64_mario_tick(mario_id, ct.byref(mario_inputs), ct.byref(mario_state), ct.byref(mario_geo))

    bpy.context.scene.cursor.location = (
        mario_state.posX / SM64_SCALE_FACTOR,
        -mario_state.posZ / SM64_SCALE_FACTOR,
        mario_state.posY / SM64_SCALE_FACTOR,
    )

    for region in (r for r in view3d.regions if r.type == 'WINDOW'):
        context_override = {'screen': bpy.context.screen, 'area': view3d, 'region': region}
        bpy.ops.view3d.view_center_cursor(context_override)

    update_mesh_data(bpy.data.meshes['libsm64_mario_mesh'])

    return 1 / 30 - (time.perf_counter() - start_time)

def get_surface_array_from_scene():
    surfaces = get_all_surfaces()
    surface_array = (SM64Surface * len(surfaces))()

    for i in range(len(surfaces)):
        surface_array[i].surftype = 0
        surface_array[i].force = 0
        surface_array[i].terrain = 1
        surface_array[i].v0x = int(SM64_SCALE_FACTOR *  surfaces[i]['v0x'])
        surface_array[i].v0y = int(SM64_SCALE_FACTOR *  surfaces[i]['v0z'])
        surface_array[i].v0z = int(SM64_SCALE_FACTOR * -surfaces[i]['v0y'])
        surface_array[i].v1x = int(SM64_SCALE_FACTOR *  surfaces[i]['v1x'])
        surface_array[i].v1y = int(SM64_SCALE_FACTOR *  surfaces[i]['v1z'])
        surface_array[i].v1z = int(SM64_SCALE_FACTOR * -surfaces[i]['v1y'])
        surface_array[i].v2x = int(SM64_SCALE_FACTOR *  surfaces[i]['v2x'])
        surface_array[i].v2y = int(SM64_SCALE_FACTOR *  surfaces[i]['v2z'])
        surface_array[i].v2z = int(SM64_SCALE_FACTOR * -surfaces[i]['v2y'])

    return surface_array

def get_all_surfaces():
    def add_mesh(matrix_world, mesh: bpy.types.Mesh, out):
        mesh.calc_loop_triangles()
        for tri in cast(List[bpy.types.MeshLoopTriangle], mesh.loop_triangles):
            out_elem = {}
            for i in range(3):
                tri_idx = tri.vertices[i]
                vx = mesh.vertices[tri_idx].co.x
                vy = mesh.vertices[tri_idx].co.y
                vz = mesh.vertices[tri_idx].co.z
                vworld = matrix_world @ mathutils.Vector((vx, vy, vz, 1))
                out_elem['v' + str(i) + 'x'] = vworld.x
                out_elem['v' + str(i) + 'y'] = vworld.y
                out_elem['v' + str(i) + 'z'] = vworld.z
            out.append(out_elem)

    scene = bpy.context.window.scene
    out = []

    for obj in cast(List[bpy.types.Object], scene.collection.all_objects):
        if isinstance(obj.data, bpy.types.Mesh):
            add_mesh(obj.matrix_world, obj.data, out)

    return out

def initialize_all_data(texture_buffer):
    size = SM64_TEXTURE_WIDTH, SM64_TEXTURE_HEIGHT
    if 'libsm64_mario_texture' in bpy.data.images:
        image = bpy.data.images["libsm64_mario_texture"]
    else:
        image = bpy.data.images.new("libsm64_mario_texture", width=size[0], height=size[1])
    pixels = [None] * size[0] * size[1]
    i = 0
    for y in range(size[1]):
        for x in range(size[0]):
            r = float(texture_buffer[i]) / 255
            g = float(texture_buffer[i+1]) / 255
            b = float(texture_buffer[i+2]) / 255
            a = float(texture_buffer[i+3]) / 255
            i += 4
            pixels[(y * size[0]) + x] = [r, g, b, a]
    pixels = [chan for px in pixels for chan in px]
    image.alpha_mode = 'STRAIGHT'
    image.file_format = 'PNG'
    image.pixels = pixels

    if 'libsm64_mario_material' in bpy.data.materials:
        mat = bpy.data.materials["libsm64_mario_material"]
    else:
        mat = bpy.data.materials.new(name="libsm64_mario_material")
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

    if not ('libsm64_mario_mesh' in bpy.data.meshes):
        mesh = bpy.data.meshes.new('libsm64_mario_mesh')
        mesh.vertex_colors.new()
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
        mesh.from_pydata(verts, edges, faces)
        mesh.uv_layers.active = mesh.uv_layers.new(name="uv0")
        mesh.materials.append(mat)

def update_mesh_data(mesh: bpy.types.Mesh):
    global mario_geo
    vcol = mesh.vertex_colors.active
    for i in range(mario_geo.numTrianglesUsed):
        mesh.vertices[3*i+0].co.x =  mario_geo.position_data[9*i+0] / SM64_SCALE_FACTOR
        mesh.vertices[3*i+0].co.z =  mario_geo.position_data[9*i+1] / SM64_SCALE_FACTOR
        mesh.vertices[3*i+0].co.y = -mario_geo.position_data[9*i+2] / SM64_SCALE_FACTOR
        mesh.vertices[3*i+1].co.x =  mario_geo.position_data[9*i+3] / SM64_SCALE_FACTOR
        mesh.vertices[3*i+1].co.z =  mario_geo.position_data[9*i+4] / SM64_SCALE_FACTOR
        mesh.vertices[3*i+1].co.y = -mario_geo.position_data[9*i+5] / SM64_SCALE_FACTOR
        mesh.vertices[3*i+2].co.x =  mario_geo.position_data[9*i+6] / SM64_SCALE_FACTOR
        mesh.vertices[3*i+2].co.z =  mario_geo.position_data[9*i+7] / SM64_SCALE_FACTOR
        mesh.vertices[3*i+2].co.y = -mario_geo.position_data[9*i+8] / SM64_SCALE_FACTOR
        mesh.uv_layers.active.data[mesh.loops[3*i+0].index].uv = (mario_geo.uv_data[6*i+0], mario_geo.uv_data[6*i+1])
        mesh.uv_layers.active.data[mesh.loops[3*i+1].index].uv = (mario_geo.uv_data[6*i+2], mario_geo.uv_data[6*i+3])
        mesh.uv_layers.active.data[mesh.loops[3*i+2].index].uv = (mario_geo.uv_data[6*i+4], mario_geo.uv_data[6*i+5])
        vcol.data[3*i+0].color = (
            mario_geo.color_data[9*i+0],
            mario_geo.color_data[9*i+1],
            mario_geo.color_data[9*i+2],
            1.0
        )
        vcol.data[3*i+1].color = (
            mario_geo.color_data[9*i+3],
            mario_geo.color_data[9*i+4],
            mario_geo.color_data[9*i+5],
            1.0
        )
        vcol.data[3*i+2].color = (
            mario_geo.color_data[9*i+6],
            mario_geo.color_data[9*i+7],
            mario_geo.color_data[9*i+8],
            1.0
        )
    mesh.update()
