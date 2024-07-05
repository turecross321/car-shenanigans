import obd
import time
import vlc

OBD_PORT = "COM12"
OBD_BAUDRATE = 9600

DEACCELERATION_THRESHOLD = 10
MINIMUM_SPEED = 40
POLLING_DELAY = 1
MIN_RPM = 2250

print("Starting connection")
connection = obd.OBD(portstr=OBD_PORT, baudrate=OBD_BAUDRATE)

if connection.is_connected():
    print("Connected to OBD adapter")
else:
    print("Unable to connect")
    exit()

slow_player = vlc.MediaPlayer("slow.wav")
fast_player = vlc.MediaPlayer("fast.mp3")

top_speed = 0

STATE_SLOW = 0
STATE_FAST = 1
state: int = STATE_SLOW

skip_check: int = 0
skip_cycles = 1

while True:
    rpm = connection.query(obd.commands.RPM).value.magnitude
    speed = connection.query(obd.commands.SPEED).value.magnitude

    if speed > MINIMUM_SPEED and not fast_player.is_playing() and rpm >= MIN_RPM:
        state = STATE_FAST
        top_speed = speed
    elif speed > top_speed:
        top_speed = speed
    elif not slow_player.is_playing() and top_speed - speed > DEACCELERATION_THRESHOLD:
        state = STATE_SLOW
        top_speed = 0


    print(f"RPM: {rpm}")
    print(f"SPEED: {speed}")

    if state == STATE_SLOW:
        if not slow_player.is_playing():
            if skip_check > 0:
                skip_check -= 1
            else:
                slow_player.stop()
                slow_player.play()
                skip_check = skip_cycles

        if fast_player.is_playing():
            fast_player.stop()
    elif state == STATE_FAST:
        if not fast_player.is_playing():
            if skip_check > 0:
                skip_check -= 1
            else:
                fast_player.stop()
                fast_player.play()
                skip_check = skip_cycles
        if slow_player.is_playing():
            fast_player.stop()


    time.sleep(POLLING_DELAY)

connection.close()