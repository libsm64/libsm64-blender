import os
import sys
from threading  import Thread
from subprocess import PIPE, Popen
from queue import Queue, Empty
import time

q = None

def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

#def _thread():
#    print("starting thread!")
#    global thread_running, proc
#    while thread_running:
#        while proc.poll() is None:
#            output = proc.stdout.readline()
#            print(output)
#    proc.kill()

def start_input_reader():
    global thread_running, q

    this_path = os.path.dirname(os.path.realpath(__file__))
    exe_path = os.path.join(this_path, 'lib', 'controller.exe')
    p = Popen([exe_path], shell=True, stdout=PIPE, bufsize=1)
    q = Queue()
    t = Thread(target=enqueue_output, args=(p.stdout, q))
    t.daemon
    t.start()

    #thread_running = True
    #thread = threading.Thread(target=_thread)
    #thread.daemon = True
    #thread.start()

def stop_input_reader():
    #global thread_running
    #thread_running = False
    pass

def sample_input_reader(mario_inputs):
    line = ''
    while True:
        try:
            line = q.get_nowait()
        except Empty:
            break
    print(line)
    #mario_inputs.stickX = _read_axis(float(event.state))
    #mario_inputs.stickY = _read_axis(float(event.state))
    #mario_inputs.buttonA = True
    #mario_inputs.buttonB = True
    #mario_inputs.buttonZ = True

def _read_axis(val):
    val /= 32768.0
    if val < 0.2 and val > -0.2:
        return 0
    return (val - 0.2) / 0.8 if val > 0.0 else (val + 0.2) / 0.8
