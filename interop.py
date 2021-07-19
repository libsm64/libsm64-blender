import os
import platform
import ctypes as ct

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

sm64: ct.CDLL = None #type: ignore

class SM64Mario:
    def __init__(self, start_pos):
        global sm64

        if sm64 == None:
            this_path = os.path.dirname(os.path.realpath(__file__))
            dll_name = 'sm64.dll' if platform.system() == 'Windows' else 'libsm64.so'
            dll_path = os.path.join(this_path, 'lib', dll_name)
            rom_path = os.path.join(this_path, "baserom.us.z64")
            sm64 = ct.cdll.LoadLibrary(dll_path)

            with open(rom_path, 'rb') as file:
                rom_bytes = bytearray(file.read())
                rom_chars = ct.c_char * len(rom_bytes)
                texture_buff = (ct.c_ubyte * (4 * SM64_TEXTURE_WIDTH * SM64_TEXTURE_HEIGHT))()
                sm64.sm64_global_init.argtypes = [ ct.c_char_p, ct.POINTER(ct.c_ubyte), ct.c_char_p ]
                sm64.sm64_global_init(rom_chars.from_buffer(rom_bytes), texture_buff, None)
                create_texture(texture_buff)
                static_surfaces_load()

        sm64.sm64_mario_create.argtypes = [ ct.c_int16, ct.c_int16, ct.c_int16 ];
        sm64.sm64_mario_create.restype = ct.c_uint32;
        self.mario_id = sm64.sm64_mario_create(
            int(SM64_SCALE_FACTOR * start_pos.x),
            int(SM64_SCALE_FACTOR * start_pos.z) + 100,
            -int(SM64_SCALE_FACTOR * start_pos.y),
        )

        self.mario_inputs = SM64MarioInputs()
        self.mario_state = SM64MarioState()
        self.mario_geo = SM64MarioGeometryBuffers()

    def tick(self):
        sm64.sm64_mario_tick.argtypes = [ ct.c_uint32, ct.POINTER(SM64MarioInputs), ct.POINTER(SM64MarioState), ct.POINTER(SM64MarioGeometryBuffers) ]
        sm64.sm64_mario_tick(self.mario_id, ct.byref(self.mario_inputs), ct.byref(self.mario_state), ct.byref(self.mario_geo))

def create_texture(buffer):
    import bpy
    size = SM64_TEXTURE_WIDTH, SM64_TEXTURE_HEIGHT
    image = bpy.data.images.new("libsm64_mario_texture", width=size[0], height=size[1])
    pixels = [None] * size[0] * size[1]
    i = 0
    for y in range(size[1]):
        for x in range(size[0]):
            r = float(buffer[i]) / 255
            g = float(buffer[i+1]) / 255
            b = float(buffer[i+2]) / 255
            a = float(buffer[i+3]) / 255
            i += 4
            pixels[(y * size[0]) + x] = [r, g, b, a]
    pixels = [chan for px in pixels for chan in px]
    image.pixels = pixels

def static_surfaces_load():
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

    sm64.sm64_static_surfaces_load.argtypes = [ ct.POINTER(SM64Surface), ct.c_uint32 ]
    sm64.sm64_static_surfaces_load(surface_array, len(surfaces))


def get_all_surfaces():
    import bpy
    import mathutils
    from typing import cast, List

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


#   public enum SM64TerrainType
#   {
#       Grass  = 0x0000,
#       Stone  = 0x0001,
#       Snow   = 0x0002,
#       Sand   = 0x0003,
#       Spooky = 0x0004,
#       Water  = 0x0005,
#       Slide  = 0x0006,
#   }
#   public enum SM64SurfaceType
#   {
#       Default          = 0x0000,// Environment default
#       Burning          = 0x0001,// Lava / Frostbite (in SL), but is used mostly for Lava
#       Hangable         = 0x0005,// Ceiling that Mario can climb on
#       Slow             = 0x0009,// Slow down Mario, unused
#       VerySlippery     = 0x0013,// Very slippery, mostly used for slides
#       Slippery         = 0x0014,// Slippery
#       NotSlippery      = 0x0015,// Non-slippery, climbable
#       ShallowQuicksand = 0x0021,// Shallow Quicksand (depth of 10 units)
#       DeepQuicksand    = 0x0022,// Quicksand (lethal, slow, depth of 160 units)
#       InstantQuicksand = 0x0023,// Quicksand (lethal, instant)
#       Ice              = 0x002E,// Slippery Ice, in snow levels and THI's water floor
#       Hard             = 0x0030,// Hard floor (Always has fall damage)
#       HardSlippery     = 0x0035,// Hard and slippery (Always has fall damage)
#       HardVerySlippery = 0x0036,// Hard and very slippery (Always has fall damage)
#       HardNotSlippery  = 0x0037,// Hard and Non-slippery (Always has fall damage)
#       VerticalWind     = 0x0038,// Death at bottom with vertical wind
#   }
