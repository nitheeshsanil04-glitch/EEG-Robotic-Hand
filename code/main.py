import serial
import time

# -------- SERIAL SETUP --------
# NPG connected to Pi
npg = serial.Serial('/dev/ttyACM0', 230400, timeout=1)
time.sleep(2)

# Reset + start NPG stream
npg.setDTR(False)
time.sleep(1)
npg.reset_input_buffer()
npg.setDTR(True)
time.sleep(2)

npg.write(b'START\n')
time.sleep(1)

# UNO connected to Pi
uno = serial.Serial('/dev/ttyACM1', 9600)
time.sleep(2)

# -------- THRESHOLDS --------
EEG_THRESHOLD = 1700   # Channel 0 (A0)
EMG_THRESHOLD = 1800   # Channels 1–5 (A1–A5)

# -------- NPG PACKET SYNC --------
SYNC1 = 0xC7
SYNC2 = 0x7C

# -------- VARIABLES --------
last_print = time.time()

# previous trigger states
prev_states = [False] * 6

print("MULTI CHANNEL SYSTEM RUNNING...")

# -------- MAIN LOOP --------
while True:
    try:
        byte = npg.read(1)

        # detect packet start
        if byte and byte[0] == SYNC1:

            byte2 = npg.read(1)

            if byte2 and byte2[0] == SYNC2:

                # read packet
                packet = npg.read(12)

                if len(packet) >= 12:

                    # -------- EXTRACT CHANNELS --------
                    ch = []

                    for i in range(6):
                        value = (packet[1 + 2*i] << 8) | packet[2 + 2*i]
                        ch.append(value)

                    # Channel mapping
                    # ch[0] = EEG  (A0)
                    # ch[1] = EMG1 (A1)
                    # ch[2] = EMG2 (A2)
                    # ch[3] = EMG3 (A3)
                    # ch[4] = EMG4 (A4)
                    # ch[5] = EMG5 (A5)

                    # -------- PRINT EVERY 1 SECOND --------
                    if time.time() - last_print >= 1:

                        print(
                            "EEG:", ch[0],
                            "| EMG1:", ch[1],
                            "| EMG2:", ch[2],
                            "| EMG3:", ch[3],
                            "| EMG4:", ch[4],
                            "| EMG5:", ch[5]
                        )

                        print("------------------------")

                        last_print = time.time()

                    # -------- EEG MASTER ENABLE --------
                    eeg_active = ch[0] > EEG_THRESHOLD

                    # -------- EMG FINGER CONTROL --------
                    if eeg_active:

                        for i in range(1, 6):

                            current_state = ch[i] > EMG_THRESHOLD

                            # Rising edge detection
                            if current_state and not prev_states[i]:

                                print(f"Finger {i} Triggered")

                                # send command to UNO
                                uno.write(str(i).encode())

                                time.sleep(0.5)

                            prev_states[i] = current_state

                    else:
                        # reset states when EEG inactive
                        prev_states = [False] * 6

    except KeyboardInterrupt:
        print("\nStopping system...")
        break

# -------- CLEANUP --------
npg.close()
uno.close()
