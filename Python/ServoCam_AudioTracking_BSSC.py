import numpy as np
import sounddevice as sd
import serial
import time
import threading
import cv2
import platform
import serial.tools.list_ports
from dearpygui.dearpygui import *
from collections import defaultdict


# Use BasicSerialServoTest_BSST.INO on the arduino side

suppress_test_output = True #Set to False to have a TON of output in the console when running in test mode. 

# CONFIG ========
BAUD_RATE = 115200
SERVO_COUNT = 18
SAMPLE_RATE = 44100
UPDATE_INTERVAL = 0.05
x_servo_selection = defaultdict(bool)
y_servo_selection = defaultdict(bool)
motion_sensitivity = 0.3

# GLOBAL STATE ========
servo_values = [0] * SERVO_COUNT
last_sent = [None] * SERVO_COUNT
slider_tags = [f"servo{i}" for i in range(SERVO_COUNT)]
audio_running = False
audio_stream = None
audio_buffer = None
buffer_lock = threading.Lock()
camera_running = False
camera_thread = None

# USER SETTINGS ========
sensitivity_val = 10.0
responsiveness_val = 100.0
freq_min = 100.0
freq_max = 1500.0
servo_min = 5
servo_max = 110
BAND_EDGES = []

# SERIAL SETUP ========
available_ports = [p.device for p in serial.tools.list_ports.comports()]
remote_port = ""
robot_port = ""
ser_remote = None
ser_robot = None
test_mode = True

# BANDS ========
def update_band_edges():
    global BAND_EDGES
    BAND_EDGES = np.linspace(freq_min, freq_max, SERVO_COUNT + 1)

# SERVO SEND ========
def move_servo(index, angle):
    global ser_robot
    angle = max(min(angle, servo_max), servo_min)

    if last_sent[index] != angle:
        if not test_mode and ser_robot and ser_robot.is_open:
            try:
                ser_robot.write(f"S:{index}:{angle}\n".encode())
                last_sent[index] = angle
            except Exception as e:
                print(f"[Serial Error] {e}")
        elif test_mode and suppress_test_output == False:
            print(f"[TestMode] Servo {index} → {angle}")


# CALLBACKS ========

def x_servo_toggle(sender, app_data, user_data):
    x_servo_selection[user_data] = app_data

def y_servo_toggle(sender, app_data, user_data):
    y_servo_selection[user_data] = app_data

def motion_sensitivity_callback(sender, app_data, user_data):
    global motion_sensitivity
    motion_sensitivity = app_data

def slider_callback(sender, app_data, user_data):
    idx = int(user_data)
    if not audio_running:
        move_servo(idx, app_data)
    servo_values[idx] = app_data

def sensitivity_callback(sender, app_data, user_data):
    global sensitivity_val
    sensitivity_val = app_data

def responsiveness_callback(sender, app_data, user_data):
    global responsiveness_val
    responsiveness_val = app_data

def freq_min_callback(sender, app_data, user_data):
    global freq_min
    freq_min = max(10.0, min(app_data, freq_max - 1))
    update_band_edges()

def freq_max_callback(sender, app_data, user_data):
    global freq_max
    freq_max = max(app_data, freq_min + 1)
    update_band_edges()

def servo_min_callback(sender, app_data, user_data):
    global servo_min
    servo_min = max(4, min(app_data, servo_max - 1))

def servo_max_callback(sender, app_data, user_data):
    global servo_max
    servo_max = max(app_data, servo_min + 1)

def set_test_mode(enabled):
    global test_mode
    test_mode = enabled
    print(f"[Mode] Test Mode: {test_mode}")

def select_remote_port(sender, app_data, user_data=None):
    global remote_port
    remote_port = app_data
    print(f"[Select] Remote Port: {remote_port}")

def select_robot_port(sender, app_data, user_data=None):
    global robot_port
    robot_port = app_data
    print(f"[Select] Robot Port: {robot_port}")

def connect_serial_ports(sender, app_data=None, user_data=None):
    global ser_remote, ser_robot, test_mode
    if test_mode:
        print("[Connect] Running in TEST MODE. No serial connections made.")
        return

    if remote_port:
        try:
            ser_remote = serial.Serial(remote_port, BAUD_RATE, timeout=1)
            time.sleep(2)
            print(f"[Remote] Connected to {remote_port}")
        except Exception as e:
            print(f"[Remote Error] Could not open {remote_port}: {e}")
            ser_remote = None

    if robot_port:
        try:
            ser_robot = serial.Serial(robot_port, BAUD_RATE, timeout=1)
            time.sleep(2)
            print(f"[Robot] Connected to {robot_port}")
        except Exception as e:
            print(f"[Robot Error] Could not open {robot_port}: {e}")
            ser_robot = None

