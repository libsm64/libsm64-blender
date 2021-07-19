import threading
from . import zeth_inputs

thread_running = False
events = []

def _input_reader_thread():
    global thread_running
    global events
    while thread_running:
        events.append(zeth_inputs.get_gamepad())

def start_input_reader():
    global thread_running

    if thread_running:
        return

    thread_running = True
    thread = threading.Thread(target=_input_reader_thread)
    thread.daemon = True
    thread.start()

def stop_input_reader():
    global thread_running
    thread_running = False

def sample_input_reader(mario_inputs):
    while len(events) > 0 :
        for event in events[0]:
            if event.code == "ABS_X":
                mario_inputs.stickX = _read_axis(float(event.state))
            elif event.code == "ABS_Y":
                mario_inputs.stickY = _read_axis(float(event.state))
            elif event.code == "BTN_SOUTH":
                if event.state == 1:
                    mario_inputs.buttonA = True
                else:
                    mario_inputs.buttonA = False
            elif event.code == "BTN_NORTH":
                if event.state == 1:
                    mario_inputs.buttonB = True
                else:
                    mario_inputs.buttonB = False
            elif event.code == "BTN_TL":
                if event.state == 1:
                    mario_inputs.buttonZ = True
                else:
                    mario_inputs.buttonZ = False
            #elif event.code != "SYN_REPORT":
            #    print(event.code + ':' + str(event.state))
        events.pop(0)

def _read_axis(val):
    val /= 32768.0
    if val < 0.2 and val > -0.2:
        return 0
    return (val - 0.2) / 0.8 if val > 0.0 else (val + 0.2) / 0.8
