import os
from threading  import Thread
from subprocess import PIPE, Popen
from queue import Queue

g_proc = None

def stop_input_reader():
    global g_proc
    if g_proc != None:
        g_proc.stdout.close()
        g_proc.kill()
        g_proc = None

def start_input_reader():
    global g_proc
    stop_input_reader()
    this_path = os.path.dirname(os.path.realpath(__file__))
    exe_path = os.path.join(this_path, 'lib', 'controller.exe')
    g_proc = Popen([exe_path], shell=False, stdin=PIPE, stdout=PIPE)
    g_proc.stdin.write('\n'.encode())
    g_proc.stdin.flush()

def sample_input_reader(mario_inputs):
    global g_proc

    line = ""
    if g_proc.poll() is None:
        line = g_proc.stdout.readline().decode('utf-8')
        g_proc.stdin.write('\n'.encode())
        g_proc.stdin.flush()

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
