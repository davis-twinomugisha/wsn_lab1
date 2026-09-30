# WSN Lab 1 — Design, Implementation and Calibration of a Multi-Sensor Edge Node

Wireless Sensor Networks, Laboratory Guide 1. A multi-sensor ESP32 edge node
(temperature/humidity, light, motion) built and validated in Wokwi, with a
Python pipeline that turns its serial output into real statistics and plots.

## Repository structure

```
lab1/
├── firmware/
│   └── sensor_node/
│       ├── sensor_node.ino     # firmware
│       ├── diagram.json        # Wokwi circuit description
│       └── libraries.txt       # Arduino libraries the sketch needs
├── python/
│   ├── acquisition.ipynb       # real-hardware pyserial capture + Wokwi-dump parser
│   ├── analysis.ipynb          # stats + plots, run against the real capture
│   ├── analysis_colab.ipynb    # same analysis, set up to run in Google Colab
│   ├── generate_sample_data.py # builds the synthetic reference dataset
│   ├── build_acquisition_nb.py # regenerates acquisition.ipynb from source
│   ├── build_analysis_nb.py    # regenerates analysis.ipynb from source
│   ├── build_analysis_nb_colab.py
│   └── _nb_builder.py          # shared helper used by the build_*.py scripts
├── data/
│   ├── raw/
│   │   ├── wokwi_serial_dump.txt   # raw text copied from Wokwi's Serial Monitor
│   │   ├── wokwi_serial_log.csv    # ^ parsed into CSV — the real dataset used below
│   │   └── sample_serial_log.csv   # synthetic dataset, kept for reference
│   └── processed/
│       └── cleaned_log.csv         # output of analysis.ipynb
├── figures/
│   ├── temp_vs_time.png
│   ├── humidity_vs_time.png
│   ├── raw_vs_filtered_temp.png
│   ├── light_vs_time.png
│   └── motion_events.png
├── docs/
│   ├── circuit_diagram.png
│   ├── make_circuit_diagram.py   # regenerates circuit_diagram.png
│   └── lab_report.pdf            # technical report (Section 9.2)
└── README.md
```

This matches the layout the lab guide recommends in Section 9.3.

**GitHub repository:** https://github.com/davis-twinomugisha/wsn_lab1

**Wokwi simulation:** https://wokwi.com/projects/476121306266761217

**Physical prototype firmware (Arduino UNO R4 WiFi):** `firmware/uno_r4_prototype/prototype_node.ino`

## Hardware / wiring (three sensing modalities, per the guide's minimum)

| Sensor | Signal pin | Power |
|---|---|---|
| DHT22 (temperature + humidity) | GPIO4 (SDA) | 3V3 / GND |
| Photoresistor module (light) | GPIO34 (AO, analog) | 3V3 / GND |
| PIR motion sensor | GPIO27 (OUT, digital) | 3V3 / GND |

There's also an LED (GPIO26, via a 220Ω resistor) that lights up whenever
`status` becomes `HIGH_TEMP`, and a buzzer (GPIO25) that clicks whenever
`motion == 1` — the "local decision or status indicator" the scenario asks
for. See `docs/circuit_diagram.png` for the full wiring diagram.

## Firmware (`firmware/sensor_node/sensor_node.ino`)

Implements, per the lab guide:

- 1 Hz periodic sampling (Section 6, step 3)
- Plausibility validation on every channel (Scenario item 2)
- A linear calibration hook for temperature (Scenario item 3 — coefficients
  are placeholders, `tempCalSlope = 1.0` / `tempCalOffset = 0.0`, until fitted
  against a real reference instrument — see "What's still needed" below)
- A 5-sample moving average filter for temperature (Section 7.2.1)
- Rate-of-change calculation (Section 7.2.2)
- Threshold/event detection → `status` field, matching the guide's own
  `HIGH_TEMP` / `NORMAL` example (Section 7.2.3)