def start_audio(sender, app_data, user_data):
    global audio_running, audio_stream, camera_running
    if audio_running:
        return
    stop_camera(None, None, None)
    try:
        audio_running = True
        audio_stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE,
                                      blocksize=int(SAMPLE_RATE * UPDATE_INTERVAL))
        audio_stream.start()
        print("Audio started.")
    except Exception as e:
        print(f"[Start Error] {e}")
        audio_running = False

def stop_audio(sender, app_data, user_data):
    global audio_running, audio_stream
    try:
        if audio_stream:
            audio_stream.stop()
            audio_stream.close()
        audio_stream = None
        audio_running = False
        print("Audio stopped.")
    except Exception as e:
        print(f"[Stop Error] {e}")

def reset_servos_callback(sender, app_data, user_data):

    for i in range(SERVO_COUNT):
        neutral = servo_min
        try:
            set_value(slider_tags[i], neutral)
            move_servo(i, neutral)
            servo_values[i] = neutral
            time.sleep(0.02)
        except Exception as e:
            print(f"[Reset Error S{i}] {e}")



# AUDIO ========
def audio_callback(indata, frames, time_info, status):
    global audio_buffer
    with buffer_lock:
        audio_buffer = indata[:, 0].copy()

def audio_processing_loop():
    global servo_values
    while True:
        if not audio_running:
            time.sleep(0.01)
            continue

        with buffer_lock:
            buffer = audio_buffer.copy() if audio_buffer is not None else None

        if buffer is None:
            time.sleep(UPDATE_INTERVAL)
            continue

        try:
            audio = buffer * sensitivity_val
            fft = np.abs(np.fft.rfft(audio))
            freqs = np.fft.rfftfreq(len(audio), d=1 / SAMPLE_RATE)

            for i in range(SERVO_COUNT):
                low, high = BAND_EDGES[i], BAND_EDGES[i + 1]
                band = np.where((freqs >= low) & (freqs < high))[0]
                if len(band) == 0:
                    continue
                energy = np.mean(fft[band])
                angle = int(np.interp(energy, [0, responsiveness_val], [servo_min, servo_max]))
                servo_values[i] = angle
                move_servo(i, angle)
                set_value(slider_tags[i], angle)

            time.sleep(UPDATE_INTERVAL)
        except Exception as e:
            print(f"[Processing Error] {e}")


#REMOTE INPUT ========
#This section is basically a placeholder, using a freenove Uno with a joystick shield
#It reads joystick values and sends them to the main program to control sensitivity, toggle audio, pretty buggy. basically just looks cool. 

def remote_input_loop():
    global sensitivity_val, ser_remote, test_mode
    last_s1 = 0
    last_s2 = 0
    last_p1 = -1
    last_p2 = -1

    while True:
        if test_mode or ser_remote is None or not ser_remote.is_open:
            time.sleep(0.5)
            continue
        try:
            line = ser_remote.readline().decode(errors="ignore").strip()
            if not line or ':' not in line:
                continue

            key, val = line.split(":")
            key = key.strip()
            val = int(val.strip())

            if key == "P1":
                if abs(val - last_p1) >= 3:
                    sensitivity_val = round(np.interp(val, [0, 1023], [1, 50]), 2)
                    set_value("Sensitivity", sensitivity_val)
                    last_p1 = val



            elif key == "S1":
                if val != last_s1:
                    if val:
                        start_audio(None, None, None)
                    else:
                        stop_audio(None, None, None)
                    last_s1 = val

            elif key == "S2":
                if val != last_s2:
                    if val:
                        start_camera(None, None, None)
                    else:
                        stop_camera(None, None, None)
                    last_s2 = val

        except Exception as e:
            print(f"[Remote Input Error] {e}")
            time.sleep(0.5)

# CAMERA ========


def get_camera():
    system = platform.system()
    if system == "Windows":
        return cv2.VideoCapture(0, cv2.CAP_DSHOW)
    else:
        return cv2.VideoCapture(0)

camera_mode = 'normal'  # Options: normal, motionmask, infrared, hightech

def change_camera_mode(sender, app_data, user_data):
    global camera_mode
    camera_mode = app_data


def start_camera(sender, app_data, user_data):
    global camera_running, camera_thread, audio_running
    if camera_running:
        return
    stop_audio(None, None, None)
    camera_running = True
    camera_thread = threading.Thread(target=camera_loop, daemon=True)
    camera_thread.start()
    print("Camera started.")

def stop_camera(sender, app_data, user_data):
    global camera_running
    camera_running = False
    print("Camera stopped.")


