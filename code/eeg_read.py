import serial

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

    while True:
        eeg_data = ser.readline().decode('utf-8').strip()
        print("EEG Signal:", eeg_data)

except KeyboardInterrupt:
    print("Stopping EEG Monitoring")

except Exception as e:
    print("Error:", e)
