"""
Record the Arduino's Serial Monitor output straight into a CSV file.

How to use (Windows):
  1. Close the Serial Monitor in the Arduino IDE (only one program can use COM6).
  2. Open Command Prompt in the folder where this file is.
  3. Type:   python capture_serial.py
  4. Press the RESET button on the Arduino when it says so.
  5. Wait 15 minutes. The file hardware_serial_log.csv appears in the same folder.
     (Press Ctrl+C to stop early -- everything recorded so far is still saved.)
"""
import csv
import time

import serial   # installed with:  pip install pyserial

PORT = "COM6"          # same port the Arduino IDE shows at the bottom right
BAUD = 115200          # same speed as Serial.begin(115200) in the code
DURATION_S = 15 * 60   # 15 minutes
OUT_FILE = "hardware_serial_log.csv"


def is_header(line):
    return line.split(",")[0].strip().lower() in ("timestamp", "sample")


def main():
    ser = serial.Serial(PORT, BAUD, timeout=2)
    time.sleep(2)
    print(f"Connected to {PORT}. Press RESET on the Arduino now.")
    print(f"Recording for {DURATION_S // 60} minutes -- press Ctrl+C to stop early.\n")

    header, rows = None, []
    start = time.time()
    try:
        while time.time() - start < DURATION_S:
            line = ser.readline().decode(errors="ignore").strip()
            if not line or "," not in line:
                continue                      # skip blank lines and start-up messages
            print(line)                        # show it on screen like the Serial Monitor
            if is_header(line):
                header, rows = line.split(","), []
                continue
            rows.append(line.split(","))
    except KeyboardInterrupt:
        print("\nStopped early.")
    finally:
        ser.close()

    if not rows:
        print("No data received. Check the port name and that the Serial Monitor is closed.")
        return
    if header is None:
        header = [f"col{i}" for i in range(len(rows[0]))]
        print("Note: no header row was seen (RESET wasn't pressed) -- columns named col0, col1, ...")
    good = [r for r in rows if len(r) == len(header)]
    with open(OUT_FILE, "w", newline="") as f:
        csv.writer(f).writerow(header)
        csv.writer(f).writerows(good)
    print(f"\nSaved {len(good)} rows to {OUT_FILE}")


if __name__ == "__main__":
    main()