def camera_loop():
    global camera_running, camera_mode
    cap = get_camera()
    _, prev = cap.read()
    prev = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    prev = cv2.GaussianBlur(prev, (21, 21), 0)

    while camera_running:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        diff = cv2.absdiff(prev, gray)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

        motion_map = cv2.bitwise_and(thresh, thresh)  # clone
        motion_coords = cv2.findNonZero(thresh)
        if motion_coords is not None:
            center = tuple(np.mean(motion_coords, axis=0)[0].astype(int))
            cv2.circle(frame, center, 10, (0, 0, 255), 2)

            # Use X/Y servos for motion pointing
            for i in range(SERVO_COUNT):
                if x_servo_selection[i]:
                    angle = int(np.interp(center[0], [0, frame.shape[1]], [servo_min, servo_max]))
                    move_servo(i, angle)
                    set_value(slider_tags[i], angle)
                if y_servo_selection[i]:
                    angle = int(np.interp(center[1], [0, frame.shape[0]], [servo_min, servo_max]))
                    move_servo(i, angle)
                    set_value(slider_tags[i], angle)

                # Apply camera mode filters
        display_frame = frame.copy()
        if camera_mode == 'motionmask':
            mask_colored = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
            display_frame = cv2.addWeighted(frame, 0.7, mask_colored, 0.3, 0)
        elif camera_mode == 'infrared':
            heat = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
            display_frame = heat
        elif camera_mode == 'hightech':
            hsv = cv2.applyColorMap(cv2.equalizeHist(gray), cv2.COLORMAP_HOT)
            display_frame = hsv

        # Draw red circle reticle (same center as earlier if motion is detected)
        if motion_coords is not None:
            cv2.circle(display_frame, center, 10, (0, 0, 255), 2)

        cv2.imshow("Motion + Aim", display_frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break


        prev = gray.copy()

    cap.release()
    cv2.destroyAllWindows()
# GUI ========


def setup_gui():
    create_context()
    create_viewport(title='Servo Control')

    with window(label="Motion Tracking Config", width=500, height=450, pos=(50, 50)):
        add_slider_float(label="Motion Sensitivity", min_value=0.05, max_value=1.0,
                         default_value=motion_sensitivity, callback=motion_sensitivity_callback)
        add_combo(label="Camera Mode", items=["normal", "motionmask", "infrared", "hightech"],
          default_value="normal", callback=change_camera_mode)

        add_text("Servo Role Selector")

        for i in range(SERVO_COUNT):
            with group(horizontal=True):
                add_checkbox(label=f"X{i}", callback=x_servo_toggle, user_data=i)
                add_checkbox(label=f"Y{i}", callback=y_servo_toggle, user_data=i)

    with window(label="Connection Setup", autosize=True, pos=(600, 50)):
        add_checkbox(label="Test Mode", default_value=True, callback=lambda s, a, u: set_test_mode(a))
        add_combo(label="Remote Input Port", items=available_ports, callback=select_remote_port)
        add_combo(label="Robot Output Port", items=available_ports, callback=select_robot_port)
        add_button(label="Connect", callback=connect_serial_ports)

    with window(label="Servo Control", autosize=True, pos=(600, 300)):
        add_button(label="Start Audio", callback=start_audio)
        add_button(label="Stop Audio", callback=stop_audio)
        add_button(label="Start Camera", callback=start_camera)
        add_button(label="Stop Camera", callback=stop_camera)
        add_button(label="Reset All Servos", callback=reset_servos_callback)

        add_slider_float(label="Sensitivity", min_value=1, max_value=50,
                         default_value=sensitivity_val, callback=sensitivity_callback, tag="Sensitivity")
        add_slider_float(label="Responsiveness", min_value=10, max_value=300,
                         default_value=responsiveness_val, callback=responsiveness_callback)
        add_slider_float(label="Freq Min (Hz)", min_value=10, max_value=500,
                         default_value=freq_min, callback=freq_min_callback)
        add_slider_float(label="Freq Max (Hz)", min_value=500, max_value=20000,
                         default_value=freq_max, callback=freq_max_callback)
        add_slider_int(label="Servo Min Angle", min_value=4, max_value=175,
                       default_value=servo_min, callback=servo_min_callback)
        add_slider_int(label="Servo Max Angle", min_value=5, max_value=180,
                       default_value=servo_max, callback=servo_max_callback)

        with group(horizontal=True):
            for i in range(SERVO_COUNT):
                add_slider_int(
                    label=f"S{i}",
                    default_value=servo_min,
                    min_value=0,
                    max_value=180,
                    width=30,
                    vertical=True,
                    callback=slider_callback,
                    tag=f"servo{i}",
                    user_data=i
                )

    setup_dearpygui()
    show_viewport()


# RUN ========
def check_for_exit():
    if not is_viewport_ok():
        stop_dearpygui()

def on_exit():
    print("[Exit] Viewport closed.")
    # Add any extra cleanup here if needed

if __name__ == "__main__":
    threading.Thread(target=remote_input_loop, daemon=True).start()
    update_band_edges()
    setup_gui()
    threading.Thread(target=audio_processing_loop, daemon=True).start()
    threading.Thread(target=reset_servos_callback, args=(None, None, None), daemon=True).start()

    set_exit_callback(on_exit) 
    start_dearpygui()
    destroy_context()
