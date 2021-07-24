import os
from threading  import Thread
from subprocess import PIPE, Popen
from queue import Queue

g_queue = None
g_proc = None
g_running = False

def enqueue_output():
    global g_queue, g_proc
    while g_running:
        g_queue.put(g_proc.stdout.readline())
    g_proc.stdout.close()
    g_proc.kill()

def start_input_reader():
    global g_queue, g_proc, g_running
    this_path = os.path.dirname(os.path.realpath(__file__))
    exe_path = os.path.join(this_path, 'lib', 'controller.exe')
    g_proc = Popen([exe_path], shell=True, stdout=PIPE, bufsize=1)
    g_queue = Queue()
    thread = Thread(target=enqueue_output)
    thread.daemon = True
    g_running = True
    thread.start()

def stop_input_reader():
    global g_running
    g_running = False

def sample_input_reader(mario_inputs):
    global g_queue
    has_line = False
    while not g_queue.empty():
        has_line = True
        line = g_queue.get()
    if not has_line:
        return
    vals = [int(x) for x in line.decode('utf-8').split()]
    mario_inputs.stickX = _read_axis(float(vals[0]))
    mario_inputs.stickY = _read_axis(float(vals[1]))
    mario_inputs.buttonA = vals[2] != 0
    mario_inputs.buttonB = vals[3] != 0
    mario_inputs.buttonZ = vals[4] != 0

def _read_axis(val):
    val /= 32768.0
    if val < 0.2 and val > -0.2:
        return 0
    return (val - 0.2) / 0.8 if val > 0.0 else (val + 0.2) / 0.8
