import os
from threading  import Thread
from subprocess import PIPE, Popen
from queue import Queue

g_queue = None
g_running = False
g_shouldStop = False

def enqueue_output(exe_path):
    global g_queue, g_running, g_shouldStop
    proc = Popen([exe_path], shell=True, stdout=PIPE)
    g_queue = Queue()
    while not g_shouldStop:
        if proc.poll() is None:
            g_queue.put(proc.stdout.readline().decode('utf-8'))
        else:
            g_shouldStop = True
    proc.stdout.close()
    proc.kill()
    g_running = False

def start_input_reader():
    global g_running, g_shouldStop
    g_shouldStop = False
    if g_running:
        return
    g_running = True
    this_path = os.path.dirname(os.path.realpath(__file__))
    exe_path = os.path.join(this_path, 'lib', 'controller.exe')
    thread = Thread(target=enqueue_output, args=(exe_path,))
    thread.daemon = True
    thread.start()

def stop_input_reader():
    global g_shouldStop
    g_shouldStop = True

def sample_input_reader(mario_inputs):
    global g_queue
    has_line = False
    while not g_queue.empty():
        has_line = True
        line = g_queue.get()
    if not has_line:
        _sample_empty_inputs(mario_inputs)
        return
    vals = [int(x) for x in line.split()]
    if len(vals) < 5:
        _sample_empty_inputs(mario_inputs)
        return
    mario_inputs.stickX = _read_axis(float(vals[0]))
    mario_inputs.stickY = _read_axis(float(vals[1]))
    mario_inputs.buttonA = vals[2] != 0
    mario_inputs.buttonB = vals[3] != 0
    mario_inputs.buttonZ = vals[4] != 0

def _sample_empty_inputs(mario_inputs):
    mario_inputs.stickX = 0.0
    mario_inputs.stickY = 0.0
    mario_inputs.buttonA = False
    mario_inputs.buttonB = False
    mario_inputs.buttonZ = False

def _read_axis(val):
    val /= 32768.0
    if val < 0.2 and val > -0.2:
        return 0
    return (val - 0.2) / 0.8 if val > 0.0 else (val + 0.2) / 0.8
