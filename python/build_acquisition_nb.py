from _nb_builder import md, code, write_notebook

cells = []

cells.append(md("""\
# WSN Lab 1 — Data Acquisition

Two ways to get a CSV into `data/raw/`:

1. **Real hardware**: read the ESP32's serial port directly with `pyserial`
   (Section 7.3 of the lab guide). Use this once you've moved off Wokwi onto
   the real board.
2. **Wokwi simulation**: Wokwi doesn't expose a serial port to this notebook,
   so instead you copy the Serial Monitor's text output and paste it into a
   `.txt` file, and the second section below parses that into the same CSV
   format.

Either path lands you in the same place: a file in `data/raw/` with columns
`sample,temp_raw,humidity,light,motion,temp_cal,temp_ma,temp_roc,status,valid`,
ready for `analysis.ipynb`.
"""))

cells.append(md("## 1. Real hardware acquisition (pyserial)\n\nRun this cell only when the ESP32 is plugged in over USB. Adjust `PORT` first — on Windows it looks like `COM5`, on macOS/Linux like `/dev/ttyUSB0` or `/dev/cu.usbserial-...`."))

cells.append(code("""\
import serial
import time
import csv

PORT = "COM6"            # <-- Windows: COM6 etc. macOS/Linux: /dev/ttyUSB0 or /dev/cu.usbmodem...
BAUD = 115200
DURATION_S = 900         # 15 minutes -> ~900 rows at 1 Hz (guide needs >= 600)
OUT_PATH = "../data/raw/hardware_serial_log.csv"

def is_header(line):
    first = line.split(",")[0].strip().lower()
    return first in ("timestamp", "sample")

def capture_from_serial(port=PORT, baud=BAUD, duration_s=DURATION_S, out_path=OUT_PATH):
    \"\"\"Close the Arduino IDE Serial Monitor first -- only one program can use the port.
    Press the board's RESET button right after starting this cell so the header row is captured.\"\"\"
    ser = serial.Serial(port, baud, timeout=2)
    time.sleep(2)
    header, rows, start = None, [], time.time()
    print(f"Capturing for {duration_s} s ... (press RESET on the board now)")
    while time.time() - start < duration_s:
        line = ser.readline().decode(errors="ignore").strip()
        if not line or "," not in line:
            continue                      # skip blank lines and startup messages
        if is_header(line):
            header = line.split(",")
            rows = []                     # start fresh from the header
            continue
        parts = line.split(",")
        if header is None or len(parts) == len(header):
            rows.append(parts)
        if len(rows) % 60 == 0 and rows:
            print(f"  {len(rows)} rows so far")
    ser.close()
    if header is None:                    # board never restarted: keep the data with generic names
        header = [f"col{i}" for i in range(len(rows[0]))]
        print("WARNING: no header row seen -- press RESET after starting next time.")
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(r for r in rows if len(r) == len(header))
    print(f"Captured {len(rows)} rows -> {out_path}")
    return out_path

# Uncomment to run against the real board:
# capture_from_serial()
"""))

cells.append(md("## 2. Parsing a Wokwi Serial Monitor capture\n\nIn Wokwi, select the Serial Monitor output, copy it, and paste it into a plain text file (e.g. `../data/raw/wokwi_serial_dump.txt`) — one line per row, exactly as it appeared on screen. This cell turns that text dump into a proper CSV."))

cells.append(code("""\
import pandas as pd

def parse_wokwi_dump(txt_path, out_csv_path):
    header = None
    rows = []
    with open(txt_path) as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            if line.split(",")[0].strip().lower() in ("timestamp", "sample"):
                header = line.split(",")
                continue
            if header is None:
                continue  # still inside the startup banner text
            parts = line.split(",")
            if len(parts) == len(header):
                rows.append(parts)

    df = pd.DataFrame(rows, columns=header)
    df.to_csv(out_csv_path, index=False)
    print(f"Parsed {len(df)} rows -> {out_csv_path}")
    return df

# Example:
# parse_wokwi_dump("../data/raw/wokwi_serial_dump.txt", "../data/raw/wokwi_serial_log.csv")
"""))

cells.append(md("## 3. For now: use the synthetic sample dataset\n\n`generate_sample_data.py` already wrote `../data/raw/sample_serial_log.csv` — a synthetic capture with the exact same columns a real run would produce, including a stable baseline, an LDR light sweep, a temperature spike above 30°C, a few PIR motion events, and a handful of invalid/NaN rows. Loading it here just confirms the file is well-formed before `analysis.ipynb` uses it."))

cells.append(code("""\
import pandas as pd

df = pd.read_csv("../data/raw/sample_serial_log.csv")
print(df.shape)
df.head()
"""))

write_notebook("acquisition.ipynb", cells)