- A machine-readable CSV stream over Serial, ready for the Python side
  (Section 7.3)

## Running the simulation in Wokwi

1. Go to [wokwi.com](https://wokwi.com) and sign in (free account).
2. Click **New Project → ESP32**.
3. Open the **diagram.json** tab and replace its contents with
   `firmware/sensor_node/diagram.json`.
4. Open the **sketch.ino** tab and replace its contents with
   `firmware/sensor_node/sensor_node.ino`.
5. Add the two libraries from `firmware/sensor_node/libraries.txt`: either
   create a `libraries.txt` file in the Wokwi project with that content, or
   install **"DHT sensor library"** (by Adafruit) and **"Adafruit Unified
   Sensor"** from the Library Manager (book icon, left sidebar).
6. Click the green **Play** button. Open the **Serial Monitor** to see the
   CSV stream.
7. While it's running, use the on-part controls to reproduce Section 7.1's
   "controlled change" experiments: click the DHT22 to drag its
   temperature/humidity sliders, click the photoresistor to drag its light
   slider (dark → bright), click the PIR to toggle "Simulate motion".
8. Select all the Serial Monitor output, copy it, and paste it into a text
   file (e.g. `data/raw/wokwi_serial_dump.txt`) — that's the raw capture the
   Python side parses.

## Python pipeline (`python/`)

- **`generate_sample_data.py`** — builds `data/raw/sample_serial_log.csv`, a
  650-row *synthetic* capture with the same columns the firmware streams
  (stable baseline, a light sweep, a temperature spike, PIR events, a few
  invalid/NaN rows). Kept for reference; no longer the active dataset.
- **`acquisition.ipynb`** — documents real `pyserial` capture from the ESP32
  (for once you're on real hardware), and includes `parse_wokwi_dump()`,
  which turns a Wokwi Serial Monitor text dump into a proper CSV.
- **`analysis.ipynb`** — loads a raw CSV, computes the required descriptive
  statistics (observation count & duration, mean/min/max, std, invalid
  count, detected-event count), produces 5 plots in `figures/`, and writes
  a cleaned dataset to `data/processed/cleaned_log.csv`.
- **`analysis_colab.ipynb`** — the same notebook, adapted to run in Google
  Colab (prompts you to upload the CSV instead of assuming a fixed folder
  structure).
- **`build_acquisition_nb.py` / `build_analysis_nb.py` / `build_analysis_nb_colab.py`
  / `_nb_builder.py`** — the scripts used to generate the three notebooks
  above from plain Python source. Not needed day-to-day; only re-run these
  if the notebooks themselves need to change.

**Currently running on real data.** `analysis.ipynb`'s `RAW_PATH` points at
`data/raw/wokwi_serial_log.csv`, parsed from a real Wokwi Serial Monitor run:

- 723 rows, ~12 minutes of capture (well above the 600-row / 5-minute minimum)
- 0 invalid readings
- 90 detected events (`HIGH_TEMP` + motion combined)
- Temperature ranged from -5.8°C to 60.8°C across several manual slider changes
- Light ranged from 0.025 to 0.989 (normalized)

To switch back to the synthetic dataset for comparison, change `RAW_PATH` in
`analysis.ipynb` to `../data/raw/sample_serial_log.csv` and re-run.

## What's still needed

Per the lab guide's deliverables list (Section 9.1), still outstanding:

- **Calibration (9.1g)** — `tempCalSlope`/`tempCalOffset` are placeholders.
  Needs paired (sensor, reference-instrument) readings from the real
  hardware build, then a linear fit — see `python/calibration.ipynb` once
  that data exists.
- **Real ESP32 hardware prototype (9.1b)** — everything above has run in
  Wokwi's simulator only.
- **Technical report (9.1j / Section 9.2)** — `docs/lab_report.pdf`.
- **Live demonstration** — part of the submission requirement, not a file.

The IMU (MPU6050) from the advanced challenge (8.2) isn't wired in — optional.
